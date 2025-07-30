from typing import List, Tuple, Union

import hydra
import hydra.utils
import torch
import torch.nn.functional as F
import warp as wp
from jaxtyping import Float
from omegaconf import DictConfig
from torch import Tensor, nn
from warpconvnet.geometry.base.coords import Coords
from warpconvnet.geometry.base.geometry import Geometry
from warpconvnet.geometry.coords.ops.voxel import voxel_downsample_random_indices
from warpconvnet.geometry.features.cat import CatFeatures
from warpconvnet.geometry.types.points import Points
from warpconvnet.nn.encodings import FourierEncoding
from warpconvnet.nn.modules.attention import (
    NestedAttention,
    ToAttention,
    ToSpatialFeatures,
)
from warpconvnet.nn.modules.base_module import BaseSpatialModel
from warpconvnet.nn.modules.mlp import Linear
from warpconvnet.nn.modules.normalizations import LayerNorm
from warpconvnet.nn.modules.sparse_conv import SparseConv3d
from warpconvnet.types import NestedTensor


class MaskInnerProduct(BaseSpatialModel):

    def forward(
        self, queries: Float[Tensor, "B Q C"], scene_feats: Geometry
    ) -> List[Float[Tensor, "Q N"]]:
        # BxQxC @ BxNxC = BxQxN
        return [
            queries[b] @ scene_feats.batched_features[b].T
            for b in range(scene_feats.batch_size)
        ]


class FFNLayer(nn.Module):
    def __init__(self, d_model: int, dim_feedforward: int, dropout: float):
        super().__init__()
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: Float[Tensor, "B M C"]) -> Float[Tensor, "B M C"]:
        x = x + self.linear2(self.dropout(self.activation(self.linear1(x))))
        return self.norm(x)


class TransformerDecoderBlock(nn.Module):
    def __init__(
        self,
        d_model: int,
        nhead: int,
        dim_feedforward: int,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout)
        self.cross_attn = NestedAttention(d_model, nhead)
        self.ffn = FFNLayer(d_model, dim_feedforward, dropout)

    def forward(
        self, queries: Float[NestedTensor, "Q C"], scene_feats: Geometry
    ) -> Float[Tensor, "B Q C"]:
        queries = self.self_attn(queries, queries, queries)[0]
        queries = self.cross_attn(query=queries, key=scene_feats, value=scene_feats)
        queries = self.ffn(queries)
        return queries


class MaskTransformer(BaseSpatialModel):
    """
    Transformer that attend query embeddings and queries x scene features.
    """

    def __init__(
        self,
        hidden_dim: int,
        num_queries: int,
        num_heads: int,
        num_layers: int,
        dim_feedforward: int,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.num_queries = num_queries
        self.hidden_dim = hidden_dim
        self.layers = nn.ModuleList(
            [
                TransformerDecoderBlock(
                    hidden_dim,
                    num_heads,
                    dim_feedforward,
                    dropout,
                )
                for _ in range(num_layers)
            ]
        )
        self.norm = nn.LayerNorm(hidden_dim)
        self.query_embed = nn.Embedding(num_queries, hidden_dim)

    def forward(
        self,
        scene_features: Geometry,
    ) -> Float[Tensor, "B Q C"]:
        queries = torch.zeros(
            (scene_features.batch_size, self.num_queries, self.hidden_dim),
            dtype=scene_features.dtype,
            device=scene_features.device,
        )
        for layer in self.layers:
            queries += self.query_embed.weight.unsqueeze(0)
            queries = layer(queries, scene_features)
        return self.norm(queries)


class MaskFormer(BaseSpatialModel):
    def __init__(
        self,
        backbone: BaseSpatialModel,
        hidden_dim: int,
        num_queries: int,
        num_heads: int,
        num_decoders: int,
        dim_feedforward: int,
        dropout: float,
        **kwargs,
    ):
        super().__init__()

        self.backbone = backbone

        self.mask_features_head = SparseConv3d(
            hidden_dim, hidden_dim, kernel_size=1, stride=1, bias=True
        )

        self.mask_transformer = MaskTransformer(
            hidden_dim=hidden_dim,
            num_queries=num_queries,
            num_heads=num_heads,
            num_layers=num_decoders,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
        )

        self.mask_inner_product = MaskInnerProduct()

    def forward(
        self, x: Geometry
    ) -> Tuple[Geometry, List[Float[Tensor, "Q N"]]]:
        # Implement the forward pass
        # This is a placeholder implementation and should be adapted to your needs
        scene_features = self.backbone(x)

        # Apply transformer
        queries = self.mask_transformer(scene_features)  # BxQxC

        # Find final mask based on the queries
        mask_features: Geometry = self.mask_features_head(scene_features)
        masks: List[Float[Tensor, "Q N"]] = self.mask_inner_product(
            queries, mask_features
        )

        return scene_features, masks

    def _downsampled_queries(
        self, x: Geometry, query_voxel_size: float
    ) -> Geometry:
        """
        To main tain the same density of queries as the input points,
        we downsample the input points using voxel_downsample.
        N points to M queries with lower density. M << N.
        """
        query_indices, query_offsets = voxel_downsample_random_indices(
            x.coordinate_tensor, x.offsets, query_voxel_size
        )
        query_pos = x.coordinate_tensor[query_indices]
        query_features = self.query_projection(self.pos_enc(query_pos))
        return x.replace(
            batched_coordinates=Coords(query_pos, offsets=query_offsets),
            batched_features=CatFeatures(query_features, offsets=query_offsets),
        )

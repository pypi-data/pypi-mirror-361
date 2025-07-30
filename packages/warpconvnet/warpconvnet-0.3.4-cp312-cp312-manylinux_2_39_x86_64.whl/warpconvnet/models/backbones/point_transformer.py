from typing import List, Literal, Optional, Union

import torch
import torch.nn as nn
from jaxtyping import Float, Int
from torch import Tensor
from warpconvnet.geometry.coords.search.knn import batched_knn_search
from warpconvnet.geometry.types.points import Points
from warpconvnet.models.backbones.dgcnn import DGCNNEncoder
from warpconvnet.nn.modules.activations import ReLU
from warpconvnet.nn.modules.attention import (
    Attention,
    ToAttention,
    ToSpatialFeatures,
    zero_out_points,
)
from warpconvnet.nn.modules.mlp import Linear
from warpconvnet.nn.modules.point_pool import PointPoolBase, PointUnpool
from warpconvnet.ops.reductions import REDUCTIONS


class TransformerBlock(nn.Module):
    """
    Transformer Block defined in https://github.com/Julie-tang00/Point-BERT/blob/master/models/Point_BERT.py
    """

    def __init__(self, embed_dim: int = 768, num_heads: int = 12, mlp_ratio: float = 4.0):
        super().__init__()
        self.attn = Attention(
            dim=embed_dim,
            num_heads=num_heads,
        )

        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, int(embed_dim * mlp_ratio)),
            nn.GELU(),
            nn.Linear(int(embed_dim * mlp_ratio), embed_dim),
        )

    def forward(self, x: Float[Tensor, "B N C"], pos_enc: Optional[Float[Tensor, "B N C"]] = None):
        x = x + self.attn(self.norm1(x), pos_enc)
        x = x + self.mlp(self.norm2(x))
        return x


class Transformer(nn.Module):
    """Transformer Encoder without hierarchical structure"""

    def __init__(
        self,
        embed_dim: int = 768,
        depth: int = 4,
        num_heads: int = 12,
        mlp_ratio: float = 4.0,
    ):
        super().__init__()

        self.blocks = nn.Sequential(
            *[
                TransformerBlock(
                    embed_dim=embed_dim,
                    num_heads=num_heads,
                    mlp_ratio=mlp_ratio,
                )
                for _ in range(depth)
            ]
        )

    def forward(
        self,
        x: Float[Tensor, "B N C"],
    ):
        return self.blocks(x)


class PointTransformer(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        encoder_knn_ks: Union[List[int], int] = 16,
        encoder_emb_dims: int = 1024,
        num_groups: int = 512,
        pool_reduction: Union[str, REDUCTIONS] = REDUCTIONS.MAX,
        num_heads: int = 4,
        mlp_ratio: float = 2.0,
        transformer_depth: int = 3,
        encoding_range: float = 4,
        encoding_num_channels: int = 32,
        encoding_concat_input: bool = True,
        out_type: Literal["classification", "segmentation"] = "classification",
    ):
        super().__init__()
        assert out_type in ["classification", "segmentation"]
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_groups = num_groups
        self.out_type = out_type
        self.encoder = DGCNNEncoder(
            in_channels, knn_ks=encoder_knn_ks, emb_dims=encoder_emb_dims, negative_slope=0.2
        )
        self.group_pool = PointPoolBase(
            reduction=pool_reduction,
            downsample_max_num_points=num_groups,
            return_type="point",
            return_neighbor_search_result=True,
        )
        self.to_attention = ToAttention(
            out_channels=encoder_emb_dims,
            num_encoding_channels=encoding_num_channels,
            encoding_range=encoding_range,
            concat_input=encoding_concat_input,
        )
        self.transformer = Transformer(
            embed_dim=encoder_emb_dims,
            depth=transformer_depth,
            num_heads=num_heads,
            mlp_ratio=mlp_ratio,
        )

        if out_type == "classification":
            # classification head
            self.head = nn.Sequential(
                nn.Linear(encoder_emb_dims, encoder_emb_dims),
                nn.ReLU(),
                nn.Linear(encoder_emb_dims, out_channels),
            )
        elif out_type == "segmentation":
            # segmentation head
            self.to_spatial = ToSpatialFeatures()
            self.unpool = PointUnpool(concat_unpooled_pc=True)
            self.head = nn.Sequential(
                Linear(2 * encoder_emb_dims, encoder_emb_dims),
                ReLU(),
                Linear(encoder_emb_dims, out_channels),
            )

    def forward(self, x: Points) -> Union[Float[Tensor, "B C"], Points]:
        enc_out = self.encoder(x)
        pooled_out, group_neighbors = self.group_pool(enc_out)
        features, pos_enc, mask, num_points = self.to_attention(pooled_out)
        features += pos_enc
        x = self.transformer(features)
        if self.out_type == "classification":
            # pool BxNxC -> BxC
            x = zero_out_points(x, num_points)
            x = x.max(dim=1)[0]
            x = self.head(x)
        elif self.out_type == "segmentation":
            # unpool BxC -> BxNxC
            x = self.to_spatial(x, pooled_out)
            x = self.unpool(x, enc_out)
            x = self.head(x)
        return x

from typing import List, Optional, Tuple

import torch.nn as nn
from warpconvnet.geometry.coords.search.search_configs import RealSearchConfig
from warpconvnet.geometry.types.points import Points
from warpconvnet.models.backbones.components.point_conv_block import (
    PointConvDecoder,
    PointConvEncoder,
    PointConvUNetBlock,
)
from warpconvnet.nn.functional.point_pool import point_pool
from warpconvnet.nn.functional.point_unpool import point_unpool
from warpconvnet.nn.modules.base_module import BaseSpatialModel
from warpconvnet.nn.modules.mlp import Linear
from warpconvnet.ops.reductions import REDUCTION_TYPES_STR, REDUCTIONS

__all__ = ["PointConvUNet", "PointConvEncoderDecoder"]


class PointConvUNet(BaseSpatialModel):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        down_channels: List[int],
        up_channels: List[int],
        neighbor_search_args: RealSearchConfig,
        neighbor_search_radii: List[float],
        downsample_voxel_sizes: List[float],
        pooling_reduction: REDUCTIONS = REDUCTIONS.MEAN,
        initial_pool_reduction: REDUCTIONS = REDUCTIONS.MEAN,
        initial_downsample_voxel_size: Optional[float] = None,
        edge_transform_mlp: Optional[nn.Module] = None,
        out_transform_mlp: Optional[nn.Module] = None,
        intermediate_dim: Optional[int] = None,
        hidden_dim: Optional[int] = None,
        channel_multiplier: int = 2,
        use_rel_pos: bool = True,
        use_rel_pos_encode: bool = False,
        pos_encode_dim: int = 32,
        pos_encode_range: float = 4,
        reductions: List[REDUCTION_TYPES_STR] = ("mean",),
        num_levels: int = 4,
    ):
        super().__init__()
        assert len(down_channels) == num_levels + 1 and len(up_channels) == num_levels + 1
        assert len(downsample_voxel_sizes) == num_levels
        assert len(neighbor_search_radii) == num_levels
        for i in range(num_levels - 1):
            assert downsample_voxel_sizes[i] < downsample_voxel_sizes[i + 1]
            assert neighbor_search_radii[i] < neighbor_search_radii[i + 1]

        self.num_levels = num_levels
        self.in_map = Linear(in_channels, down_channels[0])

        # Create from the deepest level to the shallowest level
        inner_block = None
        # start from the innermost block. This has the largest receptive field, radius, and voxel size
        for i in range(num_levels - 1, -1, -1):
            curr_neighbor_search_args: RealSearchConfig = neighbor_search_args.replace(
                radius=neighbor_search_radii[i]
            )
            inner_block = PointConvUNetBlock(
                inner_module=inner_block,
                in_channels=down_channels[i],
                inner_module_in_channels=down_channels[i + 1],
                inner_module_out_channels=up_channels[i + 1],
                out_channels=up_channels[i],
                neighbor_search_args=curr_neighbor_search_args,
                pooling_reduction=pooling_reduction,
                pooling_voxel_size=downsample_voxel_sizes[i],
                edge_transform_mlp=edge_transform_mlp,
                out_transform_mlp=out_transform_mlp,
                intermediate_dim=intermediate_dim,
                hidden_dim=hidden_dim,
                channel_multiplier=channel_multiplier,
                use_rel_pos=use_rel_pos,
                use_rel_pos_encode=use_rel_pos_encode,
                pos_encode_dim=pos_encode_dim,
                pos_encode_range=pos_encode_range,
                reductions=reductions,
            )
        self.unet = inner_block
        if initial_downsample_voxel_size is None:
            initial_downsample_voxel_size = downsample_voxel_sizes[0] / 2
        self.initial_pooling_args = {
            "reduction": initial_pool_reduction,
            "voxel_size": initial_downsample_voxel_size,
        }
        self.out_map = Linear(up_channels[0] + in_channels, out_channels)

    def forward(self, in_pc: Points) -> Tuple[Points, List[Points]]:
        """
        Given an input point collection, the network will return a list of point collections at each level of the UNet.
        """

        # downsample
        pooled_pc, to_unique = point_pool(
            in_pc,
            reduction=self.initial_pooling_args["reduction"],
            downsample_voxel_size=self.initial_pooling_args["voxel_size"],
            return_type="point",
            return_to_unique=True,
        )
        out = self.in_map(pooled_pc)

        # forward pass through the UNet
        out = self.unet(out)

        unpooled_pc = point_unpool(
            pooled_pc=out[0],
            unpooled_pc=in_pc,
            concat_unpooled_pc=True,
            to_unique=to_unique,
        )
        unpooled_pc = self.out_map(unpooled_pc)
        return unpooled_pc, *out


class PointConvEncoderDecoder(BaseSpatialModel):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        encoder_channels: List[int],
        decoder_channels: List[int],
        num_encoder_blocks_per_level: List[int],
        num_decoder_blocks_per_level: List[int],
        neighbor_search_args: RealSearchConfig,
        neighbor_search_radii: List[float],
        downsample_voxel_sizes: List[float],
        pooling_reduction: REDUCTIONS = REDUCTIONS.MEAN,
        initial_pool_reduction: REDUCTIONS = REDUCTIONS.MEAN,
        initial_downsample_voxel_size: Optional[float] = None,
        channel_multiplier: int = 2,
        use_rel_pos: bool = True,
        use_rel_pos_encode: bool = False,
        pos_encode_dim: int = 32,
        pos_encode_range: float = 4,
        reductions: List[REDUCTION_TYPES_STR] = ("mean",),
        num_levels_enc: int = 4,
        num_levels_dec: int = 4,
    ):
        super().__init__()
        assert len(encoder_channels) == num_levels_enc + 1
        assert len(decoder_channels) == num_levels_dec + 1
        assert len(num_encoder_blocks_per_level) == num_levels_enc
        assert len(num_decoder_blocks_per_level) == num_levels_dec
        assert len(downsample_voxel_sizes) == num_levels_enc
        assert len(neighbor_search_radii) == num_levels_enc
        for i in range(num_levels_enc - 1):
            assert downsample_voxel_sizes[i] < downsample_voxel_sizes[i + 1]
            assert neighbor_search_radii[i] < neighbor_search_radii[i + 1]

        self.num_levels_enc = num_levels_enc
        self.num_levels_dec = num_levels_dec
        self.in_map = Linear(in_channels, encoder_channels[0])

        self.encoder = PointConvEncoder(
            encoder_channels=encoder_channels,
            num_blocks_per_level=num_encoder_blocks_per_level,
            neighbor_search_args=neighbor_search_args,
            neighbor_search_radii=neighbor_search_radii,
            pooling_reduction=pooling_reduction,
            pooling_voxel_sizes=downsample_voxel_sizes,
            channel_multiplier=channel_multiplier,
            use_rel_pos=use_rel_pos,
            use_rel_pos_encode=use_rel_pos_encode,
            pos_encode_dim=pos_encode_dim,
            pos_encode_range=pos_encode_range,
            reductions=reductions,
            num_levels=num_levels_enc,
        )

        self.decoder = PointConvDecoder(
            decoder_channels=decoder_channels,
            encoder_channels=encoder_channels,
            num_blocks_per_level=num_decoder_blocks_per_level,
            neighbor_search_args=neighbor_search_args,
            neighbor_search_radii=neighbor_search_radii[::-1][:num_levels_dec],
            channel_multiplier=channel_multiplier,
            use_rel_pos=use_rel_pos,
            use_rel_pos_encode=use_rel_pos_encode,
            pos_encode_dim=pos_encode_dim,
            pos_encode_range=pos_encode_range,
            reductions=reductions,
            num_levels=num_levels_dec,
        )

        if initial_downsample_voxel_size is None:
            initial_downsample_voxel_size = downsample_voxel_sizes[0] / 2
        self.initial_pooling_args = {
            "reduction": initial_pool_reduction,
            "voxel_size": initial_downsample_voxel_size,
        }

        if decoder_channels[-1] != out_channels:
            self.out_map = Linear(decoder_channels[-1], out_channels)
        else:
            self.out_map = nn.Identity()

    def forward(
        self, in_pc: Points
    ) -> Tuple[Points, List[Points], List[Points]]:
        """
        Given an input point collection, the network will return a list of point
        collections at each level of the encoder and decoder

        Returns:
            out_pc: The final output point collection
            decoder_outs: A list of point collections at each level of the
                decoder. From the deepest level (low res) to the shallowest
                level (high res)

            encoder_outs: A list of point collections at each level of the
                encoder. From the shallowest level (high res) to the deepest
                level (low res)
        """
        # Downsample
        pooled_pc, to_unique = point_pool(
            in_pc,
            reduction=self.initial_pooling_args["reduction"],
            downsample_voxel_size=self.initial_pooling_args["voxel_size"],
            return_type="point",
            return_to_unique=True,
        )
        out = self.in_map(pooled_pc)

        # Forward pass through the encoder
        encoder_outs = self.encoder(out)

        # Forward pass through the decoder
        decoder_outs = self.decoder(encoder_outs[-1], encoder_outs)

        # Map to out_channels
        out_pc = self.out_map(decoder_outs[-1])

        return out_pc, decoder_outs, encoder_outs

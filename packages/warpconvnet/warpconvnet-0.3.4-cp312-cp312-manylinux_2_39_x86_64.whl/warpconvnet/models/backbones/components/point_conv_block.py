from typing import List, Literal, Optional

import torch.nn as nn
from warpconvnet.geometry.coords.search.search_configs import (
    RealSearchConfig,
    RealSearchMode,
)
from warpconvnet.geometry.types.points import Points
from warpconvnet.nn.modules.activations import ReLU
from warpconvnet.nn.modules.base_module import BaseSpatialModule
from warpconvnet.nn.modules.mlp import Linear
from warpconvnet.nn.modules.normalizations import LayerNorm
from warpconvnet.nn.modules.point_conv import PointConv
from warpconvnet.nn.modules.sequential import Sequential
from warpconvnet.ops.reductions import REDUCTION_TYPES_STR, row_reduction


class PointConvBlock(BaseSpatialModule):
    """
    A conv block that consists of two consecutive PointConv, activation, and normalization and a skip connection
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        neighbor_search_args: RealSearchConfig,
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
        out_point_feature_type: Literal["provided", "downsample", "same"] = "same",
        provided_in_channels: Optional[int] = None,
        norm_layer1: Optional[nn.Module] = None,
        norm_layer2: Optional[nn.Module] = None,
        activation: Optional[nn.Module] = None,
    ):
        super().__init__()
        assert out_point_feature_type == "same", "Only same type is supported for now"
        if intermediate_dim is None:
            intermediate_dim = out_channels
        self.conv1 = Sequential(
            PointConv(
                in_channels=in_channels,
                out_channels=intermediate_dim,
                neighbor_search_args=neighbor_search_args,
                edge_transform_mlp=edge_transform_mlp,
                out_transform_mlp=out_transform_mlp,
                hidden_dim=hidden_dim,
                channel_multiplier=channel_multiplier,
                use_rel_pos=use_rel_pos,
                use_rel_pos_encode=use_rel_pos_encode,
                pos_encode_dim=pos_encode_dim,
                pos_encode_range=pos_encode_range,
                reductions=reductions,
                out_point_type="same",
                provided_in_channels=provided_in_channels,
            ),
            nn.LayerNorm(intermediate_dim) if norm_layer1 is None else norm_layer1,
            nn.ReLU(inplace=True) if activation is None else activation,
        )
        self.conv2 = Sequential(
            PointConv(
                in_channels=intermediate_dim,
                out_channels=out_channels,
                neighbor_search_args=neighbor_search_args,
                edge_transform_mlp=edge_transform_mlp,
                out_transform_mlp=out_transform_mlp,
                hidden_dim=hidden_dim,
                channel_multiplier=channel_multiplier,
                use_rel_pos=use_rel_pos,
                use_rel_pos_encode=use_rel_pos_encode,
                pos_encode_dim=pos_encode_dim,
                pos_encode_range=pos_encode_range,
                reductions=reductions,
                out_point_type="same",
                provided_in_channels=provided_in_channels,
            ),
            nn.LayerNorm(out_channels) if norm_layer2 is None else norm_layer2,
        )

        if activation is None:
            activation = ReLU()

        self.relu = activation

    def forward(self, in_pc: Points) -> Points:
        out1 = self.conv1(in_pc)
        out2 = self.conv2(out1)
        # Skip connection
        out2 = out2 + out1
        out2 = self.relu(out2)
        return Points(
            batched_coordinates=out2.batched_coordinates,
            batched_features=out2.batched_features,
            **out2.extra_attributes,
        )


class PointConvEncoder(BaseSpatialModule):
    """
    Generate a list of output point collections from each level of the encoder
    given an input point collection.
    """

    def __init__(
        self,
        encoder_channels: List[int],
        num_blocks_per_level: List[int] | int,
        neighbor_search_args: RealSearchConfig,
        neighbor_search_radii: List[float],
        pooling_reduction: REDUCTION_TYPES_STR,
        pooling_voxel_sizes: List[float],
        channel_multiplier: int = 2,
        use_rel_pos: bool = True,
        use_rel_pos_encode: bool = False,
        pos_encode_dim: int = 32,
        pos_encode_range: float = 4,
        reductions: List[REDUCTION_TYPES_STR] = ("mean",),
        num_levels: int = 4,
    ):
        super().__init__()
        self.num_levels = num_levels
        if isinstance(num_blocks_per_level, int):
            num_blocks_per_level = [num_blocks_per_level] * num_levels
        assert len(encoder_channels) == num_levels + 1
        assert len(num_blocks_per_level) == self.num_levels
        assert len(pooling_voxel_sizes) == self.num_levels
        assert len(neighbor_search_radii) == self.num_levels
        for level in range(self.num_levels - 1):
            assert pooling_voxel_sizes[level] < pooling_voxel_sizes[level + 1]
            assert neighbor_search_radii[level] < neighbor_search_radii[level + 1]
            # print warning if search radius is not \sqrt(3) times the downsample voxel size
            if neighbor_search_args.mode == RealSearchMode.RADIUS:
                assert neighbor_search_radii[level] > pooling_voxel_sizes[level] * (
                    3**0.5
                ), f"neighbor search radius {neighbor_search_radii[level]} is less than sqrt(3) times the downsample voxel size {pooling_voxel_sizes[level]} at level {level}"

        self.down_blocks = nn.ModuleList()

        for level in range(self.num_levels):
            in_channels = encoder_channels[level]
            out_channels = encoder_channels[level + 1]
            down_neighbor_search_args: RealSearchConfig = neighbor_search_args.replace(
                radius=2 * pooling_voxel_sizes[level]
            )
            # First block out_point_feature_type is downsample, rest are conv blocks are "same"
            down_block = [
                PointConv(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    neighbor_search_args=down_neighbor_search_args,
                    pooling_reduction=pooling_reduction,
                    pooling_voxel_size=pooling_voxel_sizes[level],
                    use_rel_pos=use_rel_pos,
                    use_rel_pos_encode=use_rel_pos_encode,
                    pos_encode_dim=pos_encode_dim,
                    pos_encode_range=pos_encode_range,
                    reductions=reductions,
                    out_point_type="downsample",
                )
            ]

            curr_neighbor_search_args: RealSearchConfig = neighbor_search_args.replace(
                radius=neighbor_search_radii[level]
            )
            for _ in range(num_blocks_per_level[level]):
                down_block.append(
                    PointConvBlock(
                        in_channels=out_channels,
                        out_channels=out_channels,
                        neighbor_search_args=curr_neighbor_search_args,
                        channel_multiplier=channel_multiplier,
                        use_rel_pos=use_rel_pos,
                        use_rel_pos_encode=use_rel_pos_encode,
                        pos_encode_dim=pos_encode_dim,
                        pos_encode_range=pos_encode_range,
                        reductions=reductions,
                        out_point_feature_type="same",
                    )
                )

            self.down_blocks.append(nn.Sequential(*down_block))

    def forward(self, in_point_features: Points) -> List[Points]:
        out_point_features = []
        for down_block in self.down_blocks:
            out_point_features.append(in_point_features)
            in_point_features = down_block(in_point_features)
        out_point_features.append(in_point_features)
        return out_point_features


class PointConvDecoder(BaseSpatialModule):
    def __init__(
        self,
        decoder_channels: List[int],  # descending
        encoder_channels: List[int],  # ascending
        num_blocks_per_level: List[int],
        neighbor_search_args: RealSearchConfig,
        neighbor_search_radii: List[float],  # descending
        channel_multiplier: int = 2,
        use_rel_pos: bool = True,
        use_rel_pos_encode: bool = False,
        pos_encode_dim: int = 32,
        pos_encode_range: float = 4,
        reductions: List[REDUCTION_TYPES_STR] = ("mean",),
        num_levels: int = 4,
    ):
        super().__init__()
        self.num_levels = num_levels
        assert len(decoder_channels) == num_levels + 1
        assert len(num_blocks_per_level) == self.num_levels
        # The encoder_channels are in ascending order
        assert len(encoder_channels) >= num_levels + 1
        assert len(neighbor_search_radii) >= self.num_levels
        for level in range(self.num_levels - 1):
            assert (
                neighbor_search_radii[level] > neighbor_search_radii[level + 1]
            ), f"neighbor search radius must be in descending order, got {neighbor_search_radii}"
        assert (
            encoder_channels[-1] == decoder_channels[0]
        ), f"Last encoder channel must match first decoder channel, got last encoder channel {encoder_channels[-1]} != first decoder channel {decoder_channels[0]}"

        self.up_convs = nn.ModuleList()
        self.skips = nn.ModuleList()
        self.up_blocks = nn.ModuleList()

        for level in range(self.num_levels):
            in_channels = decoder_channels[level]
            out_channels = decoder_channels[level + 1]
            enc_channels = encoder_channels[-(level + 2)]
            curr_neighbor_search_args: RealSearchConfig = neighbor_search_args.replace(
                radius=neighbor_search_radii[level]
            )
            # Up-sampling convolution
            self.up_convs.append(
                PointConv(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    neighbor_search_args=curr_neighbor_search_args,
                    use_rel_pos=use_rel_pos,
                    use_rel_pos_encode=use_rel_pos_encode,
                    pos_encode_dim=pos_encode_dim,
                    pos_encode_range=pos_encode_range,
                    reductions=reductions,
                    out_point_type="provided",
                    provided_in_channels=enc_channels,
                )
            )

            # Skip connection
            if enc_channels != out_channels:
                self.skips.append(
                    Linear(
                        in_features=enc_channels,
                        out_features=out_channels,
                        bias=True,
                    )
                )
            else:
                self.skips.append(nn.Identity())

            # Additional up-convolution blocks
            up_block = []
            for _ in range(num_blocks_per_level[level]):
                up_block.append(
                    PointConvBlock(
                        in_channels=out_channels,
                        out_channels=out_channels,
                        neighbor_search_args=curr_neighbor_search_args,
                        channel_multiplier=channel_multiplier,
                        use_rel_pos=use_rel_pos,
                        use_rel_pos_encode=use_rel_pos_encode,
                        pos_encode_dim=pos_encode_dim,
                        pos_encode_range=pos_encode_range,
                        reductions=reductions,
                        out_point_feature_type="same",
                    )
                )
            self.up_blocks.append(nn.Sequential(*up_block))

    def forward(
        self, in_point_features: Points, encoder_outs: List[Points]
    ) -> List[Points]:
        out_pcs = []
        out_point_features = in_point_features
        for i, (up_conv, skip, up_block) in enumerate(
            zip(self.up_convs, self.skips, self.up_blocks)
        ):
            out_point_features = up_conv(out_point_features, encoder_outs[-(i + 2)])
            out_point_features = out_point_features + skip(encoder_outs[-(i + 2)])
            out_point_features = up_block(out_point_features)
            out_pcs.append(out_point_features)
        return out_pcs


class PointConvUNetBlock(BaseSpatialModule):
    """
    Given an input module, the UNet block will return a list of point collections at each level of the UNet from the inner module.

    +------------+   +------------+   +-------------+   +------------+   +-----------+   +----------------+
    | Down Blocks| ->| Down Conv  | ->| Inner Module| ->| Up Conv    | ->| Up Blocks | ->| Skip Connection|
    +------------+   +------------+   +-------------+   +------------+   +-----------+   +----------------+
    """

    def __init__(
        self,
        in_channels: int,
        inner_module_in_channels: int,
        inner_module_out_channels: int,
        out_channels: int,
        neighbor_search_args: RealSearchConfig,
        pooling_reduction: REDUCTION_TYPES_STR,
        pooling_voxel_size: float,
        inner_module: BaseSpatialModule = None,
        num_down_blocks: int = 1,
        num_up_blocks: int = 0,
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
    ):
        assert inner_module is None or isinstance(inner_module, PointConvUNetBlock)

        super().__init__()
        down_conv_block = [
            PointConvBlock(
                in_channels=in_channels,
                out_channels=in_channels,
                neighbor_search_args=neighbor_search_args,
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
                out_point_feature_type="same",
            )
        ]

        for _ in range(num_down_blocks):
            down_conv_block.append(
                PointConvBlock(
                    in_channels=in_channels,
                    out_channels=in_channels,
                    neighbor_search_args=neighbor_search_args,
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
                    out_point_feature_type="same",
                )
            )

        self.down_conv_block = nn.Sequential(*down_conv_block)

        self.down_conv = PointConv(
            in_channels=in_channels,
            out_channels=inner_module_in_channels,
            neighbor_search_args=neighbor_search_args,
            pooling_reduction=pooling_reduction,
            pooling_voxel_size=pooling_voxel_size,
            edge_transform_mlp=edge_transform_mlp,
            out_transform_mlp=out_transform_mlp,
            hidden_dim=hidden_dim,
            channel_multiplier=channel_multiplier,
            use_rel_pos=use_rel_pos,
            use_rel_pos_encode=use_rel_pos_encode,
            pos_encode_dim=pos_encode_dim,
            pos_encode_range=pos_encode_range,
            reductions=reductions,
            out_point_type="downsample",
        )

        self.inner_module = inner_module

        self.up_conv = PointConv(
            in_channels=inner_module_out_channels,
            out_channels=out_channels,
            neighbor_search_args=neighbor_search_args,
            edge_transform_mlp=edge_transform_mlp,
            out_transform_mlp=out_transform_mlp,
            hidden_dim=hidden_dim,
            channel_multiplier=channel_multiplier,
            use_rel_pos=use_rel_pos,
            use_rel_pos_encode=use_rel_pos_encode,
            pos_encode_dim=pos_encode_dim,
            pos_encode_range=pos_encode_range,
            reductions=reductions,
            out_point_type="provided",
            provided_in_channels=in_channels,
        )

        if num_up_blocks > 0:
            self.up_conv_block = nn.Sequential(
                *[
                    PointConvBlock(
                        in_channels=out_channels,
                        out_channels=out_channels,
                        neighbor_search_args=neighbor_search_args,
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
                        out_point_feature_type="same",
                    )
                    for _ in range(num_up_blocks)
                ]
            )
        else:
            self.up_conv_block = nn.Identity()

        if in_channels != out_channels:
            self.skip = Linear(
                in_features=in_channels,
                out_channels=out_channels,
                bias=True,
            )
        else:
            self.skip = nn.Identity()

    def forward(self, point_collection: Points) -> List[Points]:
        """
        Given an input point collection, the network will return a list of point collections at each level of the UNet.
        """
        out_down = self.down_conv_block(point_collection)
        out_down = self.down_conv(out_down)
        if self.inner_module is None:
            out_inner: List[Points] = [out_down]
        else:
            out_inner: List[Points] = self.inner_module(out_down)
        out_up = self.up_conv(out_inner[0], point_collection)
        out_up = out_up + self.skip(point_collection)
        out_up = self.up_conv_block(out_up)
        return [out_up] + out_inner

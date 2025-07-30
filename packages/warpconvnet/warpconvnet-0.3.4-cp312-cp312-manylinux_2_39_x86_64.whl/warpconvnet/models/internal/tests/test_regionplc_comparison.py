# Compare the output of the regionplc with spconv regionplc

import functools
import unittest

import spconv.pytorch as spconv
import torch
import torch.nn as nn
import warp as wp
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.models.internal.backbones.regionplc import (
    ResidualBlock as ResidualBlock_wp,
)
from warpconvnet.models.internal.backbones.regionplc import (
    SparseConvUNet as SparseConvUNet_wp,
)
from warpconvnet.models.internal.backbones.regionplc_spconv import (
    ResidualBlock as ResidualBlock_sp,
)
from warpconvnet.models.internal.backbones.regionplc_spconv import (
    SparseConvUNet as SparseConvUNet_sp,
)

NUM_CONV_WEIGHTS = 0


def sp2wp_weight(weight_sp):
    global NUM_CONV_WEIGHTS
    NUM_CONV_WEIGHTS += 1
    return weight_sp.permute(1, 2, 3, 4, 0).flatten(0, 2)


def match_conv_weights(conv_sp, conv_wp):
    # assert the shape of conv_wp.weight is (3^3, C_in, C_out) matches the shape of conv_sp.weight
    conv_weight_wp = sp2wp_weight(conv_sp.weight.data)
    assert (
        conv_weight_wp.shape == conv_wp.weight.shape
    ), f"conv_wp.weight.shape: {conv_wp.weight.shape}, conv_weight_wp.shape: {conv_weight_wp.shape}"
    conv_wp.weight.data = conv_weight_wp


def match_bn_weights(bn_sp, bn_wp):
    bn_wp.norm.weight.data = bn_sp.weight.data
    bn_wp.norm.bias.data = bn_sp.bias.data
    bn_wp.norm.running_mean.data = bn_sp.running_mean.data
    bn_wp.norm.running_var.data = bn_sp.running_var.data


def match_weights(conv_sp, conv_wp):
    # 1. Input convolution
    match_conv_weights(conv_sp.input_conv[0], conv_wp.input_conv)

    # 2. UBlock layers
    match_ublock_weights(conv_sp.unet, conv_wp.unet)

    # 3. Output layer
    match_bn_weights(conv_sp.output_layer[0], conv_wp.output_layer[0])


def match_ublock_weights(ublock_sp, ublock_wp):
    # Match weights for the main blocks
    for i, (block_sp, block_wp) in enumerate(zip(ublock_sp.blocks, ublock_wp.blocks)):
        match_residual_block_weights(block_sp, block_wp)

    # Match weights for the conv layer
    if hasattr(ublock_sp, "conv") and hasattr(ublock_wp, "conv"):
        match_bn_weights(ublock_sp.conv[0], ublock_wp.conv[0])
        match_conv_weights(ublock_sp.conv[2], ublock_wp.conv[2])

    # Recursively match weights for nested UBlocks
    if hasattr(ublock_sp, "u") and hasattr(ublock_wp, "u"):
        match_ublock_weights(ublock_sp.u, ublock_wp.u)

    # Match weights for the deconv layer
    if hasattr(ublock_sp, "deconv") and hasattr(ublock_wp, "deconv"):
        match_bn_weights(ublock_sp.deconv[0], ublock_wp.deconv_pre[0])
        match_conv_weights(ublock_sp.deconv[2], ublock_wp.deconv)

    # Match weights for the blocks_tail
    if hasattr(ublock_sp, "blocks_tail") and hasattr(ublock_wp, "blocks_tail"):
        for block_sp, block_wp in zip(ublock_sp.blocks_tail, ublock_wp.blocks_tail):
            match_residual_block_weights(block_sp, block_wp)


def match_residual_block_weights(block_sp, block_wp):
    # Match i_branch weights if it's not an Identity
    if not isinstance(block_sp.i_branch[0], nn.Identity):
        match_conv_weights(block_sp.i_branch[0], block_wp.i_branch)

    # Match conv_branch weights
    # 1 and 4 are ReLU
    match_bn_weights(block_sp.conv_branch[0], block_wp.conv_branch[0])
    match_conv_weights(block_sp.conv_branch[2], block_wp.conv_branch[2])
    match_bn_weights(block_sp.conv_branch[3], block_wp.conv_branch[3])
    match_conv_weights(block_sp.conv_branch[5], block_wp.conv_branch[5])


class TestRegionPLC(unittest.TestCase):
    def setUp(self):
        wp.init()
        # Set random seed
        torch.manual_seed(0)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        self.B, min_N, max_N, self.C = 3, 100000, 1000000, 16
        self.Ns = torch.randint(min_N, max_N, (self.B,))
        self.voxel_size = 0.01
        self.coords = [(torch.rand((N, 3)) / self.voxel_size).int() for N in self.Ns]
        self.features = [torch.rand((N, self.C)) for N in self.Ns]
        self.st = Voxels(self.coords, self.features, device=device).unique()
        return super().setUp()

    def test_spconv_regionplc(self):
        num_blocks = 2
        block_reps = 1
        conv_sp = SparseConvUNet_sp(
            in_channel=self.C,
            mid_channel=16,
            block_reps=block_reps,
            block_residual=True,
            num_blocks=num_blocks,  # num blocks is the depth
        ).to(self.device)
        conv_wp = SparseConvUNet_wp(
            in_channel=self.C,
            in_channels=[16 * (i + 1) for i in range(num_blocks)],
            out_channels=[16 * (i + 1) for i in range(num_blocks)],
            num_blocks=block_reps,  # num blocks is the reps in each depth
            return_intermediate=True,
        ).to(self.device)

        st = self.st.to(self.device)
        spconv_st = spconv.SparseConvTensor(
            features=st.feature_tensor.float().clone().requires_grad_(),
            indices=st.batch_indexed_coordinates.int(),
            spatial_shape=st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )

        # Call this function to match the weights
        match_weights(conv_sp, conv_wp)
        print("NUM_CONV_WEIGHTS: ", NUM_CONV_WEIGHTS)

        outs_wp = conv_wp(st)
        outs_sp = conv_sp(spconv_st)

        diff = (outs_wp[0].features - outs_sp[0].features).abs()
        print("diff max: ", diff.max())
        print("diff mean: ", diff.mean())

    def test_residual_block(self):
        st = self.st.to(self.device)
        spconv_st = spconv.SparseConvTensor(
            features=st.feature_tensor.float().clone().requires_grad_(),
            indices=st.batch_indexed_coordinates.int(),
            spatial_shape=st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )

        norm_fn = functools.partial(nn.BatchNorm1d, eps=1e-4, momentum=0.1)
        res_sp = ResidualBlock_sp(in_channels=16, out_channels=16, norm_fn=norm_fn).to(self.device)
        res_wp = ResidualBlock_wp(in_channels=16, out_channels=16, norm_fn=norm_fn).to(self.device)

        match_conv_weights(res_sp.conv_branch[2], res_wp.conv_branch[2])
        match_conv_weights(res_sp.conv_branch[5], res_wp.conv_branch[5])

        # Compare the output of the two residual blocks
        out_sp = res_sp(spconv_st)
        out_wp = res_wp(st)
        diff = (out_sp.features - out_wp.features).abs()
        print("diff max: ", diff.max())
        print("diff mean: ", diff.mean())

    def test_residual_block_with_different_channels(self):
        st = self.st.to(self.device)
        spconv_st = spconv.SparseConvTensor(
            features=st.feature_tensor.float().clone().requires_grad_(),
            indices=st.batch_indexed_coordinates.int(),
            spatial_shape=st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )
        norm_fn = functools.partial(nn.BatchNorm1d, eps=1e-4, momentum=0.1)
        res_sp = ResidualBlock_sp(in_channels=16, out_channels=32, norm_fn=norm_fn).to(self.device)
        res_wp = ResidualBlock_wp(in_channels=16, out_channels=32, norm_fn=norm_fn).to(self.device)

        match_conv_weights(res_sp.i_branch[0], res_wp.i_branch)
        match_conv_weights(res_sp.conv_branch[2], res_wp.conv_branch[2])
        match_conv_weights(res_sp.conv_branch[5], res_wp.conv_branch[5])

        out_sp = res_sp(spconv_st)
        out_wp = res_wp(st)
        diff = (out_sp.features - out_wp.features).abs()
        print("diff max: ", diff.max())
        print("diff mean: ", diff.mean())


if __name__ == "__main__":
    unittest.main()

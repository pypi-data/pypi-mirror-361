import unittest
from typing import List, Literal

import torch
import torch.nn as nn
import warp as wp

try:
    import spconv.pytorch as spconv
except ImportError:
    pass

from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.modules.normalizations import InstanceNorm
from warpconvnet.nn.modules.sparse_conv import SparseConv3d
from warpconvnet.utils.unique import unique_inverse


def sp2wp_weights(weight: torch.Tensor):
    # sp weight shape is (out_C, 3, 3, 3, in_C)
    # wp weight shape is (3^3, in_C, out_C)
    return weight.clone().permute(1, 2, 3, 4, 0).flatten(0, 2).contiguous()


class TwoLevelUNetSPConv(nn.Module):
    def __init__(self, channels: List[int]):
        super().__init__()
        self.conv_up1 = spconv.SparseConv3d(
            channels[0], channels[1], kernel_size=2, stride=2, bias=False, indice_key="up_1"
        )
        self.conv_up1_norm = spconv.SparseSequential(nn.InstanceNorm1d(channels[1]))
        self.conv_up2 = spconv.SparseConv3d(
            channels[1], channels[2], kernel_size=2, stride=2, bias=False, indice_key="up_2"
        )
        self.conv_up2_norm = spconv.SparseSequential(nn.InstanceNorm1d(channels[2]))
        # downsample
        self.conv_down2 = spconv.SparseInverseConv3d(
            channels[2], channels[1], kernel_size=2, bias=False, indice_key="up_2"
        )
        self.conv_down2_norm = spconv.SparseSequential(nn.InstanceNorm1d(channels[1]))
        self.conv_down1 = spconv.SparseInverseConv3d(
            channels[1], channels[0], kernel_size=2, bias=False, indice_key="up_1"
        )
        self.conv_down1_norm = spconv.SparseSequential(nn.InstanceNorm1d(channels[0]))

    def forward(self, x: spconv.SparseConvTensor):
        x_up1 = self.conv_up1(x)
        # x_up1 = self.conv_up1_norm(x_up1)
        x_up2 = self.conv_up2(x_up1)
        # x_up2 = self.conv_up2_norm(x_up2)
        x_down1 = self.conv_down2(x_up2)
        # x_down1 = self.conv_down2_norm(x_down1)
        x_down2 = self.conv_down1(x_down1)
        # x_down2 = self.conv_down1_norm(x_down2)
        return x_down2, x_down1, x_up2, x_up1


class TwoLevelUNetWarp(nn.Module):
    def __init__(self, channels: List[int]):
        super().__init__()
        self.conv_up1 = SparseConv3d(channels[0], channels[1], kernel_size=2, stride=2, bias=False)
        self.conv_up1_norm = InstanceNorm(channels[1])
        self.conv_up2 = SparseConv3d(channels[1], channels[2], kernel_size=2, stride=2, bias=False)
        self.conv_up2_norm = InstanceNorm(channels[2])
        # downsample
        self.conv_down2 = SparseConv3d(
            channels[2], channels[1], kernel_size=2, stride=2, bias=False, transposed=True
        )
        self.conv_down2_norm = InstanceNorm(channels[1])
        self.conv_down1 = SparseConv3d(
            channels[1], channels[0], kernel_size=2, stride=2, bias=False, transposed=True
        )
        self.conv_down1_norm = InstanceNorm(channels[0])

    def forward(self, x: Voxels):
        x_up1 = self.conv_up1(x)
        # x_up1 = self.conv_up1_norm(x_up1)
        x_up2 = self.conv_up2(x_up1)
        # x_up2 = self.conv_up2_norm(x_up2)
        x_down1 = self.conv_down2(x_up2, x_up1)
        # x_down1 = self.conv_down2_norm(x_down1)
        x_down2 = self.conv_down1(x_down1, x)
        # x_down2 = self.conv_down1_norm(x_down2)
        return x_down2, x_down1, x_up2, x_up1


class TestSpconvComparison(unittest.TestCase):

    def setUp(self) -> None:
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

    def test_spconv(self):
        in_C, out_C = self.C, 11
        spconv_st = spconv.SparseConvTensor(
            features=self.st.feature_tensor.float(),
            indices=self.st.batch_indexed_coordinates,
            spatial_shape=self.st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )
        conv = spconv.SubMConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=3,
            stride=1,
            bias=False,
        ).to(self.device)
        conv.weight.data.normal_(1, 2)
        out = conv(spconv_st)
        # out.weight.shape is (out_C, 3, 3, 3, in_C)

        conv_wp = SparseConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=3,
            stride=1,
            bias=False,
            compute_dtype=torch.float64,
        ).to(self.device)
        # conv_wp.weight.shape is (3^3, C_in, C_out)
        conv_wp.weight.data = conv.weight.data.permute(1, 2, 3, 4, 0).flatten(0, 2)
        out_wp = conv_wp(self.st)

        diff = torch.abs(out.features - out_wp.feature_tensor)
        print("diff.max(): ", diff.max().item())
        print("(diff / out.features).max() * 100: ", (diff / out.features).max().item() * 100)
        # float32
        # diff.max():  4.57763671875e-05
        # (diff / out.features).max() * 100:  0.618670741096139
        # float64
        # diff.max():  3.814697265625e-05
        # (diff / out.features).max() * 100:  0.618670741096139

    def test_spconv_backward(self):
        in_C, out_C = self.C, 11
        spconv_st = spconv.SparseConvTensor(
            features=self.st.feature_tensor.float().clone().requires_grad_(),
            indices=self.st.batch_indexed_coordinates,
            spatial_shape=self.st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )
        conv = spconv.SubMConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=3,
            stride=1,
            bias=False,
        ).to(self.device)
        conv.weight.data.normal_(1, 2)
        out = conv(spconv_st)
        # out.weight.shape is (out_C, 3, 3, 3, in_C)

        out.features.sum().backward()
        grad = spconv_st.features.grad

        # WarpConv
        conv_wp = SparseConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=3,
            stride=1,
            bias=False,
            accum_dtype=torch.float64,
        ).to(self.device)
        # conv_wp.weight.shape is (3^3, C_in, C_out)
        conv_wp.weight.data = conv.weight.data.permute(1, 2, 3, 4, 0).flatten(0, 2)
        self.st.batched_features.batched_tensor.requires_grad_()
        out_wp = conv_wp(self.st)
        out_wp.feature_tensor.sum().backward()
        grad_wp = self.st.feature_tensor.grad
        diff = torch.abs(grad - grad_wp)
        print("grad diff.max(): ", diff.max().item())
        print("(grad diff / grad).max() * 100: ", (diff / grad).max().item() * 100)
        # float32
        # grad diff.max():  9.1552734375e-05
        # (grad diff / grad).max() * 100:  0.0024100741939037107

    def test_strided_conv(self):
        in_C, out_C = self.C, 11
        st = self.st
        # st.batched_features.batched_tensor = torch.floor(st.feature_tensor / 0.1)
        spconv_st = spconv.SparseConvTensor(
            features=st.feature_tensor.float().clone().requires_grad_(),
            indices=st.batch_indexed_coordinates.int(),
            spatial_shape=st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )
        conv = spconv.SparseConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=2,
            stride=2,
            bias=False,
        ).to(self.device)
        conv.weight.data = torch.floor(conv.weight.data / 0.1)
        out = conv(spconv_st)

        conv_wp = SparseConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=2,
            stride=2,
            bias=False,
        ).to(self.device)
        conv_wp.weight.data = conv.weight.data.permute(1, 2, 3, 4, 0).flatten(0, 2)
        out_wp = conv_wp(st)

        # Get the coordinates and sort them
        to_unique_indices, _ = unique_inverse(out.indices)
        sorted_feats = out.features[to_unique_indices]
        sorted_coords = out.indices[to_unique_indices]

        # warpconv sort the features
        to_unique_wp, _ = unique_inverse(out_wp.batch_indexed_coordinates)
        sorted_feats_wp = out_wp.features[to_unique_wp]
        sorted_coords_wp = out_wp.batch_indexed_coordinates[to_unique_wp]

        self.assertTrue(torch.allclose(sorted_coords, sorted_coords_wp))
        diff = torch.abs(sorted_feats - sorted_feats_wp)
        print("strided conv diff.max(): ", diff.max().item())
        print(
            "(strided conv diff / sorted_feats).max() * 100: ",
            (diff / sorted_feats).max().item() * 100,
        )

    def test_transposed_conv(self):
        in_C, out_C = self.C, 11
        st = self.st
        st.batched_features.batched_tensor = st.features + 1
        spconv_st = spconv.SparseConvTensor(
            features=st.feature_tensor.float().clone().requires_grad_(),
            indices=st.batch_indexed_coordinates.int(),
            spatial_shape=st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )
        conv = spconv.SparseConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=2,
            stride=2,
            bias=False,
            indice_key="spconv_tr",
        ).to(self.device)
        conv_tr = spconv.SparseInverseConv3d(
            in_channels=out_C,
            out_channels=in_C,
            kernel_size=2,
            indice_key="spconv_tr",
            bias=False,
        ).to(self.device)

        conv.weight.data.normal_(1, 2)
        conv_tr.weight.data.normal_(1, 2)
        out = conv(spconv_st)
        out_tr = conv_tr(out)

        conv_wp = SparseConv3d(
            in_channels=in_C,
            out_channels=out_C,
            kernel_size=2,
            stride=2,
            bias=False,
        ).to(self.device)
        conv_wp.weight.data = conv.weight.data.permute(1, 2, 3, 4, 0).flatten(0, 2)
        conv_wp_tr = SparseConv3d(
            in_channels=out_C,
            out_channels=in_C,
            kernel_size=2,
            stride=2,
            transposed=True,
            bias=False,
        ).to(self.device)
        conv_wp_tr.weight.data = conv_tr.weight.data.permute(1, 2, 3, 4, 0).flatten(0, 2)

        out_wp = conv_wp(st)
        out_wp_tr = conv_wp_tr(out_wp, st)

        # transposed conv diff.max():  0.0009765625
        # (transposed conv diff / out_tr.features).max() * 100:  2.78951469808816
        diff = torch.abs(out_tr.features - out_wp_tr.features)
        print("transposed conv diff.max(): ", diff.max().item())
        print(
            "(transposed conv diff / out_tr.features).max() * 100: ",
            (diff / out_tr.features).max().item() * 100,
        )

    def test_two_level_unet(self):
        channels = [self.C, 32, 64]
        unet_spconv = TwoLevelUNetSPConv(channels).to(self.device)
        unet_warp = TwoLevelUNetWarp(channels).to(self.device)
        st = self.st.to(self.device)
        st.batched_features.batched_tensor.normal_(1, 2).requires_grad_()
        spconv_st = spconv.SparseConvTensor(
            features=st.feature_tensor.float().clone().requires_grad_(),
            indices=st.batch_indexed_coordinates.int(),
            spatial_shape=st.coordinate_tensor.max(dim=0).values + 1,
            batch_size=self.B,
        )
        # Set the weights to be large
        unet_spconv.conv_up1.weight.data.normal_(1, 2)
        unet_spconv.conv_up2.weight.data.normal_(1, 2)
        unet_spconv.conv_down1.weight.data.normal_(1, 2)
        unet_spconv.conv_down2.weight.data.normal_(1, 2)
        unet_warp.conv_up1.weight.data = sp2wp_weights(unet_spconv.conv_up1.weight.data)
        unet_warp.conv_up2.weight.data = sp2wp_weights(unet_spconv.conv_up2.weight.data)
        unet_warp.conv_down2.weight.data = sp2wp_weights(unet_spconv.conv_down2.weight.data)
        unet_warp.conv_down1.weight.data = sp2wp_weights(unet_spconv.conv_down1.weight.data)

        # Difference is significant
        out_spconv, out_spconv_down2, out_spconv_up2, out_spconv_up1 = unet_spconv(spconv_st)
        out_warp, out_warp_down2, out_wp_up2, out_wp_up1 = unet_warp(st)

        # Retain gradients
        out_spconv.features.retain_grad()
        out_spconv_down2.features.retain_grad()
        out_spconv_up2.features.retain_grad()
        out_spconv_up1.features.retain_grad()
        out_warp.feature_tensor.retain_grad()
        out_warp_down2.batched_features.batched_tensor.retain_grad()
        out_wp_up2.batched_features.batched_tensor.retain_grad()
        out_wp_up1.batched_features.batched_tensor.retain_grad()

        # Generate gradients
        out_spconv.features.sum().backward()
        out_warp.feature_tensor.sum().backward()

        def output_comparison(name, out_spconv, out_warp):
            to_unique_indices, _ = unique_inverse(out_spconv.indices)
            out_spconv_feat_sorted = out_spconv.features[to_unique_indices]
            out_spconv_coord_sorted = out_spconv.indices[to_unique_indices]
            to_unique_wp, _ = unique_inverse(out_warp.batch_indexed_coordinates)
            out_wp_feat_sorted = out_warp.features[to_unique_wp]
            out_wp_coord_sorted = out_warp.batch_indexed_coordinates[to_unique_wp]

            print(f"========={name}=========")
            assert torch.allclose(
                out_spconv_coord_sorted, out_wp_coord_sorted
            ), f"{name} coords mismatch"

            diff = torch.abs(out_spconv_feat_sorted - out_wp_feat_sorted)
            print(f"{name} spconv_feat.mean(): {out_spconv_feat_sorted.abs().mean().item():.4e}")
            print(f"{name} diff.max(): {diff.max().item():.4e}")
            print(f"{name} diff.mean(): {diff.mean().item():.4e}")
            print(
                f"{name} diff.max() rel: {(diff / out_spconv_feat_sorted).max().item() * 100:.4f}%",
            )
            print(
                f"{name} diff.mean() rel: {diff.mean().item() / out_spconv_feat_sorted.abs().mean().item() * 100:.4f}%",
            )
            print()

            # Gradients
            grad_spconv = out_spconv.features.grad[to_unique_indices]
            grad_warp = out_warp.batched_features.batched_tensor.grad[to_unique_wp]
            diff_grad = torch.abs(grad_spconv - grad_warp)
            print(f"{name} grad_spconv.mean(): {grad_spconv.abs().mean().item():.4e}")
            print(f"{name} grad_warp.mean(): {grad_warp.abs().mean().item():.4e}")
            print(f"{name} grad diff.max(): {diff_grad.max().item():.4e}")
            print(f"{name} grad diff.mean(): {diff_grad.mean().item():.4e}")
            print(
                f"{name} grad diff.max() rel: {(diff_grad / grad_spconv).max().item() * 100:.4f}%",
            )
            print(
                f"{name} grad diff.mean() rel: {diff_grad.mean().item() / grad_spconv.abs().mean().item() * 100:.4f}%",
            )
            print()

        output_comparison("up1", out_spconv_up1, out_wp_up1)
        output_comparison("up2", out_spconv_up2, out_wp_up2)
        output_comparison("down2", out_spconv_down2, out_warp_down2)
        output_comparison("down1", out_spconv, out_warp)


if __name__ == "__main__":
    # Running a function
    #
    # python -m unittest tests.test_spconv_comparison.TestSpconvComparison.test_two_level_unet
    unittest.main()

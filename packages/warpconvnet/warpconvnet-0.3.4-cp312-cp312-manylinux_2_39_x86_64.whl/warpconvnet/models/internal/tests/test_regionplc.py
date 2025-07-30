import unittest

import torch
import warp as wp
from warpconvnet.geometry.types.points import Points
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.models.internal.backbones.regionplc import SparseConvUNet


class TestSparseConvUNet(unittest.TestCase):
    def setUp(self):
        # Initialize Warp
        wp.init()
        torch.manual_seed(0)

        # Parameters for the test
        device = torch.device("cuda:0")
        self.B = 2  # Batch size
        min_N, max_N = 10000, 50000
        self.Ns = torch.randint(min_N, max_N, (self.B,)).tolist()
        self.C_in = 3  # Input channels
        self.voxel_size = 0.01

        # Generate random coordinates and features for each batch
        self.coords_list = [torch.rand((N, 3)) for N in self.Ns]
        self.features_list = [torch.rand((N, self.C_in)) for N in self.Ns]

        # Create input Voxels
        self.pc = Points(self.coords_list, self.features_list).to(
            device=device
        )
        self.input_st = self.pc.to_sparse(voxel_size=self.voxel_size)

    def test_sparse_conv_unet_forward(self):
        device = torch.device("cuda:0")

        in_channels = [32, 64, 96, 128]
        out_channels = [64, 96, 128, 128]
        # Instantiate the SparseConvUNet model
        model = SparseConvUNet(
            in_channel=self.C_in,
            in_channels=in_channels,
            out_channels=out_channels,
            num_blocks=4,
        ).to(device=device)

        # Pass the input through the model
        outputs = model(self.input_st.to(device=device))

        # Check that the output is a Voxels
        self.assertIsInstance(outputs, Voxels)

        # Check that the output features have the correct number of channels
        self.assertEqual(outputs.num_channels, out_channels[0])

        # Check that the output has the same number of points as the input
        self.assertEqual(outputs.features.shape[0], self.input_st.features.shape[0])

    def test_sparse_conv_unet_attention_forward(self):
        device = torch.device("cuda:0")

        in_channels = [32, 64, 96, 128]
        out_channels = [64, 96, 128, 128]

        # Test with mixed blocks (residual in shallow layers, attention in deep layers)
        model_mixed = SparseConvUNet(
            in_channel=self.C_in,
            in_channels=in_channels,
            out_channels=out_channels,
            num_blocks=1,
            block_types=["res", "res", "attn", "attn"],
            num_heads=[8, 8, 8, 8],
        ).to(device=device)

        # Test forward pass with mixed blocks
        outputs_mixed = model_mixed(self.input_st.to(device=device))
        self.assertIsInstance(outputs_mixed, Voxels)
        self.assertEqual(outputs_mixed.num_channels, out_channels[0])
        self.assertEqual(
            outputs_mixed.features.shape[0], self.input_st.features.shape[0]
        )


if __name__ == "__main__":
    unittest.main()

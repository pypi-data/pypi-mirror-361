import functools
import unittest

import torch
import warp as wp
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.models.backbones.mink_unet import (
    ConvTransformerBlock,
    MinkUNet18,
    MinkUNet50,
    MinkUNet101,
)
from warpconvnet.models.internal.backbones.mink_sparse_dense_unet import (
    MinkSparseDenseUNet,
    MinkUNetEncoder,
)
from warpconvnet.nn.modules.attention import PatchAttention, SpatialFeatureAttention


class TestMinkSparseDenseUNetEncoder(unittest.TestCase):
    def setUp(self):
        # Initialize Warp
        wp.init()
        torch.manual_seed(0)

        # Parameters for the test
        self.B = 2  # Batch size
        min_N, max_N = 10000, 50000
        self.Ns = torch.randint(min_N, max_N, (self.B,)).tolist()
        self.C_in = 3  # Input channels
        self.voxel_size = 0.01

        # Generate random coordinates and features for each batch
        self.coords_list = [(torch.rand((N, 3)) / self.voxel_size).int() for N in self.Ns]
        self.features_list = [torch.rand((N, self.C_in)) for N in self.Ns]

        # Create input Voxels
        self.input_st = Voxels(self.coords_list, self.features_list)

        # Parameters for the encoder
        self.encoder_channels = [32, 64, 128, 256]
        self.encoder_blocks = [2, 2, 2]
        self.initial_kernel_size = 5

    def test_encoder_output_shapes(self):
        device = torch.device("cuda:0")

        st = self.input_st.to(device=device)
        # Define block types for the encoder (all sparse in this test)
        encoder_block_types = ["sparse"] * len(self.encoder_channels)

        # Instantiate the encoder
        encoder = MinkUNetEncoder(
            in_channels=self.C_in,
            encoder_channels=self.encoder_channels,
            num_blocks_per_level=self.encoder_blocks,
            block_types=encoder_block_types,
            initial_kernel_size=self.initial_kernel_size,
            bias=False,
        ).to(device=device)

        # Pass the input through the encoder
        outputs = encoder(st)

        # Check that the outputs list has the correct length
        expected_length = len(self.encoder_channels)
        self.assertEqual(len(outputs), expected_length)

        # Check that output feature dimensions match encoder_channels
        for i, out in enumerate(outputs):
            if isinstance(out, Voxels):
                self.assertEqual(out.num_channels, self.encoder_channels[i])
            else:
                self.assertEqual(out.shape[1], self.encoder_channels[i])

    def test_encoder_dense_output_shapes(self):
        device = torch.device("cuda:0")

        st = self.input_st.to(device=device)
        # Define block types with a transition from sparse to dense
        encoder_block_types = ["sparse", "sparse", "dense", "dense"]

        # Instantiate the encoder
        encoder = MinkUNetEncoder(
            in_channels=self.C_in,
            encoder_channels=self.encoder_channels,
            num_blocks_per_level=self.encoder_blocks,
            block_types=encoder_block_types,
            initial_kernel_size=self.initial_kernel_size,
            bias=False,
        ).to(device=device)

        # Pass the input through the encoder
        outputs = encoder(st)

        # Check that the outputs list has the correct length
        expected_length = len(self.encoder_channels)
        self.assertEqual(len(outputs), expected_length)

        # Check output types and shapes
        for i, out in enumerate(outputs):
            block_type = encoder_block_types[i]
            if block_type == "sparse":
                self.assertIsInstance(out, Voxels)
                self.assertEqual(out.num_channels, self.encoder_channels[i])
            else:
                self.assertIsInstance(out, torch.Tensor)
                self.assertEqual(out.shape[1], self.encoder_channels[i])


class TestMinkUNet(unittest.TestCase):
    def setUp(self):
        # Initialize Warp
        wp.init()
        torch.manual_seed(0)

        # Parameters for the test
        self.B = 2  # Batch size
        min_N, max_N = 10000, 50000
        self.Ns = torch.randint(min_N, max_N, (self.B,)).tolist()
        self.C_in = 3  # Input channels
        self.C_out = 10  # Output channels
        self.voxel_size = 0.01

        # Generate random coordinates and features for each batch
        self.coords_list = [(torch.rand((N, 3)) / self.voxel_size).int() for N in self.Ns]
        self.features_list = [torch.rand((N, self.C_in)) for N in self.Ns]

        # Create input Voxels
        self.input_st = Voxels(self.coords_list, self.features_list)

        # Parameters for MinkUNet
        self.encoder_channels = [32, 64, 128, 256]
        self.decoder_channels = [256, 128, 64, 32]
        self.encoder_blocks = [2, 2, 2]
        self.decoder_blocks = [2, 2, 2]
        self.initial_kernel_size = 5
        self.final_kernel_size = 1

    def test_minkunet_forward(self):
        device = torch.device("cuda:0")

        # Instantiate the MinkUNet model
        model = MinkSparseDenseUNet(
            in_channels=self.C_in,
            out_channels=self.C_out,
            encoder_channels=self.encoder_channels,
            decoder_channels=self.decoder_channels,
            encoder_blocks=self.encoder_blocks,
            decoder_blocks=self.decoder_blocks,
            dense_depth=2,
            initial_kernel_size=self.initial_kernel_size,
            final_kernel_size=self.final_kernel_size,
            bias=False,
        ).to(device=device)

        # Pass the input through the model
        output = model(self.input_st.to(device=device))

        # Check that the output is a Voxels or torch.Tensor
        self.assertTrue(isinstance(output, (Voxels, torch.Tensor)))

        # Check that the output features have the correct number of channels
        if isinstance(output, Voxels):
            self.assertEqual(output.num_channels, self.C_out)
        else:
            self.assertEqual(output.shape[1], self.C_out)

    def test_minkunet50_forward(self):
        device = torch.device("cuda:0")

        # Instantiate the MinkUNet50 model
        model = MinkUNet50(
            in_channels=self.C_in,
            out_channels=self.C_out,
            block_types="bbbbbbbb",  # Mix of block types
            num_heads=4,
            patch_sizes=1024,
        ).to(device)

        # Pass the input through the model
        input_tensor = self.input_st.to(device)
        output = model(input_tensor)

        # Check output type and shape
        self.assertIsInstance(output, Voxels)
        self.assertEqual(output.num_channels, self.C_out)

        # Verify that the output features are not all zeros
        for features in output.features:
            self.assertFalse(torch.allclose(features, torch.zeros_like(features)))

    def test_minkunet101_forward(self):
        device = torch.device("cuda:0")

        # Instantiate the MinkUNet101 model
        model = MinkUNet101(
            in_channels=self.C_in,
            out_channels=self.C_out,
            block_types="bbbbbbbb",  # Mix of block types
            num_heads=4,
            patch_sizes=1024,
        ).to(device)

        # Pass the input through the model
        input_tensor = self.input_st.to(device)
        output = model(input_tensor)

        # Check output type and shape
        self.assertIsInstance(output, Voxels)
        self.assertEqual(output.num_channels, self.C_out)

        # Verify that the output features are not all zeros
        for features in output.features:
            self.assertFalse(torch.allclose(features, torch.zeros_like(features)))


class TestTransformerBlocks(unittest.TestCase):
    def setUp(self):
        # Initialize Warp
        wp.init()
        torch.manual_seed(0)

        # Parameters for the test
        self.B = 2  # Batch size
        min_N, max_N = 1000, 5000  # Smaller numbers for faster testing
        self.Ns = torch.randint(min_N, max_N, (self.B,)).tolist()
        self.C_in = 32  # Input channels
        self.C_out = 64  # Output channels
        self.voxel_size = 0.01

        # Generate random coordinates and features
        self.coords_list = [(torch.rand((N, 3)) / self.voxel_size).int() for N in self.Ns]
        self.features_list = [torch.rand((N, self.C_in)) for N in self.Ns]

        # Create input Voxels
        self.input_st = Voxels(self.coords_list, self.features_list)

    def test_basic_transformer_block(self):
        device = torch.device("cuda:0")

        # Create transformer block
        transformer_block = ConvTransformerBlock(
            in_channels=self.C_in,
            out_channels=self.C_out,
            num_heads=4,
            qkv_bias=True,
            attn_drop=0.1,
            proj_drop=0.1,
            attn_fn=functools.partial(SpatialFeatureAttention, use_encoding=False),
        ).to(device)

        # Pass input through transformer block
        input_tensor = self.input_st.to(device)
        output = transformer_block(input_tensor)

        # Check output type and shape
        self.assertIsInstance(output, Voxels)
        self.assertEqual(output.num_channels, self.C_out)

        # Check that the output coordinates match the input
        for i in range(len(self.coords_list)):
            self.assertTrue(torch.equal(output.coordinates[i], input_tensor.coordinates[i]))

    def test_minkunet_with_transformers(self):
        device = torch.device("cuda:0")

        # Create MinkUNet with transformer blocks
        model = MinkUNet18(
            in_channels=self.C_in,
            out_channels=self.C_out,
            block_types="bbbbbbbb",  # Mix of block types
            num_heads=4,
            patch_sizes=1024,
        ).to(device)

        # Pass input through model
        input_tensor = self.input_st.to(device)
        output = model(input_tensor)

        # Check output type and shape
        self.assertIsInstance(output, Voxels)
        self.assertEqual(output.num_channels, self.C_out)

    def test_transformer_attention_output(self):
        device = torch.device("cuda:0")

        # Create transformer block with spatial feature attention
        transformer_block = ConvTransformerBlock(
            in_channels=self.C_in,
            out_channels=self.C_out,
            num_heads=4,
            qkv_bias=True,
            attn_drop=0.0,  # No dropout for deterministic testing
            proj_drop=0.0,
        ).to(device)

        # Process same input twice
        input_tensor = self.input_st.to(device)
        output1 = transformer_block(input_tensor)
        output2 = transformer_block(input_tensor)

        # Check that outputs are identical (deterministic behavior)
        for i in range(len(self.coords_list)):
            self.assertTrue(torch.allclose(output1.features[i], output2.features[i]))

    def test_patch_attention_block(self):
        device = torch.device("cuda:0")

        # Create transformer block with patch attention
        transformer_block = ConvTransformerBlock(
            in_channels=self.C_in,
            out_channels=self.C_out,
            num_heads=4,
            qkv_bias=True,
            attn_fn=functools.partial(PatchAttention, patch_size=512, rand_perm_patch=False),
        ).to(device)

        # Process input
        input_tensor = self.input_st.to(device)
        output = transformer_block(input_tensor)

        # Verify output
        self.assertIsInstance(output, Voxels)
        self.assertEqual(output.num_channels, self.C_out)

        # Check that features are not all zeros (attention is working)
        for features in output.features:
            self.assertFalse(torch.allclose(features, torch.zeros_like(features)))


if __name__ == "__main__":
    unittest.main()

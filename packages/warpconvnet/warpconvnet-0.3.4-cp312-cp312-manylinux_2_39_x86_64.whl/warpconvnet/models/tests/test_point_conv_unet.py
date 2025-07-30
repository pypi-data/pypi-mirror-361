import unittest

import torch
import warp as wp
from warpconvnet.geometry.coords.search.search_configs import RealSearchConfig
from warpconvnet.geometry.ops.neighbor_search_continuous import RealSearchMode
from warpconvnet.geometry.types.points import Points
from warpconvnet.models.backbones.point_conv_unet import PointConvUNet
from warpconvnet.ops.reductions import REDUCTIONS


class TestPointConvUNet(unittest.TestCase):
    def setUp(self):
        wp.init()
        self.device = torch.device("cuda:0")
        self.B, min_N, max_N, self.C = 3, 1000, 10000, 7
        self.Ns = torch.randint(min_N, max_N, (self.B,))
        self.coords = [torch.rand((N, 3)) for N in self.Ns]
        self.features = [torch.rand((N, self.C)) for N in self.Ns]
        self.pc = Points(self.coords, self.features).to(self.device)

    def test_point_conv_unet(self):
        pc = self.pc
        # Create conv layer
        in_channels, out_channels = self.C, 16
        search_args = RealSearchConfig(
            mode=RealSearchMode.RADIUS,
        )
        down_channels = [16, 32, 64]
        up_channels = [16, 32, 64]
        neighbor_search_radii = [0.1, 0.2]
        downsample_voxel_sizes = [0.1, 0.2]
        unet = PointConvUNet(
            in_channels=in_channels,
            out_channels=out_channels,
            down_channels=down_channels,
            up_channels=up_channels,
            neighbor_search_args=search_args,
            neighbor_search_radii=neighbor_search_radii,
            pooling_reduction=REDUCTIONS.MEAN,
            downsample_voxel_sizes=downsample_voxel_sizes,
            num_levels=2,
        ).to(self.device)
        # Forward pass
        out = unet(pc)
        # backward
        out[0].feature_tensor.mean().backward()
        # print the conv param grads
        for name, param in unet.named_parameters():
            if param.grad is not None:
                print(name, param.grad.shape)
            else:
                print(name, "has no grad")


if __name__ == "__main__":
    wp.init()
    unittest.main()

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, Tuple

import torch
import torch.nn as nn

from warpconvnet.geometry.base.geometry import Geometry


class BaseSpatialModule(nn.Module):
    """Base module for spatial features. The input must be an instance of `BatchedSpatialFeatures`."""

    @property
    def device(self):
        """Returns the device that the model is on."""
        return next(self.parameters()).device

    def forward(self, x: Geometry):
        """Forward pass."""
        raise NotImplementedError


class BaseSpatialModel(BaseSpatialModule):
    """Base model class."""

    def data_dict_to_input(self, data_dict, **kwargs) -> Any:
        """Convert data dictionary to appropriate input for the model."""
        raise NotImplementedError

    def loss_dict(self, data_dict, **kwargs) -> Dict:
        """Compute the loss dictionary for the model."""
        raise NotImplementedError

    @torch.no_grad()
    def eval_dict(self, data_dict, **kwargs) -> Dict:
        """Compute the evaluation dictionary for the model."""
        raise NotImplementedError

    def image_pointcloud_dict(self, data_dict, datamodule) -> Tuple[Dict, Dict]:
        """Compute the image dict and pointcloud dict for the model."""
        raise NotImplementedError

from contextlib import nullcontext

import pytest
import torch
import warp as wp
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.models.backbones.mink_unet import MinkUNet34


@pytest.fixture
def setup_voxel_data():
    """Setup fixed coordinate and feature data for benchmarking."""
    wp.init()
    torch.manual_seed(0)
    device = "cuda:0"

    # Fixed configuration for data generation
    B, min_N, max_N = 3, 100000, 1000000
    base_channels = 32  # Use maximum channel size for feature generation

    # Generate fixed coordinates and features
    Ns = torch.randint(min_N, max_N, (B,))
    voxel_size = 0.01
    # default dtype is float32
    coords = [(torch.rand((N, 3), device=device) / voxel_size).int() for N in Ns]
    features = [torch.randn((N, base_channels), device=device) for N in Ns]

    return coords, features


@pytest.mark.benchmark(group="mink_unet")
@pytest.mark.parametrize(
    "model_class,amp_config",
    [
        # (model, (use_amp, amp_dtype, compute_dtype))
        (MinkUNet34, (False, None, None)),  # baseline fp32
        (MinkUNet34, (True, torch.float16, None)),  # amp fp16
        (MinkUNet34, (True, torch.bfloat16, None)),  # amp bf16
        (MinkUNet34, (True, torch.float16, torch.float16)),  # amp fp16 + compute fp16
        (MinkUNet34, (True, torch.float16, torch.bfloat16)),  # amp fp16 + compute bf16
    ],
    ids=[
        "unet34_fp32",
        "unet34_amp_fp16",
        "unet34_amp_bf16",
        "unet34_amp_fp16_comp_fp16",
        "unet34_amp_fp16_comp_bf16",
    ],
)
def test_mink_unet_speed(model_class, amp_config, setup_voxel_data, benchmark):
    """Benchmark MinkUNet with different precision configurations."""
    use_amp, amp_dtype, compute_dtype = amp_config
    device = "cuda:0"
    coords, base_features = setup_voxel_data

    # Slice features if needed to match in_channels
    features = [f[:, :3] for f in base_features]
    input_voxels = Voxels(coords, features, device=device).unique()

    model = model_class(in_channels=3, out_channels=10, compute_dtype=compute_dtype).to(device)

    def run_forward():
        with torch.no_grad():
            ctx = torch.cuda.amp.autocast(dtype=amp_dtype) if use_amp else nullcontext()
            with ctx:
                return model(input_voxels)

    result = benchmark.pedantic(
        run_forward,
        iterations=4,
        rounds=3,
        warmup_rounds=1,
    )


@pytest.mark.benchmark(group="mink_unet_train")
@pytest.mark.parametrize(
    "model_class,amp_config",
    [
        (MinkUNet34, (False, None, None)),  # baseline fp32
        (MinkUNet34, (True, torch.float16, None)),  # amp fp16
        (MinkUNet34, (True, torch.bfloat16, None)),  # amp bf16
    ],
    ids=[
        "unet34_fp32",
        "unet34_amp_fp16",
        "unet34_amp_bf16",
    ],
)
def test_mink_unet_train_speed(model_class, amp_config, setup_voxel_data, benchmark):
    """Benchmark MinkUNet training with different precision configurations."""
    use_amp, amp_dtype, compute_dtype = amp_config
    device = "cuda:0"
    coords, base_features = setup_voxel_data

    features = [f[:, :3] for f in base_features]
    input_voxels = Voxels(coords, features, device=device).unique()

    model = model_class(in_channels=3, out_channels=10, compute_dtype=compute_dtype).to(device)

    optimizer = torch.optim.Adam(model.parameters())
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    def run_train_step():
        optimizer.zero_grad(set_to_none=True)
        ctx = torch.cuda.amp.autocast(dtype=amp_dtype) if use_amp else nullcontext()
        with ctx:
            output = model(input_voxels)
            loss = output.features.mean()

        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

    result = benchmark.pedantic(
        run_train_step,
        iterations=4,
        rounds=3,
        warmup_rounds=1,
    )

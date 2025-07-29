# Copyright (c) 2025, Wentao Guo, Ted Zadouri, Tri Dao.

import pytest
import torch

from quack.rmsnorm import rmsnorm, rmsnorm_ref, rstd_ref


@pytest.mark.parametrize("eps", [1e-5, 1e-6])
# @pytest.mark.parametrize("eps", [1e-5])
@pytest.mark.parametrize("input_dtype", [torch.bfloat16, torch.float16, torch.float32])
# @pytest.mark.parametrize("input_dtype", [torch.bfloat16])
@pytest.mark.parametrize(
    "N",
    [192, 256, 512, 760, 1024, 1128, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144]
    # [192]
)
@pytest.mark.parametrize("M", [1, 37, 199])
# @pytest.mark.parametrize("M", [1])
def test_rmsnorm_forward(M, N, input_dtype, eps):
    """Test RMSNorm forward pass against reference implementation."""
    device = "cuda"
    # Set tolerance based on dtype
    if input_dtype == torch.bfloat16:
        atol = 5e-2
    elif input_dtype == torch.float16:
        atol = 1e-2
    else:
        atol = 1e-4
    torch.random.manual_seed(0)
    x = torch.randn(M, N, device=device, dtype=input_dtype, requires_grad=True)
    weight = torch.randn(N, device=device, dtype=torch.float32, requires_grad=True)
    x_ref = x.detach().clone().requires_grad_()
    weight_ref = weight.detach().clone().requires_grad_()
    out, rstd = rmsnorm(x, weight, eps=eps, return_rstd=True)
    out_ref = rmsnorm_ref(x_ref, weight_ref, eps=eps)
    rstd_ref_val = rstd_ref(x_ref, eps=eps)

    # Check output shape and dtype
    assert out.shape == x.shape
    assert out.dtype == input_dtype
    assert rstd.shape == (M,)
    assert rstd.dtype == torch.float32

    # Check accuracy
    torch.testing.assert_close(out, out_ref, atol=atol, rtol=1e-3)
    torch.testing.assert_close(rstd, rstd_ref_val, atol=atol, rtol=1e-3)


# @pytest.mark.parametrize("eps", [1e-5, 1e-6])
# @pytest.mark.parametrize("input_dtype", [torch.float16, torch.bfloat16, torch.float32])
# @pytest.mark.parametrize("N", [1024, 4096, 16384])
# def test_rmsnorm_backward(N, input_dtype, eps):
#     """Test RMSNorm backward pass against reference implementation."""
#     device = "cuda"
#     M = 32

#     # Set tolerance based on dtype
#     if input_dtype == torch.bfloat16:
#         atol = 5e-2
#     elif input_dtype == torch.float16:
#         atol = 1e-2
#     else:
#         atol = 1e-4

#     # Set seed for reproducibility
#     torch.random.manual_seed(0)

#     # Create input tensors
#     x = torch.randn(M, N, device=device, dtype=input_dtype, requires_grad=True)
#     weight = torch.randn(N, device=device, dtype=torch.float32, requires_grad=True)

#     # Clone for reference
#     x_ref = x.detach().clone().requires_grad_()
#     weight_ref = weight.detach().clone().requires_grad_()

#     # Forward pass
#     out = rmsnorm(x, weight, eps=eps)
#     out_ref = rmsnorm_ref(x_ref, weight_ref, eps=eps)

#     # Backward pass
#     grad_out = torch.randn_like(out)
#     out.backward(grad_out)
#     out_ref.backward(grad_out)

#     # Check gradients
#     torch.testing.assert_close(x.grad, x_ref.grad, atol=atol, rtol=1e-3)
#     torch.testing.assert_close(weight.grad, weight_ref.grad, atol=atol, rtol=1e-3)


@pytest.mark.parametrize("return_rstd", [True, False])
def test_rmsnorm_return_rstd_option(return_rstd):
    """Test that return_rstd option works correctly."""
    device = "cuda"
    M, N = 32, 1024
    eps = 1e-6

    x = torch.randn(M, N, device=device, dtype=torch.float16)
    weight = torch.randn(N, device=device, dtype=torch.float32)

    if return_rstd:
        out, rstd = rmsnorm(x, weight, eps=eps, return_rstd=True)
        assert out.shape == (M, N)
        assert rstd.shape == (M,)
        assert rstd.dtype == torch.float32
    else:
        out = rmsnorm(x, weight, eps=eps, return_rstd=False)
        assert out.shape == (M, N)
        assert isinstance(out, torch.Tensor)


def test_rmsnorm_input_validation():
    """Test input validation and error handling."""
    device = "cuda"

    # Test 3D input (should fail)
    x_3d = torch.randn(2, 32, 1024, device=device, dtype=torch.float16)
    weight = torch.randn(1024, device=device, dtype=torch.float32)

    with pytest.raises(AssertionError, match="Input must be 2D"):
        rmsnorm(x_3d, weight)

    # Test weight dimension mismatch
    x = torch.randn(32, 1024, device=device, dtype=torch.float16)
    weight_wrong = torch.randn(512, device=device, dtype=torch.float32)

    with pytest.raises(AssertionError, match="Last dimension of input must match weight dimension"):
        rmsnorm(x, weight_wrong)

    # Test CPU tensors (should fail)
    x_cpu = torch.randn(32, 1024, dtype=torch.float16)
    weight_cpu = torch.randn(1024, dtype=torch.float32)

    with pytest.raises(AssertionError, match="Tensors must be on CUDA device"):
        rmsnorm(x_cpu, weight_cpu)

    # Test unsupported dtype
    x = torch.randn(32, 1024, device=device, dtype=torch.float64)
    weight = torch.randn(1024, device=device, dtype=torch.float32)

    with pytest.raises(AssertionError, match="Unsupported dtype"):
        rmsnorm(x, weight)

    # Test wrong weight dtype
    x = torch.randn(32, 1024, device=device, dtype=torch.float16)
    weight_wrong_dtype = torch.randn(1024, device=device, dtype=torch.float16)

    with pytest.raises(AssertionError, match="Weight must be float32"):
        rmsnorm(x, weight_wrong_dtype)


def test_rmsnorm_compile_cache():
    """Test that compile cache works correctly for repeated calls."""
    device = "cuda"
    M, N = 32, 1024
    eps = 1e-6

    # Clear cache
    rmsnorm.compile_cache.clear()
    assert len(rmsnorm.compile_cache) == 0

    x1 = torch.randn(M, N, device=device, dtype=torch.float16)
    weight1 = torch.randn(N, device=device, dtype=torch.float32)

    # First call should compile
    out1 = rmsnorm(x1, weight1, eps=eps)
    assert len(rmsnorm.compile_cache) == 1

    # Same shape should reuse cache
    x2 = torch.randn(M, N, device=device, dtype=torch.float16)
    weight2 = torch.randn(N, device=device, dtype=torch.float32)
    out2 = rmsnorm(x2, weight2, eps=eps)
    assert len(rmsnorm.compile_cache) == 1

    # Different shape should create new cache entry
    x3 = torch.randn(M, N * 2, device=device, dtype=torch.float16)
    weight3 = torch.randn(N * 2, device=device, dtype=torch.float32)
    out3 = rmsnorm(x3, weight3, eps=eps)
    assert len(rmsnorm.compile_cache) == 2

    # Different dtype should create new cache entry
    x4 = torch.randn(M, N, device=device, dtype=torch.float32)
    weight4 = torch.randn(N, device=device, dtype=torch.float32)
    out4 = rmsnorm(x4, weight4, eps=eps)
    assert len(rmsnorm.compile_cache) == 3

# Copyright (c) 2025, Wentao Guo, Ted Zadouri, Tri Dao.


import torch
from typing import Optional

import cuda.bindings.driver as cuda

import cutlass
import cutlass.cute as cute
from cutlass.cute.runtime import from_dlpack
import quack.utils as utils
from quack.reduction_base import ReductionBase, torch2cute_dtype_map


class RMSNorm(ReductionBase):
    def __init__(self, dtype: cutlass.Numeric, N: int):
        super().__init__(dtype, N, stage=1)
        self.reload_from = None if N <= 16384 else "smem"
        self.delay_w_load = False

    def _calculate_threads_per_row(self):
        N = self.N
        return (
            8
            if N <= 64
            else (
                16
                if N <= 128
                else (32 if N <= 3072 else (64 if N <= 6144 else (128 if N <= 16384 else 256)))
            )
        )

    def _set_cluster_n(self):
        N = self.N
        # cluster_n = 4 is faster and cluster_n = 2 for N=64k for some reason
        # Similarly cluster_n = 8 is faster for N=128k
        if cutlass.const_expr(self.dtype.width == 16):
            cluster_n = (
                1
                if N <= 16 * 1024
                else (
                    2
                    if N <= 32 * 1024
                    else (4 if N <= 64 * 1024 else (8 if N <= 128 * 1024 else 16))
                )
            )
        else:  # fp32
            cluster_n = (
                1
                if N <= 32 * 1024
                else (
                    2
                    if N <= 64 * 1024
                    else (4 if N <= 128 * 1024 else (8 if N <= 256 * 1024 else 16))
                )
            )
        self.cluster_n = cluster_n

    @cute.jit
    def __call__(
        self,
        mX: cute.Tensor,
        mW: cute.Tensor,
        mO: cute.Tensor,
        mRstd: Optional[cute.Tensor],
        stream: cuda.CUstream,
        eps: cutlass.Float32 = 1e-6,
    ):
        assert mX.element_type == self.dtype
        assert mO.element_type == self.dtype
        self._set_cluster_n()
        tiler_mn, tv_layout = self._get_tv_layout()
        num_threads = cute.size(tv_layout, mode=[0])
        num_warps = num_threads // cute.arch.WARP_SIZE
        mW_expanded_layout = cute.prepend(mW.layout, cute.make_layout((tiler_mn[0],), stride=(0,)))
        mW = cute.make_tensor(mW.iterator, mW_expanded_layout)
        if cutlass.const_expr(mRstd is not None):
            mRstd_expanded_layout = cute.append(
                mRstd.layout, cute.make_layout((self.N,), stride=(0,))
            )
            mRstd = cute.make_tensor(mRstd.iterator, mRstd_expanded_layout)
        self.kernel(mX, mW, mO, mRstd, eps, tv_layout, tiler_mn, self.reload_from).launch(
            grid=[cute.ceil_div(mX.shape[0], tiler_mn[0]), self.cluster_n, 1],
            block=[num_threads, 1, 1],
            cluster=[1, self.cluster_n, 1] if cutlass.const_expr(self.cluster_n > 1) else None,
            smem=self._smem_size_in_bytes(tiler_mn, num_warps),
            stream=stream,
        )

    @cute.kernel
    def kernel(
        self,
        mX: cute.Tensor,
        mW: cute.Tensor,
        mO: cute.Tensor,
        mRstd: Optional[cute.Tensor],
        eps: cute.Float32,
        tv_layout: cute.Layout,
        tiler_mn: cute.Shape,
        reload_from: cutlass.Constexpr = None,
        delay_w_load: cutlass.Constexpr = False,
    ):
        tidx, _, _ = cute.arch.thread_idx()
        bidx, _, _ = cute.arch.block_idx()
        if cutlass.const_expr(self.cluster_n > 1):
            cluster_y = cute.arch.block_idx()[1]
        else:
            cluster_y = cutlass.const_expr(0)

        smem = cutlass.utils.SmemAllocator()
        sX = smem.allocate_tensor(
            mX.element_type, cute.make_ordered_layout(tiler_mn, order=(1, 0)), byte_alignment=16
        )
        reduction_buffer, mbar_ptr = self._allocate_reduction_buffer_and_mbar(smem, tv_layout)

        shape = mX.shape
        idX = cute.make_identity_tensor(shape)
        # slice for CTAs
        gX, gO, cX = [cute.local_tile(mT, tiler_mn, (bidx, cluster_y)) for mT in (mX, mO, idX)]
        gW = cute.local_tile(mW, tiler_mn, (0, cluster_y))
        gRstd = (
            cute.local_tile(mRstd, tiler_mn, (bidx, cluster_y))
            if cutlass.const_expr(mRstd is not None)
            else None
        )

        # declare the atoms which will be used later for memory copy
        copy_atom_load_X = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mX.element_type, num_bits_per_copy=128
        )
        copy_atom_load_X_async = cute.make_copy_atom(
            cute.nvgpu.cpasync.CopyG2SOp(), mX.element_type, num_bits_per_copy=128
        )
        copy_atom_load_W = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mW.element_type, num_bits_per_copy=128
        )
        copy_atom_store_O = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mO.element_type, num_bits_per_copy=128
        )

        thr_copy_X = cute.make_tiled_copy(copy_atom_load_X_async, tv_layout, tiler_mn).get_slice(
            tidx
        )
        thr_copy_W = cute.make_tiled_copy(copy_atom_load_W, tv_layout, tiler_mn).get_slice(tidx)
        thr_copy_O = cute.make_tiled_copy(copy_atom_store_O, tv_layout, tiler_mn).get_slice(tidx)

        tWgW = thr_copy_W.partition_S(gW)
        tXgX = thr_copy_X.partition_S(gX)
        tXsX = thr_copy_X.partition_D(sX)
        tXgO = thr_copy_O.partition_D(gO)
        tXrRstd = thr_copy_O.partition_D(gRstd) if cutlass.const_expr(mRstd is not None) else None
        tXcX = thr_copy_X.partition_S(cX)[(0, None), None, None]

        # allocate fragments for gmem->rmem
        tWrW = cute.make_fragment_like(tWgW)
        tXrW = thr_copy_X.retile(tWrW)
        tXrX, tXrO = [cute.make_fragment_like(thr) for thr in (tXgX, tXgO)]

        num_warps = cute.size(tv_layout, mode=[0]) // cute.arch.WARP_SIZE
        self._initialize_cluster(tidx, mbar_ptr, num_warps)

        tXpX = utils.predicate_k(thr_copy_X.partition_S(cX), limit=shape[1])
        row = tXcX[0][0]
        if row < shape[0]:
            cute.copy(copy_atom_load_X_async, tXgX, tXsX, pred=tXpX)
        cute.arch.cp_async_commit_group()

        tWpW = utils.predicate_k(thr_copy_W.partition_S(cX), limit=shape[1])
        if cutlass.const_expr(not delay_w_load):
            cute.copy(copy_atom_load_W, tWgW, tWrW, pred=tWpW)

        cute.arch.cp_async_wait_group(0)
        cute.autovec_copy(tXsX, tXrX)
        x = tXrX.load().to(cute.Float32)
        threads_per_row = tv_layout.shape[0][0]
        sum_sq_x = utils.row_reduce(
            x * x,
            cute.ReductionOp.ADD,
            threads_per_row,
            reduction_buffer[None, None, 0],
            mbar_ptr,
            init_val=0.0,
            hook_fn=cute.arch.cluster_wait if cutlass.const_expr(self.cluster_n > 1) else None,
        )
        rstd = utils.rsqrt(sum_sq_x / shape[1] + eps)
        if cutlass.const_expr(mRstd is not None):
            # Only the thread corresponding to column 0 writes out the rstd to gmem
            if (
                tXcX[0][1] == 0
                and row < shape[0]
                and (self.cluster_n == 1 or cute.arch.block_idx_in_cluster() == 0)
            ):
                tXrRstd[0] = rstd
        if cutlass.const_expr(delay_w_load):
            cute.copy(copy_atom_load_W, tWgW, tWrW, pred=tWpW)
        if cutlass.const_expr(reload_from == "smem"):
            cute.autovec_copy(tXsX, tXrX)
            x = tXrX.load().to(cute.Float32)
        elif cutlass.const_expr(reload_from == "gmem"):
            cute.copy(copy_atom_load_X, tXgX, tXrX, pred=tXpX)
            x = tXrX.load().to(cute.Float32)
        x_hat = x * rstd
        w = tXrW.load().to(cute.Float32)
        y = x_hat * w
        tXrO.store(y.to(tXrO.element_type))
        tOpO = utils.predicate_k(thr_copy_O.partition_S(cX), limit=shape[1])
        if row < shape[0]:
            cute.copy(copy_atom_store_O, tXrO, tXgO, pred=tOpO)


def _rmsnorm_fwd(
    x: torch.Tensor,
    weight: torch.Tensor,
    eps: float = 1e-6,
    return_rstd: bool = False,
) -> torch.Tensor:
    """RMSNorm forward pass.
    Args:
        x: Input tensor of shape (M, N)
        weight: Weight tensor of shape (N,)
        eps: Small value for numerical stability
        return_rstd: Whether to return the reciprocal standard deviation
    Returns:
        Normalized output tensor of same shape as x
        If return_rstd is True, also returns rstd tensor of shape (M,)
    """
    assert x.dim() == 2, "Input must be 2D"
    assert weight.dim() == 1, "Weight must be 1D"
    assert x.shape[-1] == weight.shape[0], "Last dimension of input must match weight dimension"
    assert x.is_cuda and weight.is_cuda, "Tensors must be on CUDA device"
    assert x.dtype in [torch.float16, torch.bfloat16, torch.float32], "Unsupported dtype"
    assert weight.dtype == torch.float32, "Weight must be float32"
    M, N = x.shape
    device = x.device
    out = torch.empty_like(x)
    rstd = torch.empty(M, device=device, dtype=torch.float32) if return_rstd else None
    dtype = torch2cute_dtype_map[x.dtype]
    convert_from_dlpack = lambda x: (
        from_dlpack(x.detach(), assumed_align=16).mark_compact_shape_dynamic(
            mode=0, stride_order=(0, 1)
        )
    )
    x_tensor, out_tensor = [
        # utils.convert_from_dlpack(t, leading_dim=t.ndim - 1, divisibility=128 // dtype.width)
        convert_from_dlpack(t)
        for t in (x, out)
    ]
    weight_tensor = utils.convert_from_dlpack(
        weight.detach(), leading_dim=0, divisibility=128 // cutlass.Float32.width
    )
    rstd_tensor = (
        from_dlpack(rstd.detach(), assumed_align=4).mark_layout_dynamic(leading_dim=0)
        if rstd is not None
        else None
    )
    current_stream = cuda.CUstream(torch.cuda.current_stream().cuda_stream)
    compile_key = (dtype, N, rstd is not None)
    if compile_key not in _rmsnorm_fwd.compile_cache:
        rmsnorm_op = RMSNorm(dtype, N)
        _rmsnorm_fwd.compile_cache[compile_key] = cute.compile(
            rmsnorm_op, x_tensor, weight_tensor, out_tensor, rstd_tensor, current_stream
        )
    _rmsnorm_fwd.compile_cache[compile_key](
        x_tensor, weight_tensor, out_tensor, rstd_tensor, current_stream, eps
    )
    return (out, rstd) if return_rstd else out


_rmsnorm_fwd.compile_cache = {}


def rmsnorm_ref(x, w, eps=1e-6):
    x_f32 = x.float()
    return (x_f32 / (torch.sqrt(torch.mean(x_f32.square(), dim=-1, keepdim=True) + eps)) * w).to(
        x.dtype
    )


def rstd_ref(x, eps=1e-6):
    x_f32 = x.float()
    return 1.0 / torch.sqrt(torch.mean(x_f32 * x_f32, dim=-1) + eps)


def rmsnorm_bwd_ref(x, w, dout, rstd, eps=1e-6):
    """Reference implementation for RMSNorm backward pass."""
    x_f32 = x.float()
    x_hat = x_f32 * rstd.unsqueeze(1)
    wdy = dout * w
    c1 = (x_hat * wdy).mean(dim=-1, keepdim=True)
    dx = (wdy - x_hat * c1) * rstd.unsqueeze(1)

    # dL/dW
    dw = (dout * x_hat).sum(dim=0)
    return dx.to(x.dtype), dw.to(w.dtype)


class RMSNormBackward(ReductionBase):
    def __init__(self, dtype: cutlass.Numeric, N: int):
        # 1 stage for computing mean of x_hat * wdy
        super().__init__(dtype, N, stage=1, reduction_dtype=cutlass.Float32)

    def _calculate_threads_per_row(self):
        N = self.N
        return (
            8
            if N <= 64
            else (
                16
                if N <= 128
                else (32 if N <= 3072 else (64 if N <= 6144 else (128 if N <= 16384 else 256)))
            )
        )

    def _set_cluster_n(self):
        N = self.N
        if cutlass.const_expr(self.dtype.width == 16):
            cluster_n = (
                1
                if N <= 16 * 1024
                else (
                    2
                    if N <= 32 * 1024
                    else (4 if N <= 64 * 1024 else (8 if N <= 128 * 1024 else 16))
                )
            )
        else:  # fp32
            cluster_n = (
                1
                if N <= 32 * 1024
                else (
                    2
                    if N <= 64 * 1024
                    else (4 if N <= 128 * 1024 else (8 if N <= 256 * 1024 else 16))
                )
            )
        self.cluster_n = cluster_n

    @cute.jit
    def __call__(
        self,
        mX: cute.Tensor,
        mW: cute.Tensor,
        mDout: cute.Tensor,
        mRstd: cute.Tensor,
        mDx: cute.Tensor,
        mDw: cute.Tensor,
        sm_count: cutlass.Constexpr,
        stream: cuda.CUstream,
    ):
        self._set_cluster_n()
        tiler_mn, tv_layout = self._get_tv_layout()
        num_threads = cute.size(tv_layout, mode=[0])
        num_warps = num_threads // cute.arch.WARP_SIZE

        mW_expanded_layout = cute.prepend(mW.layout, cute.make_layout((tiler_mn[0],), stride=(0,)))
        mW = cute.make_tensor(mW.iterator, mW_expanded_layout)

        mRstd_expanded_layout = cute.append(mRstd.layout, cute.make_layout((self.N,), stride=(0,)))
        mRstd = cute.make_tensor(mRstd.iterator, mRstd_expanded_layout)

        num_blocks = (
            sm_count if tiler_mn[0] == 1 else min(sm_count, cute.ceil_div(1024, tiler_mn[0]))
        )

        self.kernel(mX, mW, mDout, mRstd, mDx, mDw, sm_count, tv_layout, tiler_mn).launch(
            grid=[num_blocks, self.cluster_n, 1],
            block=[num_threads, 1, 1],
            cluster=[1, self.cluster_n, 1] if self.cluster_n > 1 else None,
            smem=self._smem_size_in_bytes(tiler_mn, num_warps),
            stream=stream,
        )

    @cute.kernel
    def kernel(
        self,
        mX: cute.Tensor,
        mW: cute.Tensor,
        mDout: cute.Tensor,
        mRstd: cute.Tensor,
        mDx: cute.Tensor,
        mDw: cute.Tensor,
        sm_count: cutlass.Constexpr,
        tv_layout: cute.Layout,
        tiler_mn: cute.Shape,
    ):
        tidx, _, _ = cute.arch.thread_idx()
        bidx, cluster_y, _ = cute.arch.block_idx()
        gdim, _, _ = cute.arch.grid_dim()

        shape = mX.shape
        M, N = shape[0], shape[1]

        idX = cute.make_identity_tensor(shape)

        smem = cutlass.utils.SmemAllocator()
        reduction_buffer, mbar_ptr = self._allocate_reduction_buffer_and_mbar(smem, tv_layout)

        copy_atom_load_X = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mX.element_type, num_bits_per_copy=128
        )

        copy_atom_load_W = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mW.element_type, num_bits_per_copy=128
        )

        copy_atom_store_dX = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mDx.element_type, num_bits_per_copy=128
        )

        copy_atom_dw = cute.make_copy_atom(
            cute.nvgpu.CopyUniversalOp(), mDw.element_type, num_bits_per_copy=128
        )

        thr_copy_X = cute.make_tiled_copy(copy_atom_load_X, tv_layout, tiler_mn).get_slice(tidx)
        thr_copy_W = cute.make_tiled_copy(copy_atom_load_W, tv_layout, tiler_mn).get_slice(tidx)
        thr_copy_dw = cute.make_tiled_copy(copy_atom_dw, tv_layout, tiler_mn).get_slice(tidx)
        thr_store_dx = cute.make_tiled_copy(copy_atom_store_dX, tv_layout, tiler_mn).get_slice(tidx)

        gW = cute.local_tile(mW, tiler_mn, (bidx, 0 if self.cluster_n == 1 else cluster_y))
        tWgW = thr_copy_W.partition_S(gW)
        tWrW = cute.make_fragment_like(tWgW)
        tXrW = thr_copy_X.retile(tWrW)

        gW_coord = cute.local_tile(idX, tiler_mn, (0, 0 if self.cluster_n == 1 else cluster_y))

        tWpW = utils.predicate_k(thr_copy_W.partition_S(gW_coord), limit=shape[1])
        cute.copy(copy_atom_load_W, tWgW, tWrW, pred=tWpW)
        weight = tXrW.load().to(cute.Float32)

        num_warps = cute.size(tv_layout, mode=[0]) // cute.arch.WARP_SIZE

        self._initialize_cluster(tidx, mbar_ptr, num_warps)

        dw_coord = cute.local_tile(idX, tiler_mn, (0, 0 if self.cluster_n == 1 else cluster_y))
        tDwpDw = utils.predicate_k(thr_copy_dw.partition_S(dw_coord), limit=shape[1])

        gDw = cute.local_tile(mDw, tiler_mn, (bidx, 0 if self.cluster_n == 1 else cluster_y))
        tDwgDw = thr_copy_dw.partition_D(gDw)
        tDwrDw = cute.make_fragment_like(tDwgDw)
        dw_accumulator = thr_copy_X.retile(tDwrDw)
        dw_accumulator.fill(0.0)

        M_pad = ((M + sm_count - 1) // sm_count) * sm_count

        jump = sm_count if tiler_mn[0] == 1 else min(sm_count, cute.ceil_div(1024, tiler_mn[0]))

        if cutlass.const_expr(self.cluster_n > 1):
            cute.arch.cluster_arrive()
            cute.arch.cluster_wait()

        ## need to update range_dynamic since it will be deprecated soon
        for row_offset in cutlass.range_dynamic(bidx, M_pad, jump):
            gX = cute.local_tile(
                mX, tiler_mn, (row_offset, 0 if self.cluster_n == 1 else cluster_y)
            )
            gDout = cute.local_tile(
                mDout, tiler_mn, (row_offset, 0 if self.cluster_n == 1 else cluster_y)
            )
            gRstd = cute.local_tile(
                mRstd, tiler_mn, (row_offset, 0 if self.cluster_n == 1 else cluster_y)
            )
            gDx = cute.local_tile(
                mDx, tiler_mn, (row_offset, 0 if self.cluster_n == 1 else cluster_y)
            )
            cX = cute.local_tile(
                idX, tiler_mn, (row_offset, 0 if self.cluster_n == 1 else cluster_y)
            )

            tXgX = thr_copy_X.partition_S(gX)
            thrDout = thr_copy_X.partition_S(gDout)
            tXrRstd = thr_copy_W.partition_S(gRstd)
            thrDx = thr_store_dx.partition_D(gDx)
            tXcX = thr_copy_X.partition_S(cX)[(0, None), None, None]

            tXrX, frgDout, frgDx = [cute.make_fragment_like(thr) for thr in (tXgX, thrDout, thrDx)]

            tXpX = utils.predicate_k(thr_copy_X.partition_S(cX), limit=shape[1])

            if tXcX[0][0] < shape[0]:
                cute.copy(copy_atom_load_X, tXgX, tXrX, pred=tXpX)
                cute.copy(copy_atom_load_X, thrDout, frgDout, pred=tXpX)

            x = tXrX.load().to(cute.Float32)
            dout = frgDout.load().to(cute.Float32)

            rstd = tXrRstd[0]
            x_hat = x * rstd
            wdy = dout * weight

            threads_per_row = tv_layout.shape[0][0]

            row = tXcX[0][0]
            if cutlass.const_expr(self.cluster_n > 1):
                cute.arch.cluster_arrive()
                cute.arch.cluster_wait()
            else:
                cute.arch.barrier()

            mean_xhat_wdy = (
                utils.row_reduce(
                    x_hat * wdy,
                    cute.ReductionOp.ADD,
                    threads_per_row,
                    reduction_buffer[None, None, 0],
                    mbar_ptr + 0 if cutlass.const_expr(self.cluster_n > 1) else None,
                    init_val=0.0,
                    hook_fn=cute.arch.cluster_wait
                    if cutlass.const_expr(self.cluster_n > 1)
                    else None,
                )
                / shape[1]
            )

            dx = (wdy - x_hat * mean_xhat_wdy) * rstd
            frgDx.store(dx.to(frgDout.element_type))

            if row < M:
                cute.copy(copy_atom_store_dX, frgDx, thrDx, pred=tXpX)

            if cutlass.const_expr(self.cluster_n > 1):
                cute.arch.cluster_arrive()
                cute.arch.cluster_wait()
            else:
                cute.arch.barrier()

            if row < M:
                dw_row = dout * x_hat
                current_dw = dw_accumulator.load().to(cute.Float32)
                updated_dw = current_dw + dw_row
                dw_accumulator.store(updated_dw.to(dw_accumulator.element_type))

            """ 
            if cutlass.const_expr(self.cluster_n > 1):
                cute.arch.cluster_arrive()
                cute.arch.cluster_wait()
            else:
                cute.arch.barrier()
            """
        """ 
        if cutlass.const_expr(self.cluster_n > 1):
            cute.arch.cluster_arrive()
            cute.arch.cluster_wait()
        else:
            cute.arch.barrier()
        """

        cute.autovec_copy(dw_accumulator, tDwrDw)
        cute.copy(copy_atom_dw, tDwrDw, tDwgDw, pred=tDwpDw)


def _rmsnorm_backward(
    x: torch.Tensor,
    weight: torch.Tensor,
    dout: torch.Tensor,
    rstd: torch.Tensor,
) -> (torch.Tensor, torch.Tensor):
    """RMSNorm backward pass.
    Args:
        x: Input tensor of shape (M, N)
        weight: Weight tensor of shape (N,)
        dout: Upstream gradients tensor of shape (M, N)
        rstd: Reciprocal standard deviation tensor of shape (M,)
    Returns:
        Tuple of (dx, dw) where:
        - dx: Input gradients tensor of same shape as x
        - dw: Weight gradients tensor of same shape as weight
    """
    assert x.dim() == 2, "Input must be 2D"
    assert weight.dim() == 1, "Weight must be 1D"
    assert x.shape[-1] == weight.shape[0], "Last dimension of input must match weight dimension"
    assert x.is_cuda and weight.is_cuda, "Tensors must be on CUDA device"
    assert x.dtype in [torch.float16, torch.bfloat16, torch.float32], "Unsupported dtype"
    assert weight.dtype == torch.float32, "Weight must be float32"

    M, N = x.shape
    dx = torch.empty_like(x)

    device = x.device

    sm_count = torch.cuda.get_device_properties(device).multi_processor_count * 8
    dw_partial = torch.zeros((sm_count, N), device=device, dtype=weight.dtype)

    dtype = torch2cute_dtype_map[x.dtype]

    convert_from_dlpack = lambda tensor: (
        from_dlpack(tensor.detach(), assumed_align=16).mark_compact_shape_dynamic(
            mode=0, stride_order=(0, 1)
        )
    )

    x_tensor, dout_tensor, dx_tensor = [convert_from_dlpack(tensor) for tensor in (x, dout, dx)]

    weight_tensor = utils.convert_from_dlpack(
        weight.detach(), leading_dim=0, divisibility=128 // cutlass.Float32.width
    )

    dw_partial_tensor = convert_from_dlpack(dw_partial)
    rstd_tensor = from_dlpack(rstd.detach(), assumed_align=4).mark_layout_dynamic(leading_dim=0)

    current_stream = cuda.CUstream(torch.cuda.current_stream().cuda_stream)

    compile_key = (dtype, N)
    if compile_key not in _rmsnorm_backward.compile_cache:
        rmsnorm_backward_op = RMSNormBackward(dtype, N)
        _rmsnorm_backward.compile_cache[compile_key] = cute.compile(
            rmsnorm_backward_op,
            x_tensor,
            weight_tensor,
            dout_tensor,
            rstd_tensor,
            dx_tensor,
            dw_partial_tensor,
            sm_count,
            current_stream,
        )

    _rmsnorm_backward.compile_cache[compile_key](
        x_tensor,
        weight_tensor,
        dout_tensor,
        rstd_tensor,
        dx_tensor,
        dw_partial_tensor,
        current_stream,
    )

    dw = dw_partial.sum(dim=0).to(weight.dtype)
    return dx, dw


_rmsnorm_backward.compile_cache = {}


class RMSNormFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, weight, eps):
        out, rstd = _rmsnorm_fwd(x, weight, eps, return_rstd=True)
        ctx.save_for_backward(x, weight, rstd)
        ctx.eps = eps
        return out

    @staticmethod
    def backward(ctx, dout):
        x, weight, rstd = ctx.saved_tensors
        dx, dw = _rmsnorm_backward(x, weight, dout, rstd)
        # dw is returned for weight gradient, None for eps gradient
        return dx, dw, None


def rmsnorm(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """RMSNorm forward pass with automatic differentiation support.

    Args:
        x: Input tensor of shape (M, N)
        weight: Weight tensor of shape (N,)
        eps: Small value for numerical stability

    Returns:
        Normalized output tensor of same shape as x
    """
    return RMSNormFunction.apply(x, weight, eps)

from __future__ import annotations

from functools import partial

import math
from math import ceil

import torch
from torch import Tensor, arange
import torch.nn.functional as F

from einops import repeat, rearrange, reduce

# taken from appendix B https://arxiv.org/abs/2507.02754

import triton
import triton.language as tl
from triton.language.extra import libdevice

@triton.autotune (
    configs=[
        triton.Config(
            {"BLOCK_SIZE_Q": 64, "BLOCK_SIZE_KV": 32, "HEAD_DIM": 64},
            num_stages=1,
            num_warps=4,
        ),
    ],
    key=["HEAD_DIM"],
)
@triton.jit
def two_simplicial_attn_fwd_kernel(
    Q_ptr,  # [b, s, k, h]
    K1_ptr,  # [b, s, k, h]
    K2_ptr,  # [b, s, k, h]
    V1_ptr,  # [b, s, k, h]
    V2_ptr,  # [b, s, k, h]
    O_ptr,  # [b, s, k, h]
    M_ptr,  # [b, k, s]
    bs,
    seq_len,
    num_heads,
    head_dim,
    w1: tl.constexpr,
    w2: tl.constexpr,
    q_stride_b,
    q_stride_s,
    q_stride_k,
    q_stride_h,
    k1_stride_b,
    k1_stride_s,
    k1_stride_k,
    k1_stride_h,
    k2_stride_b,
    k2_stride_s,
    k2_stride_k,
    k2_stride_h,
    v1_stride_b,
    v1_stride_s,
    v1_stride_k,
    v1_stride_h,
    v2_stride_b,
    v2_stride_s,
    v2_stride_k,
    v2_stride_h,
    out_stride_b,
    out_stride_s,
    out_stride_k,
    out_stride_h,
    m_stride_b,
    m_stride_k,
    m_stride_s,
    BLOCK_SIZE_Q: tl.constexpr,
    BLOCK_SIZE_KV: tl.constexpr,
    HEAD_DIM: tl.constexpr,
    INPUT_PRECISION: tl.constexpr,
    SM_SCALE: tl.constexpr,
    K2_BIAS: tl.constexpr,
    V2_BIAS: tl.constexpr,
    num_stages: tl.constexpr,
):
    data_dtype = tl.bfloat16
    compute_dtype = tl.float32
    gemm_dtype = tl.bfloat16

    q_start = tl.program_id(0) * BLOCK_SIZE_Q
    q_end = q_start + BLOCK_SIZE_Q
    bk = tl.program_id(1)

    offs_b = bk // num_heads
    offs_k = bk % num_heads

    qkv_offs_bk = offs_b * q_stride_b + offs_k * q_stride_k

    Q_ptr += qkv_offs_bk
    K1_ptr += qkv_offs_bk
    K2_ptr += qkv_offs_bk
    V1_ptr += qkv_offs_bk
    V2_ptr += qkv_offs_bk
    O_ptr += qkv_offs_bk
    M_ptr += offs_b * m_stride_b + offs_k * m_stride_k

    m_i = tl.zeros((BLOCK_SIZE_Q,), dtype=compute_dtype) - float("inf")
    l_i = tl.zeros((BLOCK_SIZE_Q,), dtype=compute_dtype)
    acc = tl.zeros((BLOCK_SIZE_Q, HEAD_DIM), dtype=compute_dtype)

    q_offs_s = q_start + tl.arange(0, BLOCK_SIZE_Q)
    qkv_offs_h = tl.arange(0, HEAD_DIM)

    q_mask_s = q_offs_s < seq_len
    qkv_mask_h = qkv_offs_h < head_dim

    q_offs = q_offs_s[:, None] * q_stride_s + qkv_offs_h[None, :] * q_stride_h
    q_mask = q_mask_s[:, None] & (qkv_mask_h[None, :])

    q_tile = tl.load(Q_ptr + q_offs, mask=q_mask).to(compute_dtype)  # [BLOCK_SIZE_Q, HEAD_DIM]

    softmax_scale = tl.cast(SM_SCALE, gemm_dtype)

    for kv1_idx in tl.range(tl.maximum(0, q_start - w1), tl.minimum(seq_len, q_end)):
        k1_offs = kv1_idx * k1_stride_s + qkv_offs_h * k1_stride_h
        k1_tile = (tl.load(K1_ptr + k1_offs, mask=qkv_mask_h).to(compute_dtype))[None, :]  # [1, HEAD_DIM]
        qk1 = q_tile * k1_tile  # [BLOCK_SIZE_Q, HEAD_DIM]
        qk1 = qk1.to(gemm_dtype)

        v1_offs = kv1_idx * v1_stride_s + qkv_offs_h * v1_stride_h
        v1_tile = (tl.load(V1_ptr + v1_offs, mask=qkv_mask_h).to(compute_dtype))[None, :]  # [1, HEAD_DIM]

        for kv2_idx in tl.range(
            tl.maximum(0, q_start - w2),
            tl.minimum(seq_len, q_end),
            BLOCK_SIZE_KV,
            num_stages=num_stages,
        ):
            kv2_offs_s = kv2_idx + tl.arange(0, BLOCK_SIZE_KV)
            kv2_mask_s = kv2_offs_s < seq_len

            k2t_mask = kv2_mask_s[None, :] & qkv_mask_h[:, None]
            v2_mask = kv2_mask_s[:, None] & qkv_mask_h[None, :]

            k2_offs = (kv2_offs_s[None, :] * k2_stride_s + qkv_offs_h[:, None] * k2_stride_h)
            v2_offs = kv2_offs_s[:, None] * v2_stride_s + qkv_offs_h[None, :] * v2_stride_h

            k2t_tile = tl.load(K2_ptr + k2_offs, mask=k2t_mask).to(compute_dtype)  # [HEAD_DIM, BLOCK_SIZE_KV]
            v2_tile = tl.load(V2_ptr + v2_offs, mask=v2_mask).to(compute_dtype)  # [BLOCK_SIZE_KV, HEAD_DIM]

            k2t_tile += K2_BIAS
            v2_tile += V2_BIAS

            k2t_tile = k2t_tile.to(gemm_dtype)
            v2_tile = v2_tile.to(compute_dtype)

            qk = tl.dot(
                qk1 * softmax_scale,
                k2t_tile,
                input_precision="132",  # INPUT_PRECISION,
                out_dtype=tl.float32,
            )  # [BLOCK_SIZE_Q, BLOCK_SIZE_KV]

            qk_mask = q_mask_s[:, None] & kv2_mask_s[None, :]

            # Mask for q_idx - w1 < kv1_idx <= q_idx and q_idx - w2 < kv2_offs_s <= q_idx
            kv1_local_mask = ((q_offs_s[:, None] - w1) < kv1_idx) & (kv1_idx <= q_offs_s[:, None])
            kv2_local_mask = ((q_offs_s[:, None] - w2) < kv2_offs_s[None, :]) & (kv2_offs_s[None, :] < q_offs_s[:, None])
            qk_mask &= kv1_local_mask & kv2_local_mask

            qk += tl.where(qk_mask, 0, -1.0e38)

            m_ij = tl.maximum(m_i, tl.max(qk, 1))
            p = tl.math.exp(qk - m_ij[:, None])
            l_ij = tl.sum(p, 1)

            alpha = tl.math.exp(m_i - m_ij)
            l_i = alpha * l_i + l_ij

            acc *= alpha[:, None]

            v12_tile = v1_tile * v2_tile  # [BLOCK_SIZE_KV, HEAD_DIM]
            acc += tl.dot(
                p.to(gemm_dtype),
                v12_tile.to(gemm_dtype),
                input_precision="leee",  # INPUT_PRECISION,
                out_dtype=tl.float32,
            )

            m_i = m_ij

    acc /= l_i[:, None]
    acc = tl.where(q_mask, acc, 0.0)
    acc = acc.to(data_dtype)

    out_offs = q_offs_s[:, None] * out_stride_s + qkv_offs_h[None, :] * out_stride_h
    tl.store(O_ptr + out_offs, acc, mask=q_mask)

    m = m_i + tl.log(l_i)
    m_offs = q_offs_s * m_stride_s
    m_mask = q_offs_s < seq_len
    tl.store(M_ptr + m_offs, m, mask=m_mask)

@triton.jit
def two_simplicial_attn_bwd_kv1_kernel(
    Q_ptr,  # [b, s, k, h]
    K1_ptr,  # [b, s, k, h]
    K2_ptr,  # [b, s, k, h]
    V1_ptr,  # [b, s, k, h]
    V2_ptr,  # [b, s, k, h]
    do_ptr,  # [b, s, k, h]
    M_ptr,  # [b, k, s]
    D_ptr,  # [b, k, s]
    dQ_ptr,  # [b, s, k, h]
    dK1_ptr,  # [b, s, k, h]
    dV1_ptr,  # [b, s, k, h]
    # Skip writing dk2, dv2 for now.
    bs,
    seq_len,
    num_heads,
    head_dim,
    w1,  # Q[i]: KV1(i-w1, i]
    w2,  # Q[i]: KV2(i-w2, i]
    q_stride_b,
    q_stride_s,
    q_stride_k,
    q_stride_h,
    k1_stride_b,
    k1_stride_s,
    k1_stride_k,
    k1_stride_h,
    k2_stride_b,
    k2_stride_s,
    k2_stride_k,
    k2_stride_h,
    v1_stride_b,
    v1_stride_s,
    v1_stride_k,
    v1_stride_h,
    v2_stride_b,
    v2_stride_s,
    v2_stride_k,
    v2_stride_h,
    do_stride_b,
    do_stride_s,
    do_stride_k,
    do_stride_h,
    m_stride_b,
    m_stride_k,
    m_stride_s,
    d_stride_b,
    d_stride_k,
    d_stride_s,
    dq_stride_b,
    dq_stride_s,
    dq_stride_k,
    dq_stride_h,
    dk1_stride_b,
    dk1_stride_s,
    dk1_stride_k,
    dk1_stride_h,
    dv1_stride_b,
    dv1_stride_s,
    dv1_stride_k,
    dv1_stride_h,
    BLOCK_SIZE_Q: tl.constexpr,
    BLOCK_SIZE_KV: tl.constexpr,
    HEAD_DIM: tl.constexpr,
    SM_SCALE: tl.constexpr,
    K2_BIAS: tl.constexpr,
    V2_BIAS: tl.constexpr,
    COMPUTE_DQ: tl.constexpr,
    num_stages: tl.constexpr,
    is_flipped: tl.constexpr,
):
    data_dtype = tl.bfloat16
    compute_dtype = tl.float32
    gemm_dtype = tl.bfloat16

    kv1_start = tl.program_id(0) * BLOCK_SIZE_KV
    kv1_end = kv1_start + BLOCK_SIZE_KV
    bk = tl.program_id(1)

    offs_b = bk // num_heads
    offs_k = bk % num_heads

    qkv_offs_bk = offs_b * q_stride_b + offs_k * q_stride_k

    Q_ptr += qkv_offs_bk
    K1_ptr += qkv_offs_bk
    K2_ptr += qkv_offs_bk
    V1_ptr += qkv_offs_bk
    V2_ptr += qkv_offs_bk

    do_ptr += offs_b * do_stride_b + offs_k * do_stride_k
    M_ptr += offs_b * m_stride_b + offs_k * m_stride_k
    D_ptr += offs_b * d_stride_b + offs_k * d_stride_k
    dK1_ptr += offs_b * dk1_stride_b + offs_k * dk1_stride_k
    dV1_ptr += offs_b * dv1_stride_b + offs_k * dv1_stride_k
    if COMPUTE_DQ:
        dQ_ptr += offs_b * dq_stride_b + offs_k * dq_stride_k

    softmax_scale = tl.cast(SM_SCALE, gemm_dtype)

    qkv_offs_h = tl.arange(0, HEAD_DIM)
    qkv_mask_h = qkv_offs_h < head_dim

    kv1_offs_s = kv1_start + tl.arange(0, BLOCK_SIZE_KV)
    k1_offs = kv1_offs_s[:, None] * k1_stride_s + qkv_offs_h[None, :] * k1_stride_h
    kv1_mask_s = kv1_offs_s < seq_len
    kv1_mask = kv1_mask_s[:, None] & qkv_mask_h[None, :]
    k1_tile = tl.load(K1_ptr + k1_offs, mask=kv1_mask).to(compute_dtype)  # [BLOCK_SIZE_KV, HEAD_DIM]

    v1_offs = kv1_offs_s[:, None] * v1_stride_s + qkv_offs_h[None, :] * v1_stride_h
    v1_tile = tl.load(V1_ptr + v1_offs, mask=kv1_mask).to(compute_dtype)  # [BLOCK_SIZE_KV, HEAD_DIM]

    if is_flipped:
        k1_tile += K2_BIAS
        v1_tile += V2_BIAS

    dv1 = tl.zeros((BLOCK_SIZE_KV, HEAD_DIM), compute_dtype)
    dk1 = tl.zeros((BLOCK_SIZE_KV, HEAD_DIM), compute_dtype)

    for kv2_idx in tl.range(
        tl.maximum(0, kv1_start - w2), tl.minimum(seq_len, kv1_end + w1)
    ):
        k2_offs = kv2_idx * k2_stride_s + qkv_offs_h * k2_stride_h
        k2_tile = (tl.load(K2_ptr + k2_offs, mask=qkv_mask_h).to(compute_dtype))[None, :]  # [1, HEAD_DIM]

        v2_offs = kv2_idx * v2_stride_s + qkv_offs_h * v2_stride_h
        v2_tile = (tl.load(V2_ptr + v2_offs, mask=qkv_mask_h).to(compute_dtype))[None, :]  # [1, HEAD_DIM]

        if not is_flipped:
            k2_tile += K2_BIAS
            v2_tile += V2_BIAS

        k1k2 = k1_tile * k2_tile  # [BLOCK_SIZE_KV, HEAD_DIM]
        v1v2 = v1_tile * v2_tile  # [BLOCK_SIZE_KV, HEAD_DIM]

        k1k2 = k1k2.to(gemm_dtype)
        v1v2 = v1v2.to(gemm_dtype)

        q_start = tl.maximum(kv1_start, kv2_idx)
        q_end = tl.minimum(seq_len, tl.minimum(kv1_end + w1, kv2_idx + w2))

        for q_idx in tl.range(q_start, q_end, BLOCK_SIZE_Q):
            # Load qt, m, d, do
            q_offs_s = q_idx + tl.arange(0, BLOCK_SIZE_Q)
            q_offs = q_offs_s[None, :] * q_stride_s + qkv_offs_h[:, None] * q_stride_h
            q_mask_s = q_offs_s < seq_len
            qt_mask = q_mask_s[None, :] & qkv_mask_h[:, None]
            qt_tile = tl.load(Q_ptr + q_offs, mask=qt_mask).to(gemm_dtype)  # [HEAD_DIM, BLOCK_SIZE_Q]

            m_offs = q_offs_s * m_stride_s
            m_tile = tl.load(M_ptr + m_offs, mask=q_mask_s).to(compute_dtype)[None, :]  # [1, BLOCK_SIZE_Q]

            d_offs = q_offs_s * d_stride_s
            d_tile = tl.load(D_ptr + d_offs, mask=q_mask_s).to(compute_dtype)[None, :]  # [1, BLOCK_SIZE_Q]

            do_offs = (q_offs_s[:, None] * do_stride_s + qkv_offs_h[None, :] * do_stride_h)
            do_tile = tl.load(
                do_ptr + do_offs, mask=q_mask_s[:, None] & qkv_mask_h[None, :]
            ).to(compute_dtype)  # [BLOCK_SIZE_Q, HEAD_DIM]

            if COMPUTE_DQ:
                dq = tl.zeros((BLOCK_SIZE_Q, HEAD_DIM), tl.float32)

            qkkT = tl.dot(k1k2, qt_tile) * softmax_scale  # [BLOCK_SIZE_KV, BLOCK_SIZE_Q]

            # Mask qkkt to inf
            kv1_local_mask = ((q_offs_s[None, :] - w1) < kv1_offs_s[:, None]) & (kv1_offs_s[:, None] <= q_offs_s[None, :])
            kv2_local_mask = ((q_offs_s - w2) < kv2_idx) & (kv2_idx <= q_offs_s)
            local_mask = kv1_local_mask & kv2_local_mask[None, :]  # [BLOCK_SIZE_KV, BLOCK_SIZE_Q]

            qkkT = tl.where(local_mask, qkkT, -1.0e38)

            pT = tl.exp(qkkT - m_tile)  # [BLOCK_SIZE_KV, BLOCK_SIZE_Q]
            pT = tl.where(local_mask, pT, 0.0)

            do_v2 = do_tile * v2_tile  # [BLOCK_SIZE_Q, HEAD_DIM]
            dv1 += tl.dot(pT.to(gemm_dtype), do_v2.to(gemm_dtype), out_dtype=tl.float32)  # [BLOCK_SIZE_KV, HEAD_DIM]

            dpT = tl.dot(v1v2, tl.trans(do_tile.to(gemm_dtype)), out_dtype=tl.float32)  # [BLOCK_SIZE_KV, BLOCK_SIZE_Q]
            dsT = pT * (dpT - d_tile)  # [BLOCK_SIZE_KV, BLOCK_SIZE_Q]
            dsT = tl.where(local_mask, dsT, 0.0) * softmax_scale

            dk1 += (tl.dot(dsT.to(gemm_dtype), tl.trans(qt_tile), out_dtype=tl.float32) * k2_tile.to(tl.float32))

            if COMPUTE_DQ:
                dsT = dsT.to(gemm_dtype)
                dq += (tl.dot(tl.trans(dsT), k1k2, out_dtype=tl.float32) * softmax_scale)  # [BLOCK_SIZE_Q, HEAD_DIM]

                dq_offs = (q_offs_s[:, None] * dq_stride_s + qkv_offs_h[None, :] * dq_stride_h)
                tl.atomic_add(
                    dQ_ptr + dq_offs, dq, mask=q_mask_s[:, None] & qkv_mask_h[None, :]
                )

    dv1_offs = kv1_offs_s[:, None] * dv1_stride_s + qkv_offs_h[None, :] * dv1_stride_h
    dk1_offs = kv1_offs_s[:, None] * dk1_stride_s + qkv_offs_h[None, :] * dk1_stride_h
    tl.store(dV1_ptr + dv1_offs, dv1.to(data_dtype), mask=kv1_mask)
    tl.store(dK1_ptr + dk1_offs, dk1.to(data_dtype), mask=kv1_mask)

@triton.autotune(
    configs=[
        triton.Config(
            {"BLOCK_SIZE_Q": 32, "BLOCK_SIZE_KV2": 64, "HEAD_DIM": 64},
            num_stages=1,
            num_warps=4,
        ),
    ],
    key=["HEAD_DIM"],
)
@triton.jit
def two_simplicial_attn_bwd_kv2q_kernel(
    Q_ptr,  # [b, s, k, h]
    K1_ptr,  # [b, s, k, h]
    K2_ptr,  # [b, s, k, h]
    V1_ptr,  # [b, s, k, h]
    V2_ptr,  # [b, s, k, h]
    do_ptr,  # [b, s, k, h]
    M_ptr,  # [b, k, s]
    D_ptr,  # [b, k, s]
    dQ_ptr,  # [b, s, k, h]
    dK2_ptr,  # [b, s, k, h]
    dV2_ptr,  # [b, s, k, h]
    bs,
    seq_len,
    num_heads,
    head_dim,
    w1,  # Q[i]: KV1(i-w1, i]
    w2,  # Q[i]: KV2(i-w2, i]
    q_stride_b,
    q_stride_s,
    q_stride_k,
    q_stride_h,
    k1_stride_b,
    k1_stride_s,
    k1_stride_k,
    k1_stride_h,
    k2_stride_b,
    k2_stride_s,
    k2_stride_k,
    k2_stride_h,
    v1_stride_b,
    v1_stride_s,
    v1_stride_k,
    v1_stride_h,
    v2_stride_b,
    v2_stride_s,
    v2_stride_k,
    v2_stride_h,
    do_stride_b,
    do_stride_s,
    do_stride_k,
    do_stride_h,
    m_stride_b,
    m_stride_k,
    m_stride_s,
    d_stride_b,
    d_stride_k,
    d_stride_s,
    dq_stride_b,
    dq_stride_s,
    dq_stride_k,
    dq_stride_h,
    dk2_stride_b,
    dk2_stride_s,
    dk2_stride_k,
    dk2_stride_h,
    dv2_stride_b,
    dv2_stride_s,
    dv2_stride_k,
    dv2_stride_h,
    BLOCK_SIZE_Q: tl.constexpr,
    BLOCK_SIZE_KV2: tl.constexpr,
    HEAD_DIM: tl.constexpr,
    SM_SCALE: tl.constexpr,
    K2_BIAS: tl.constexpr,
    V2_BIAS: tl.constexpr,
    num_stages: tl.constexpr,
    IS_SECOND_PASS: tl.constexpr,
):
    assert BLOCK_SIZE_KV2 >= BLOCK_SIZE_Q + w2
    data_dtype = tl.bfloat16
    compute_dtype = tl.float32
    gemm_dtype = tl.bfloat16

    # First pass does even tiles, second pass does odd tiles.
    q_start = tl.program_id(0) * BLOCK_SIZE_KV2
    if IS_SECOND_PASS:
        q_start += BLOCK_SIZE_Q
    q_end = q_start + BLOCK_SIZE_Q
    kv2_start = q_start - w2

    bk = tl.program_id(1)
    offs_b = bk // num_heads
    offs_k = bk % num_heads

    qkv_offs_bk = offs_b * q_stride_b + offs_k * q_stride_k

    Q_ptr += qkv_offs_bk
    K1_ptr += qkv_offs_bk
    K2_ptr += qkv_offs_bk
    V1_ptr += qkv_offs_bk
    V2_ptr += qkv_offs_bk

    do_ptr += offs_b * do_stride_b + offs_k * do_stride_k
    M_ptr += offs_b * m_stride_b + offs_k * m_stride_k
    D_ptr += offs_b * d_stride_b + offs_k * d_stride_k
    dQ_ptr += offs_b * dq_stride_b + offs_k * dq_stride_k
    dK2_ptr += offs_b * dk2_stride_b + offs_k * dk2_stride_k
    dV2_ptr += offs_b * dv2_stride_b + offs_k * dv2_stride_k

    softmax_scale = tl.cast(SM_SCALE, gemm_dtype)
    qkv_offs_h = tl.arange(0, HEAD_DIM)
    qkv_mask_h = qkv_offs_h < head_dim

    q_offs_s = q_start + tl.arange(0, BLOCK_SIZE_Q)
    kv2_offs_s = kv2_start + tl.arange(0, BLOCK_SIZE_KV2)
    q_offs = q_offs_s[:, None] * q_stride_s + qkv_offs_h[None, :] * q_stride_h
    kv2_offs = kv2_offs_s[:, None] * k2_stride_s + qkv_offs_h[None, :] * k2_stride_h

    m_offs = q_offs_s * m_stride_s
    d_offs = q_offs_s * d_stride_s
    do_offs = q_offs_s[:, None] * do_stride_s + qkv_offs_h[None, :] * do_stride_h

    q_mask_s = q_offs_s < seq_len
    q_mask = q_mask_s[:, None] & qkv_mask_h[None, :]
    kv2_mask_s = (0 <= kv2_offs_s) & (kv2_offs_s < seq_len)
    kv2_mask = kv2_mask_s[:, None] & qkv_mask_h[None, :]

    q_tile = tl.load(Q_ptr + q_offs, mask=q_mask).to(compute_dtype)  # [BLOCK_SIZE_Q, HEAD_DIM]
    k2_tile = tl.load(K2_ptr + kv2_offs, mask=kv2_mask).to(gemm_dtype)  # [KV2, HEAD_DIM]
    v2_tile = tl.load(V2_ptr + kv2_offs, mask=kv2_mask).to(gemm_dtype)  # [KV2, HEAD_DIM]
    m_tile = tl.load(M_ptr + m_offs, mask=q_mask_s).to(compute_dtype)  # [BLOCK_SIZE_Q]
    d_tile = tl.load(D_ptr + d_offs, mask=q_mask_s).to(compute_dtype)  # [BLOCK_SIZE_Q]
    do_tile = tl.load(do_ptr + do_offs, mask=q_mask).to(gemm_dtype)  # [BLOCK_SIZE_Q, HEAD_DIM]

    # Apply KV2 norm.
    k2_tile += K2_BIAS
    v2_tile += V2_BIAS
    k2_tile = k2_tile.to(gemm_dtype)
    v2_tile = v2_tile.to(gemm_dtype)

    dq = tl.zeros((BLOCK_SIZE_Q, HEAD_DIM), tl.float32)
    dk2 = tl.zeros((BLOCK_SIZE_KV2, HEAD_DIM), tl.float32)
    dv2 = tl.zeros((BLOCK_SIZE_KV2, HEAD_DIM), tl.float32)

    kv1_start = tl.maximum(0, q_start - w1)
    kv1_end = tl.minimum(seq_len, q_end)

    for kv1_idx in tl.range(kv1_start, kv1_end, num_stages=num_stages):
        k1_offs = kv1_idx * k1_stride_s + qkv_offs_h * k1_stride_h
        v1_offs = kv1_idx * v1_stride_s + qkv_offs_h * v1_stride_h

        k1_tile = tl.load(K1_ptr + k1_offs, mask=qkv_mask_h).to(compute_dtype)  # [HEAD_DIM]
        v1_tile = tl.load(V1_ptr + v1_offs, mask=qkv_mask_h).to(compute_dtype)  # [HEAD_DIM]

        qk1_s = q_tile * (k1_tile[None, :] * softmax_scale)  # [Q, D]
        qk1_s = qk1_s.to(gemm_dtype)

        qkkT = tl.dot(k2_tile, qk1_s.T, out_dtype=tl.float32)  # [KV2, Q]
        qkT_mask = kv2_mask_s[:, None] & q_mask_s[None, :]  # [KV2, Q]

        kv1_local_mask = ((q_offs_s[None, :] - w1) < kv1_idx) & (kv1_idx <= q_offs_s[None, :])  # [KV2, Q]
        kv2_local_mask = ((q_offs_s[None, :] - w2) < kv2_offs_s[:, None]) & (kv2_offs_s[:, None] < q_offs_s[None, :])  # [KV2, Q]
        local_mask = qkT_mask & kv1_local_mask & kv2_local_mask  # [KV2, Q]

        qkkT = tl.where(local_mask, qkkT, -1.0e38)
        pT = tl.exp(qkkT - m_tile[None, :])  # [KV2, Q]
        pT = tl.where(qkT_mask, pT, 0.0)

        do_v1 = do_tile * v1_tile[None, :]  # [Q, D]
        do_v1 = do_v1.to(gemm_dtype)
        # pT[KV2, Q] @ do_v1[Q, D] => [KV2, D]
        dv2 += tl.dot(pT.to(gemm_dtype), do_v1, out_dtype=tl.float32)

        # v2[KV2, D] @ do_v1.T[D, Q] => dpT[KV2, Q]
        dpT = tl.dot(v2_tile, do_v1.T, out_dtype=tl.float32)
        dsT = pT * (dpT - d_tile[None, :])  # [KV2, Q]
        dsT = tl.where(qkT_mask, dsT, 0.0)
        dsT = dsT.to(gemm_dtype)

        # dsT[KV2, Q] @ qk1_s[Q, D] => dk2[KV2, D]
        dk2 += tl.dot(dsT, qk1_s, out_dtype=tl.float32)

        k1k2 = k1_tile[None, :] * k2_tile  # [KV2, D]
        k1k2 = k1k2.to(gemm_dtype)
        dq += tl.dot(dsT.T, k1k2) # softmax_scale at the end

    # End update derivatives
    if IS_SECOND_PASS:
        # load, add
        prev_dk2 = tl.load(dK2_ptr + kv2_offs, kv2_mask)
        prev_dv2 = tl.load(dV2_ptr + kv2_offs, kv2_mask)
        dk2 += prev_dk2
        dv2 += prev_dv2

    dq *= softmax_scale
    tl.store(dK2_ptr + kv2_offs, dk2, kv2_mask)
    tl.store(dV2_ptr + kv2_offs, dv2, kv2_mask)
    tl.store(dQ_ptr + q_offs, dq, q_mask)

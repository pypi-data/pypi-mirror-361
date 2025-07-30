"""
Functional module:

Contains the functional implementation of masked normalization
"""

from __future__ import annotations

from torch import Tensor

from .validation import validate_masked_norm
from .validation import validate_affine_masked_norm
from .util import batchwise_mul, batchwise_add


def masked_norm(
    inpt: Tensor,
    mask: Tensor | None = None,
) -> Tensor:
    """
    Masked normalization procedure

    Normalizes only elements of the input specified by the mask; if no mask is
    passed to the routine, normalization is performed across the first axis
    If either by chance or design a collection of samples yields null
    variance, the normalization over such collection is ignored, and the
    values are passed along unaltered
    """

    out = validate_masked_norm(inpt, mask)

    clone = inpt.clone()

    dim = out.dim()
    reduce = tuple(range(1, dim))

    mean = out.mean(dim=reduce, keepdim=True)
    var = out.var(dim=reduce, keepdim=True)

    var_mask = (var != 0.0).flatten()

    out = (out[var_mask] - mean[var_mask]) / var[var_mask].sqrt()

    if mask is None:
        clone[var_mask] = out
    else:
        tmp = clone[mask].clone()
        tmp[var_mask] = out
        clone[mask] = tmp

    return clone


def affine_masked_norm(
    inpt: Tensor,
    mask: Tensor | None,
    weight: Tensor,
    bias: Tensor | None,
) -> Tensor:
    """
    Affine masked normalization procedure

    Normalizes only elements of the input specified by the mask; if no mask is
    passed to the routine, normalization is performed across the first axis
    If either by chance or design a collection of samples yields null
    variance, the normalization over such collection is ignored, and the
    values are passed along unaltered

    After normalization an affine transformation is performed along the
    normalized dimensions
    """

    out, weight, bias = validate_affine_masked_norm(inpt, mask, weight, bias)

    clone = inpt.clone()

    dim = out.dim()
    reduce = tuple(range(1, dim))

    mean = out.mean(dim=reduce, keepdim=True)
    var = out.var(dim=reduce, keepdim=True)

    var_mask = (var != 0.0).flatten()

    out = (out[var_mask] - mean[var_mask]) / var[var_mask].sqrt()

    out = batchwise_mul(weight[var_mask], out)

    if not bias is None:
        out = batchwise_add(bias[var_mask], out)

    if mask is None:
        clone[var_mask] = out
    else:
        tmp = clone[mask].clone()
        tmp[var_mask] = out
        clone[mask] = tmp

    return clone

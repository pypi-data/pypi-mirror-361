"""
Validation module:

Contains routines that validate inputs for both the masked_norm and
affine_masked_norm procedures

The routines presented in this module make no effort in validating the input
objects types. Code is type annotated, which doesn't replace proper
validation at runtime.
"""

from __future__ import annotations

from torch import Tensor, Size
from torch import float32, float64, float16, bfloat16
from torch import float8_e4m3fn, float8_e5m2
from torch import bool as bool_dtype


# PyTorch doesn't offer abstract type hinting for xfloat* dtypes
# you can work around this by verifying membership on a set of xfloat* dtypes
float_dtype = {
    float64,
    float32,
    float16,
    bfloat16,
    float8_e4m3fn,
    float8_e5m2
}


def validate_masked_norm(inpt: Tensor, mask: Tensor | None) -> Tensor:
    """
    Validates the input of masked_norm procedure
    Outputs are reshaped according to mask
    """

    if not inpt.dtype in float_dtype:
        raise ValueError("'inpt' must be a tensor of xfloat* dtype")

    if mask is None:

        return inpt

    if not mask.dtype == bool_dtype:
        # mask tensor must be necessarily of bool dtype
        raise ValueError("'mask' must be a tensor of bool dtype")

    if len(inpt.shape) < len(mask.shape):
        raise ValueError(
            "'mask' must have a smaller number of axes than 'inpt'"
        )

    # mask shape must partially match input shape
    for axis, ax_dim in enumerate(zip(inpt.shape, mask.shape)):
        inpt_ax_dim, mask_ax_dim = ax_dim
        if inpt_ax_dim != mask_ax_dim:
            raise ValueError(
                f"dim mismatch between 'inpt' and 'mask' on axis {axis}"
        )

    return inpt[mask]


def validate_affine_masked_norm(
    inpt: Tensor,
    mask: Tensor | None,
    weight: Tensor,
    bias: Tensor | None
) -> tuple[Tensor, Tensor, Tensor | None]:
    """
    Validates the input of the affine_masked_norm procedure
    Outputs are reshaped according to mask
    """

    shape: Size

    out = validate_masked_norm(inpt, mask)

    # weight and bias must have proper dtype
    if not weight.dtype in float_dtype:
        raise ValueError("'weight' must be a tensor of xfloat* dtype")

    if not bias is None and not bias.dtype in float_dtype:
        raise ValueError("'bias' must be a tensor of xfloat* dtype")


    if mask is None:
        # if no mask is passed, weight and bias tensor must be flat
        shape = out.shape[0: 1]

        if weight.shape != shape:
            raise ValueError(
                f"'weight' must be a flat tensor with shape {shape}"
            )

        if not bias is None and bias.shape != shape:
            raise ValueError(
                f"'bias' must be a flat tensor with shape {shape}"
            )

        return out, weight, bias

    # if a mask is passed, weight and bias must have the same shape as mask
    shape = mask.shape

    if weight.shape != shape:
        raise ValueError(
            "'weight' must have the same shape as 'mask'"
        )

    if not bias is None and bias.shape != shape:
        raise ValueError(
            "'bias' must have the same shape as 'mask'"
        )

    if bias is None:
        return out, weight[mask], bias

    return out, weight[mask], bias[mask]

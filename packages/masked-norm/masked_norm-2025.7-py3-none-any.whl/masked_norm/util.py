"""
Utilities module:

Contains simple utilities routine
"""

from torch import Tensor


def get_factory_key(key: str) -> bool:
    """
    Filtering procedure for selecting factory kwargs
    """

    if key == "device":
        return True
    if key == "dtype":
        return True
    return False


def batchwise_add(flat: Tensor, x: Tensor) -> Tensor:
    """
    """

    if flat.shape != x.shape[0: 1]:
        raise ValueError("dim mismatch on the first axis")

    for _ in x.shape[1:]:
        flat = flat[None, ...]

    flat = flat.transpose(0, -1)

    return flat + x


def batchwise_mul(flat: Tensor, x: Tensor) -> Tensor:
    """
    """

    if flat.shape != x.shape[0: 1]:

        print(flat.shape, x.shape)
        raise ValueError("dim mismatch on the first axis")

    for _ in x.shape[1:]:
        flat = flat[None, ...]

    flat = flat.transpose(0, -1)

    return flat * x

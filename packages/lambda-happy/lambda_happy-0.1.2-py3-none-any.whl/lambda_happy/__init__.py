try:
    import torch
except ImportError:
    raise ImportError(
        "torch is not installed. Please install it with the correct CUDA version: CUDA 11.8\n"
    )

from .lambda_happy import LambdaHappy
from .benchmark import LambdaBenchmark

__all__ = ["LambdaHappy", "LambdaBenchmark"]

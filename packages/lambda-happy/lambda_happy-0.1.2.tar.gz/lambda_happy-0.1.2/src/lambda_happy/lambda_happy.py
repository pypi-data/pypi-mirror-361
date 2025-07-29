import torch
from typing import List, Callable, Optional

from .lib_lambda import LambdaComputer

# Add an example with torch.manual_seed()#TODO


class LambdaHappy:
    """Compute the λ factor for solving sparse models on CPU or GPU.

    LambdaHappy estimates a scalar λ by projecting a (possibly sparse) tensor
    onto random subspaces and taking the 0.95-quantile of the ratio between
    the Chebyshev norm of XᵀZ and the l2-norm of Z. Backends include native
    C++ CUDA kernels and PyTorch routines on both CPU and GPU.

    Attributes:
        X (torch.Tensor): Input tensor to analyze.

    Examples:
        # With minimal parameters (single estimation)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1000, 10000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda = model.compute()
        >>> print(f"Estimated λ: {lambda:.4f}")

        # With all parameters (single estimation)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1000, 10000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda = model.compute(
        ...     m=10000,
        ...     version="AUTOMATIC",
        ...     dtype=torch.float16,
        ...     device_type="cpu"
        ... )
        >>> print(f"Estimated λ: {lambda:.4f}")

        # With minimal parameters (many estimations)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1000, 10000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda = model.compute_many(nb_run=100)
        >>> print(f"Estimated λs: {lambda}")

        # With all parameters (many estimations)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1000, 10000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda = model.compute_many(
        ...     m=10000,
        ...     version="AUTOMATIC",
        ...     dtype=torch.float16,
        ...     device_type="cpu",
        ...     nb_run=100
        ... )
        >>> print(f"Estimated λs: {lambda}")

        # With minimal parameters (aggregated estimation)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1000, 10000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda = model.compute_agg(nb_run=100)
        >>> print(f"Estimated λ: {lambda:.4f}")

        # With all parameters (aggregated estimation)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1000, 10000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda = model.compute_agg(
        ...     m=10000,
        ...     version="AUTOMATIC",
        ...     dtype=torch.float16,
        ...     device_type="cpu",
        ...     nb_run=100,
        ...     func=torch.mean
        ... )
        >>> print(f"Estimated λ: {lambda:.4f}")
    """

    __slots__ = ("__X", "__cuda_worker")

    VALID_VERSIONS = {"AUTOMATIC", "GPU_DEDICATED", "SMART_TENSOR"}

    __dispatch_default = {
        ("cuda", torch.float32): lambda self, m: self._gpu_f32_native(m),
        ("cuda", torch.float16): lambda self, m: self._gpu_f16_pytorch(m),
        ("cpu", torch.float32): lambda self, m: self._cpu_f32_pytorch(m),
        ("cpu", torch.float16): lambda self, m: self._cpu_f16_pytorch(m),
    }
    __dispatch_native = {
        ("cuda", torch.float32): lambda self, m: self._gpu_f32_native(m),
        ("cuda", torch.float16): lambda self, m: self._gpu_f16_native(m),
        ("cpu", torch.float32): lambda self, m: self._cpu_f32_pytorch(m),
        ("cpu", torch.float16): lambda self, m: self._cpu_f16_pytorch(m),
    }
    __dispatch_pytorch = {
        ("cuda", torch.float32): lambda self, m: self._gpu_f32_pytorch(m),
        ("cuda", torch.float16): lambda self, m: self._gpu_f16_pytorch(m),
        ("cpu", torch.float32): lambda self, m: self._cpu_f32_pytorch(m),
        ("cpu", torch.float16): lambda self, m: self._cpu_f16_pytorch(m),
    }

    def __init__(self, X: torch.Tensor):
        """Initialize the LambdaHappy solver.

        Args:
            X (torch.Tensor): Input tensor of shape (n, p).
        """

        self.__X = X
        worker = None
        if torch.cuda.is_available():
            try:
                _ = torch.empty(1, device="cuda")  # Forcer l'initialisation CUDA
                device_index = X.device.index or 0
                seed = torch.cuda.default_generators[device_index].initial_seed()
                worker = LambdaComputer(seed=seed)
            except Exception as e:
                worker = None
        self.__cuda_worker = worker

    @property
    def X(self) -> torch.Tensor:
        """Return a clone of the input tensor.

        Returns:
            torch.Tensor: A copy of the original input X.
        """
        return self.__X.clone()

    def _validate_args(self, version: str, device_type: str, dtype: torch.dtype):
        """Validate algorithm parameters.

        Args:
            version (str): One of {'AUTOMATIC', 'GPU_DEDICATED', 'SMART_TENSOR'}.
            device_type (str): 'cpu' or 'cuda'.
            dtype (torch.dtype): torch.float32 or torch.float16.

        Raises:
            ValueError: If version, device_type, or dtype is invalid.
            RuntimeError: If CUDA requested but not available.
        """
        if version not in self.VALID_VERSIONS:
            raise ValueError(
                f"Invalid version: {version}, expected : {self.VALID_VERSIONS}"
            )
        if device_type not in ("cpu", "cuda"):
            raise ValueError(f"Invalid device_type: {device_type}")
        if dtype not in (torch.float32, torch.float16):
            raise ValueError(f"Invalid dtype: {dtype}")
        if device_type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA not available")

    def _select_impl(
        self, version: str, device_type: str, dtype: torch.dtype
    ) -> Callable[[int], float]:
        """Select the computation implementation based on parameters.

        Args:
            version (str): Execution mode.
            device_type (str): 'cpu' or 'cuda'.
            dtype (torch.dtype): Desired tensor data type.

        Raises:
            RuntimeError: If no implementation matches the given settings.

        Returns:
            Callable[[int], float]: Function taking m and returning λ.
        """
        key = (device_type, dtype)
        if version == "AUTOMATIC":
            fn = self.__dispatch_default.get(key)
        elif version == "GPU_DEDICATED":
            fn = self.__dispatch_native.get(key)
        elif version == "SMART_TENSOR":
            fn = self.__dispatch_pytorch.get(key)

        if fn is None:
            raise RuntimeError(
                f"No implementation for ({device_type =}, {dtype =} and {version =})"
            )
        return fn

    def compute(
        self,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        """Compute a single estimate of λ.

        Args:
            m (int, optional): Number of columns in the random projection matrix Z.
                    Z has shape (n, m). Defaults to 10000.
            version (str, optional): Strategy for dispatching the λ-computation. Must be one of:
                    - 'AUTOMATIC': automatically picks the best available backend for the current
                    device and dtype (either native C++ CUDA or PyTorch routines).
                    - 'GPU_DEDICATED': always uses the native C++ CUDA implementation on GPU;
                    raises if no CUDA float implementation is available.
                    - 'SMART_TENSOR': runs via PyTorch on CPU or GPU with smart tensor
                    optimizations (mixed-precision, fused ops).
                    Defaults to 'AUTOMATIC'.
            device_type (str, optional): 'cpu' or 'cuda'. Defaults to X.device.type.
            dtype (torch.dtype, optional): Data type for computation. Defaults to X.dtype.

        Returns:
            float: The estimated λ (0.95-quantile).
        """
        device_type = device_type or self.__X.device.type
        dtype = dtype or self.__X.dtype
        self._validate_args(version, device_type, dtype)
        impl = self._select_impl(version, device_type, dtype)
        return impl(self, m)

    def compute_many(
        self,
        nb_run: int,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> List[float]:
        """
        Compute multiple independent estimates of λ.

        Args:
            nb_run (int): Number of independent runs.
            m (int, optional): Number of columns in the random projection matrix Z.
                    Z has shape (n, m). Defaults to 10000.
            version (str, optional): Strategy for dispatching the λ-computation. Must be one of:
                    - 'AUTOMATIC': automatically picks the best available backend for the current
                    device and dtype (either native C++ CUDA or PyTorch routines).
                    - 'GPU_DEDICATED': always uses the native C++ CUDA implementation on GPU;
                    raises if no CUDA float implementation is available.
                    - 'SMART_TENSOR': runs via PyTorch on CPU or GPU with smart tensor
                    optimizations (mixed-precision, fused ops).
                    Defaults to 'AUTOMATIC'.
            device_type (str, optional): 'cpu' or 'cuda'. Defaults to X.device.type.
            dtype (torch.dtype, optional): Data type for computation.
                                           Defaults to X.dtype.

        Returns:
            List[float]: A list of λ estimates, one per run.
        """
        device_type = device_type or self.__X.device.type
        dtype = dtype or self.__X.dtype
        self._validate_args(version, device_type, dtype)
        impl = self._select_impl(version, device_type, dtype)

        return [impl(self, m) for _ in range(nb_run)]

    def compute_agg(
        self,
        nb_run: int,
        func: Callable = torch.median,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        """Compute an aggregated λ estimate over multiple runs.

        Args:
            nb_run (int): Number of independent runs.
            func (Callable, optional): Aggregation function (e.g., torch.mean,
                                       torch.median). Defaults to torch.median.
            m (int, optional): Number of columns in the random projection matrix Z.
                    Z has shape (n, m). Defaults to 10000.
            version (str, optional): Strategy for dispatching the λ-computation. Must be one of:
                    - 'AUTOMATIC': automatically picks the best available backend for the current
                    device and dtype (either native C++ CUDA or PyTorch routines).
                    - 'GPU_DEDICATED': always uses the native C++ CUDA implementation on GPU;
                    raises if no CUDA float implementation is available.
                    - 'SMART_TENSOR': runs via PyTorch on CPU or GPU with smart tensor
                    optimizations (mixed-precision, fused ops).
                    Defaults to 'AUTOMATIC'.
            device_type (str, optional): 'cpu' or 'cuda'. Defaults to X.device.type.
            dtype (torch.dtype, optional): Data type for computation.
                                           Defaults to X.dtype.

        Returns:
            float: Aggregated λ estimate (result of func over individual runs).
        """
        device_type = device_type or self.__X.device.type
        dtype = dtype or self.__X.dtype
        self._validate_args(version, device_type, dtype)
        impl = self._select_impl(version, device_type, dtype)

        results = torch.empty(nb_run, dtype=dtype, device=device_type)
        for i in range(nb_run):
            results[i] = impl(self, m)

        return func(results).item()

    def get_dtype(self) -> torch.dtype:
        """Get the data type of the input tensor X.

        Returns:
            torch.dtype: The dtype of X.
        """
        return self.__X.dtype

    def get_device_type(self) -> str:
        """Get the device type of the input tensor X.

        Returns:
            str: 'cpu' or 'cuda'.
        """
        return self.__X.device.type

    def _gpu_f32_native(self, m: int) -> float:
        """Compute λ using the native CUDA float32 backend.

        Args:
            m (int): Number of columns in Z.

        Raises:
            RuntimeError: If the native CUDA backend is not available.

        Returns:
            float: Estimated λ.
        """
        if self.__cuda_worker is None:
            raise RuntimeError("Native CUDA backend not available")
        Xc = self.__X.to(device="cuda", dtype=torch.float32).contiguous()
        return self.__cuda_worker.compute(Xc, m)

    def _gpu_f16_native(self, m: int) -> float:
        """Compute λ using the native CUDA float16 backend (falls back to PyTorch).

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._gpu_f16_pytorch(m)

    def _gpu_f32_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CUDA with float32.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cuda", torch.float32)

    def _gpu_f16_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CUDA with float16.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cuda", torch.float16)

    def _cpu_f32_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CPU with float32.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cpu", torch.float32)

    def _cpu_f16_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CPU with float16.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cpu", torch.float16)

    def _pytorch_compute(self, m: int, device: str, dtype: torch.dtype) -> float:
        """Compute λ using PyTorch operations on the specified device and precision.

        This method performs the following steps:
            1. Moves the input matrix X to the specified device and dtype.
            2. Samples a random Gaussian matrix Z of shape (n, m), zero-centered.
            3. Computes the Chebyshev (∞) norm of XᵀZ across columns.
            4. Computes the l2 norm of each column of Z.
            5. Computes λ = ||XᵀZ||_∞ / ||Z||₂ for each column.
            6. Returns the 0.95-quantile of the λ values as a float.

        Args:
            m (int): Number of columns in Z.
            device (str): 'cpu' or 'cuda'.
            dtype (torch.dtype): Data type for computation.

        Returns:
            float: Estimated λ (0.95-quantile).
        """
        X = self.__X.to(device=device, dtype=dtype)
        n = X.shape[0]
        Z = torch.randn(n, m, device=device, dtype=dtype)
        Z.sub_(Z.mean(dim=0, keepdim=True))
        numer = torch.linalg.norm(X.T @ Z, ord=float("inf"), dim=0)
        denom = torch.linalg.norm(Z, ord=2, dim=0)
        lambdas = (numer / denom).to(torch.float32)
        return torch.quantile(lambdas, 0.95).item()


class LambdaHappyPartial:
    """Stepwise computation of the λ factor for sparse models.

    This helper class breaks down the λ-estimation pipeline into individual
    stages (random projection generation, centering, matrix multiplications,
    norm computations, ratio calculation, and quantile extraction). Users
    can prepare any stage by running all preceding steps via `prepare_func`.
    """

    def __init__(self, X: torch.Tensor, m: int, device_type: str, dtype: torch.dtype):
        """
        Initialize the partial λ-computation pipeline.

        Args:
            X (torch.Tensor): Input tensor of shape (n, p).
            m (int): Number of columns in the random projection matrix Z.
            device_type (str): Target device for computation ('cpu' or 'cuda').
            dtype (torch.dtype): Data type for computation (torch.float32 or torch.float16).
        """
        self._X = X.to(device=device_type, dtype=dtype)
        self._m = m
        self._device_type = device_type
        self._dtype = dtype

        self._Z = None
        self._XTZ = None
        self._numerator = None
        self._denominator = None
        self._lambdas = None

        self.pipeline = [
            self.generate_Z,
            self.center_Z,
            self.compute_XTZ,
            self.compute_numerator,
            self.compute_denominator,
            self.compute_lambdas,
            self.compute_lambda_quantile,
            self.chain1,
            self.chain2,
        ]

    def _get_preparation_pipeline(self, target_func: Callable):
        """Get the list of pipeline steps needed before running `target_func`.

        Args:
            target_func (Callable): One of the methods in `self.pipeline`.

        Raises:
            ValueError: If `target_func` is not found in the pipeline.

        Returns:
            Tuple[List[Callable], Callable]: (preparation steps, the target function)
        """
        if target_func not in self.pipeline:
            raise ValueError(f"Fonction {target_func} non trouvée dans la pipeline")
        idx = self.pipeline.index(target_func)
        return self.pipeline[:idx], target_func

    def prepare_func(self, target_callable: Callable):
        """Execute all pipeline steps prior to the specified target callable.

        Args:
            target_callable (Callable): One of the pipeline methods to prepare for.
        """
        prepare_funcs, _ = self._get_preparation_pipeline(target_callable)
        for func in prepare_funcs:
            func()

    def generate_Z(self):
        """Generate the random projection matrix Z.

        Z has shape (n, m), sampled from a standard normal distribution.
        """
        n = self._X.shape[0]
        self._Z = torch.randn(n, self._m, device=self._device_type, dtype=self._dtype)

    def center_Z(self):
        """Center each column of Z in-place to have zero mean."""
        self._Z.sub_(self._Z.mean(dim=0, keepdim=True))  # In-place centering

    def compute_XTZ(self):
        """Compute the product XᵀZ and store it in `_XTZ`."""
        self._XTZ = self._X.T @ self._Z

    def compute_numerator(self):
        """Compute the Chebyshev (ℓ∞) norm of each column of XᵀZ.

        Stores per-column norms in `_numerator`.
        """
        self._numerator = torch.linalg.norm(self._XTZ, ord=float("inf"), dim=0)

    def compute_denominator(self):
        """Compute the Euclidean (ℓ₂) norm of each column of Z.

        Stores per-column norms in `_denominator`.
        """
        self._denominator = torch.linalg.norm(self._Z, ord=2, dim=0)

    def compute_lambdas(self):
        """Compute the ratio of `_numerator` to `_denominator` for each column.

        Stores results in `_lambdas`.
        """
        self._lambdas = self._numerator / self._denominator

    def compute_lambda_quantile(self) -> float:
        """Compute and return the 0.95-quantile of the λ ratios.

        Returns:
            float: The 0.95-quantile of `_lambdas` (cast to float32).
        """
        return torch.quantile(self._lambdas.to(torch.float32), 0.95).item()

    def chain1(self):
        """Combined step: recompute XᵀZ and its Chebyshev norm.

        Useful for quick re-evaluation without regenerating Z.
        """
        self._XTZ = self._X.T @ self._Z
        self._numerator = torch.linalg.norm(self._XTZ, ord=float("inf"), dim=0)

    def chain2(self) -> float:
        """Full re-evaluation of ratio and quantile, reusing existing Z.

        Returns:
            float: The 0.95-quantile of the recomputed λ ratios.
        """
        self._XTZ = self._X.T @ self._Z
        self._numerator = torch.linalg.norm(self._XTZ, ord=float("inf"), dim=0)
        self._denominator = torch.linalg.norm(self._Z, ord=2, dim=0)
        self._lambdas = self._numerator / self._denominator
        self._lambdas = self._lambdas.to(torch.float32)
        return torch.quantile(self._lambdas, 0.95).item()

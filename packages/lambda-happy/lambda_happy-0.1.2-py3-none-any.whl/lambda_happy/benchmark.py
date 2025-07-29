import time
from typing import List, Callable, Optional

import torch
import numpy as np
import matplotlib


def choose_matplotlib_backend(preferred_backends=None):
    if preferred_backends is None:
        preferred_backends = ["Qt5Agg", "TkAgg", "Agg"]
    for backend in preferred_backends:
        try:
            matplotlib.use(backend)
            print(f"Using matplotlib backend: {backend}")
            return backend
        except ImportError:
            pass
    else:
        raise RuntimeError("No suitable matplotlib backend found.")


backend = choose_matplotlib_backend()

import matplotlib.pyplot as plt

from .lambda_happy import LambdaHappy, LambdaHappyPartial


class LambdaBenchmark:
    def __init__(self, estimator: LambdaHappy):
        self.estimator = estimator
        self.tested_versions = ["SMART_TENSOR", "GPU_DEDICATED"]

    def _sync(self):
        if self.estimator.get_device_type() == "cuda" and torch.cuda.is_available():
            torch.cuda.synchronize()

    def _benchmark_single(
        self,
        m: int = 100_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        self._sync()
        _ = self.estimator.compute(
            m=1, version=version, device_type=device_type, dtype=dtype
        )
        self._sync()
        start = time.perf_counter()
        _ = self.estimator.compute(
            m=m, version=version, device_type=device_type, dtype=dtype
        )
        self._sync()
        return 1.0 / (time.perf_counter() - start)

    def _benchmark_many(
        self,
        nb_run: int = 20,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        self._sync()
        [
            self.estimator.compute(
                m=1, version=version, device_type=device_type, dtype=dtype
            )
            for _ in range(10)
        ]
        self._sync()
        start = time.perf_counter()
        _ = self.estimator.compute_many(
            nb_run, m=m, version=version, device_type=device_type, dtype=dtype
        )
        self._sync()
        return nb_run / (time.perf_counter() - start)

    def _benchmark_many_callable(
        self, nb_run: int, target_callable: Callable[[], Optional[float]]
    ) -> float:
        self._sync()
        target_callable()
        self._sync()

        start = time.perf_counter()
        for _ in range(nb_run):
            target_callable()
        self._sync()
        elapsed = time.perf_counter() - start
        return nb_run / elapsed

    def show_benchmark_2D(
        self,
        m_values: np.ndarray = None,
        p_values: np.ndarray = None,
        initial_n: int = 1_000,
        initial_p: int = 1_000,
        initial_m: int = 10_000,
        version: str = "AUTOMATIC",
    ) -> None:

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        if p_values is None:
            p_values = np.arange(10, 10_000, 1_000)

        original_estimator = self.estimator
        benchmark_m_results = {"pytorch_cpu": [], "pytorch_cuda": []}
        benchmark_nb_cols_results = {"pytorch_cpu": [], "pytorch_cuda": []}
        for m in m_values:
            X = torch.randn(
                initial_n,
                initial_p,
                device=original_estimator.get_device_type(),
                dtype=original_estimator.get_dtype(),
            )
            self.estimator = LambdaHappy(X)
            benchmark_m_results["pytorch_cpu"].append(
                self._benchmark_many(m=m, version=version, device_type="cpu")
            )
            benchmark_m_results["pytorch_cuda"].append(
                self._benchmark_many(m=m, version=version, device_type="cuda")
            )

        for p in p_values:
            X = torch.randn(
                initial_n,
                p,
                device=original_estimator.get_device_type(),
                dtype=original_estimator.get_dtype(),
            )
            self.estimator = LambdaHappy(X)
            benchmark_nb_cols_results["pytorch_cpu"].append(
                self._benchmark_many(m=initial_m, version=version, device_type="cpu")
            )
            benchmark_nb_cols_results["pytorch_cuda"].append(
                self._benchmark_many(m=initial_m, version=version, device_type="cuda")
            )

        self.estimator = original_estimator
        fig, axs = plt.subplots(1, 2, figsize=(14, 6))
        axs[0].plot(m_values, benchmark_m_results["pytorch_cpu"], label="CPU")
        axs[0].set_title("CPU Benchmark for m values")
        axs[0].set_xlabel("m Size")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].grid(True)
        axs[1].plot(m_values, benchmark_m_results["pytorch_cuda"], label="CUDA")
        axs[1].set_title("CUDA Benchmark for m values")
        axs[1].set_xlabel("m Size")
        axs[1].set_ylabel("FPS (s$^{-1}$)")
        axs[1].grid(True)
        plt.tight_layout()

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))
        axs[0].plot(p_values, benchmark_nb_cols_results["pytorch_cpu"], label="CPU")
        axs[0].set_title("CPU Benchmark for number of cols values")
        axs[0].set_xlabel("p Size")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].grid(True)
        axs[1].plot(p_values, benchmark_nb_cols_results["pytorch_cuda"], label="CUDA")
        axs[1].set_title("CUDA Benchmark for number of cols values")
        axs[1].set_xlabel("p Size")
        axs[1].set_ylabel("FPS (s$^{-1}$)")
        axs[1].grid(True)
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

    def show_benchmark_3D(
        self,
        m_values: np.ndarray = None,
        p_values: np.ndarray = None,
        n: int = 1_000,
        version: str = "AUTOMATIC",
    ) -> None:

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        if p_values is None:
            p_values = np.arange(10, 10_000, 1_000)

        original_estimator = self.estimator
        benchmark_results = {
            "pytorch_cpu": np.zeros((len(m_values), len(p_values))),
            "pytorch_cuda": np.zeros((len(m_values), len(p_values))),
        }

        for i, m in enumerate(m_values):
            for j, p in enumerate(p_values):
                X = torch.randn(n, p)
                self.estimator = LambdaHappy(X)
                benchmark_results["pytorch_cpu"][i, j] = self._benchmark_many(
                    m=m, version=version, device_type="cpu"
                )

                if torch.cuda.is_available():
                    benchmark_results["pytorch_cuda"][i, j] = self._benchmark_many(
                        m=m, version=version, device_type="cuda"
                    )

        self.estimator = original_estimator

        M, P = np.meshgrid(m_values, p_values, indexing="ij")

        fig = plt.figure(figsize=(14, 6))

        # 3D plot CPU
        ax1 = fig.add_subplot(121, projection="3d")
        ax1.plot_surface(M, P, benchmark_results["pytorch_cpu"], cmap="Blues")
        ax1.set_title(f"Benchmark {version} CPU")
        ax1.set_xlabel("m values")
        ax1.set_ylabel("p values")
        ax1.set_zlabel("FPS (s$^{-1}$)")

        # 3D plot CUDA
        ax2 = fig.add_subplot(122, projection="3d")
        ax2.plot_surface(M, P, benchmark_results["pytorch_cuda"], cmap="Reds")
        ax2.set_title(f"Benchmark {version} CUDA")
        ax2.set_xlabel("m values")
        ax2.set_ylabel("p values")
        ax2.set_zlabel("FPS (s$^{-1}$)")

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

    def _estimate_lambda_distribution(
        self, m_values: np.ndarray, nb_run: int = 100, version: str = "SMART_TENSOR"
    ) -> List[List[float]]:
        results = []
        for m in m_values:
            results.append(
                self.estimator.compute_many(nb_run=nb_run, version=version, m=m)
            )
        return results

    def _show_lambda_distribution(
        self,
        median_value: float,
        results: List[List[float]],
        m_values: np.ndarray,
        m_median_size: int = 100_000,
    ) -> None:
        formatted_median_size = f"{m_median_size:,}".replace(",", "_")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        ax1.boxplot(results, positions=range(1, len(m_values) + 1))
        ax1.set_xticks(range(1, len(m_values) + 1))
        ax1.set_xticklabels(m_values)
        ax1.set_xlabel("Size of Z (m)")
        ax1.set_ylabel("Lambda values distribution")
        ax1.hlines(
            median_value,
            1,
            len(m_values),
            linestyles="dashed",
            colors="red",
            label=f"Median (Z size : {formatted_median_size}): {median_value}",
        )

        ax2.plot(
            range(1, len(m_values) + 1),
            [np.var(i) for i in results],
            color="blue",
            label="Variance",
        )
        ax2.set_xticks(range(1, len(m_values) + 1))
        ax2.set_xticklabels(m_values)
        ax2.set_ylabel("Variance")
        ax2.set_xlabel("Size of Z (m)")

        fig.suptitle("Median and Variance on Lambda Estimations")

        ax1.legend(loc="upper right")
        ax2.legend(loc="upper right")

        ax1.grid(True)
        ax2.grid(True)

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

    def show_lambda_distribution_small(
        self,
        m_values: np.ndarray = None,
        nb_run: int = 100,
        m_median_size: int = 100_000,
        version: str = "SMART_TENSOR",
    ) -> None:

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        results = self._estimate_lambda_distribution(
            m_values, nb_run=nb_run, version=version
        )
        median_value = self.estimator.compute_agg(
            nb_run=nb_run, func=torch.median, m=m_median_size, version=version
        )

        self._show_lambda_distribution(
            median_value=median_value,
            results=results,
            m_values=m_values,
            m_median_size=m_median_size,
        )

    def show_lambda_distribution_large(
        self,
        m_values: np.ndarray = None,
        nb_run: int = 100,
        m_median_size: int = 100_000,
        version: str = "SMART_TENSOR",
    ) -> None:

        if m_values is None:
            m_values = np.concatenate(
                (
                    10 * 2 ** np.arange(10, 14),
                    (
                        (10 * 2 ** np.arange(10, 14) + 10 * 2 ** np.arange(11, 15)) / 2
                    ).astype(int),
                )
            )
        m_values.sort()

        results = self._estimate_lambda_distribution(
            m_values, nb_run=nb_run, version=version
        )
        median_value = self.estimator.compute_agg(
            nb_run=nb_run, func=torch.median, m=m_median_size, version=version
        )

        self._show_lambda_distribution(
            median_value=median_value,
            results=results,
            m_values=m_values,
            m_median_size=m_median_size,
        )

    def show_benchmark_float(
        self, m_values: np.ndarray = None, version: str = "SMART_TENSOR"
    ) -> None:

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        benchmark_m_results = {"pytorch_cuda_float16": [], "pytorch_cuda_float32": []}

        for m in m_values:
            benchmark_m_results["pytorch_cuda_float16"].append(
                self._benchmark_many(
                    m=m,
                    nb_run=500,
                    version=version,
                    device_type="cuda",
                    dtype=torch.float16,
                )
            )
            benchmark_m_results["pytorch_cuda_float32"].append(
                self._benchmark_many(
                    m=m,
                    nb_run=500,
                    version=version,
                    device_type="cuda",
                    dtype=torch.float32,
                )
            )

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))

        axs[0].plot(
            m_values,
            benchmark_m_results["pytorch_cuda_float16"],
            label="CUDA float16",
            color="b",
        )
        axs[0].plot(
            m_values,
            benchmark_m_results["pytorch_cuda_float32"],
            label="CUDA float32",
            color="r",
        )
        axs[0].set_title(
            f"Benchmark PyTorch CUDA with float16 vs float32 (version: {version})"
        )
        axs[0].set_xlabel("m values")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].legend()
        axs[0].grid(True)

        # Gain factor = float16 speed / float32 speed
        fps_f16 = np.array(benchmark_m_results["pytorch_cuda_float16"])
        fps_f32 = np.array(benchmark_m_results["pytorch_cuda_float32"])
        gain_factor = fps_f16 / fps_f32

        axs[1].plot(m_values, gain_factor, label="Gain factor", color="black")
        axs[1].set_title("Performance comparison: float32 vs float16")
        axs[1].set_xlabel("m values")
        axs[1].set_ylabel("Gain factor (float16 / float32)")
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

    def show_benchmark_version(
        self, m_values: np.ndarray = None, p_values: np.ndarray = None, n: int = 1_000
    ) -> None:

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        if p_values is None:
            p_values = np.arange(10, 10_000, 1_000)

        benchmark_m = {v: [] for v in self.tested_versions}
        benchmark_p = {v: [] for v in self.tested_versions}

        # Benchmark with different m
        for m in m_values:
            for version in self.tested_versions:
                fps = self._benchmark_many(version=version, device_type="cuda", m=m)
                benchmark_m[version].append(fps)

        # Benchmark with different p
        original = self.estimator
        for p in p_values:
            X = torch.randn(n, p, device="cuda", dtype=torch.float32)
            self.estimator = LambdaHappy(X)
            for version in self.tested_versions:
                fps = self._benchmark_many(version=version, device_type="cuda")
                benchmark_p[version].append(fps)
        self.estimator = original

        # Plot variation de m
        fig, ax = plt.subplots(figsize=(7, 5))
        for version in self.tested_versions:
            ax.plot(m_values, benchmark_m[version], label=version)
        ax.set_title(
            f"GPU Benchmark ({self.tested_versions[0]} vs {self.tested_versions[1]}) - m variation"
        )
        ax.set_xlabel("m")
        ax.set_ylabel("FPS (s$^{-1}$)")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()

        # Plot variation de p
        fig, ax = plt.subplots(figsize=(7, 5))
        for version in self.tested_versions:
            ax.plot(p_values, benchmark_p[version], label=version)
        ax.set_title(
            f"GPU Benchmark ({self.tested_versions[0]} vs {self.tested_versions[1]}) - p variation"
        )
        ax.set_xlabel("p")
        ax.set_ylabel("FPS (s$^{-1}$)")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()

        plt.show(block=False)
        plt.pause(0.1)

    def benchmark_partial(
        self, n: int = 1_000, p: int = 1_000, m: int = 10_000, nb_run: int = 500
    ) -> None:

        original_estimator = self.estimator
        device_type = original_estimator.get_device_type()
        dtype = original_estimator.get_dtype()
        X = torch.randn(n, p, device=device_type, dtype=dtype)

        partial_estimator = LambdaHappyPartial(
            X, m, device_type=device_type, dtype=dtype
        )
        self.estimator = LambdaHappy(X)

        total_time = 0.0

        for target_callable in partial_estimator.pipeline:
            partial_estimator.prepare_func(target_callable)
            mean_fps = self._benchmark_many_callable(nb_run, lambda: target_callable())
            print(
                f"Mean FPS over {nb_run} runs of {target_callable.__func__.__name__:31s} : {mean_fps:.8f} FPS ({(1/mean_fps):.8f} sec)"
            )
            if target_callable not in (
                partial_estimator.chain1,
                partial_estimator.chain2,
            ):
                total_time += 1 / mean_fps

        for version in self.tested_versions:
            mean_fps = self._benchmark_many(
                nb_run=nb_run,
                m=m,
                version=version,
                device_type=device_type,
                dtype=dtype,
            )
            print(
                f"Mean FPS over {nb_run} runs of {self.estimator.__class__.__name__:31s} : {mean_fps:.8f} FPS ({(1/mean_fps):.8f} sec) (version={version})"
            )
        self.estimator = original_estimator

        fps_theorical = 1.0 / total_time if total_time > 0 else float("inf")
        print(
            f"Theorical LambdaHappy mean FPS (sum of independent steps) : {fps_theorical:.8f} FPS ({total_time:.8f} sec) (version=SMART_TENSOR)"
        )

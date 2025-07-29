import argparse
import sys

import torch
import matplotlib.pyplot as plt
from lambda_happy import LambdaHappy, LambdaBenchmark


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="CLI for LambdaHappy benchmarking and λ estimation."
    )
    # Benchmark toggles
    parser.add_argument(
        "--benchmark_2D", action="store_true", help="Run 2D benchmark (m vs throughput)"
    )
    parser.add_argument(
        "--benchmark_3D",
        action="store_true",
        help="Run 3D benchmark (m,p vs throughput)",
    )
    parser.add_argument(
        "--benchmark_float",
        action="store_true",
        help="Compare CUDA float16 vs float32 throughput",
    )
    parser.add_argument(
        "--benchmark_version",
        action="store_true",
        help="Compare GPU_DEDICATED vs SMART_TENSOR on CUDA",
    )
    parser.add_argument(
        "--distribution_small",
        action="store_true",
        help="Show small-scale λ distribution across multiple m",
    )
    parser.add_argument(
        "--distribution_large",
        action="store_true",
        help="Show large-scale λ distribution across multiple m",
    )
    parser.add_argument(
        "--compute_lambda",
        action="store_true",
        help="Compute a single λ estimate and print it",
    )

    # Hyper‑parameters
    parser.add_argument(
        "--dtype",
        type=str,
        default="float32",
        choices=["float16", "float32"],
        help="Tensor data type for computation",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="SMART_TENSOR",
        choices=["AUTOMATIC", "GPU_DEDICATED", "SMART_TENSOR"],
        help="Implementation version to use",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        choices=["cpu", "cuda"],
        help="Device on which to run (default = X.device or cpu if not set)",
    )
    parser.add_argument("-n", type=int, default=1_000, help="Number of rows in X")
    parser.add_argument(
        "-p", type=int, default=1_000, help="Number of columns (features) in X"
    )
    parser.add_argument(
        "-m",
        type=int,
        default=10_000,
        help="Number of random projection vectors (columns of Z)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=100,
        help="Number of runs for batched benchmarks / distributions",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
    }
    dtype = dtype_map[args.dtype]

    # Determine device
    if args.device:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Build random X
    print(f"> Creating X of shape ({args.n}, {args.p}) on {device} with dtype={dtype}")
    X = torch.randn(args.n, args.p, device=device, dtype=dtype)

    # Instantiate
    estimator = LambdaHappy(X)
    bench = LambdaBenchmark(estimator)

    # Dispatch
    any_ran = False

    if args.compute_lambda:
        lam = estimator.compute(
            m=args.m, version=args.version, device_type=device, dtype=dtype
        )
        print(f"> λ estimate (m={args.m}, version={args.version}): {lam:.6f}")
        any_ran = True

    if args.benchmark_2D:
        print("> Running 2D benchmark…")
        bench.show_benchmark_2D(
            version=args.version,
        )
        any_ran = True

    if args.benchmark_3D:
        print("> Running 3D benchmark…")
        bench.show_benchmark_3D(
            version=args.version,
        )
        any_ran = True

    if args.benchmark_float:
        print("> Running float16 vs float32 benchmark on CUDA…")
        bench.show_benchmark_float(
            version=args.version,
        )
        any_ran = True

    if args.benchmark_version:
        print("> Running version comparison benchmark on CUDA…")
        bench.show_benchmark_version()
        any_ran = True

    if args.distribution_small:
        print("> Showing small λ distribution…")
        bench.show_lambda_distribution_small(
            nb_run=args.runs,
            version=args.version,
        )
        any_ran = True

    if args.distribution_large:
        print("> Showing large λ distribution…")
        bench.show_lambda_distribution_large(
            nb_run=args.runs,
            version=args.version,
        )
        any_ran = True

    if not any_ran:
        print("No action requested. Use --help to see available options.")
        sys.exit(1)

    if plt.get_fignums():
        plt.show()


if __name__ == "__main__":
    main()

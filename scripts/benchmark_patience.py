# ruff: noqa: E501
import functools
import logging
import statistics
from collections.abc import Callable
from time import perf_counter
from typing import Any

from diffr.core.patience import diff_hunks


def profile_performance(runs: int = 1, show_stats: bool = True):
    """
    Decorate to profile the performance of a function.

    Args:
        runs: Number of times to run the function for averaging
        show_stats: Whether to show detailed statistics

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            wrapper.execution_times = []  # Store execution times in the wrapper

            result = None
            for _ in range(runs):
                start_time = perf_counter()
                result = func(*args, **kwargs)
                end_time = perf_counter()
                wrapper.execution_times.append(end_time - start_time)

            if show_stats and runs > 1:
                logging.info(f"\n----- Performance profile for {func.__name__} -----")
                logging.info(f"Total runs: {runs}")
                logging.info(f"Average time: {statistics.mean(wrapper.execution_times):.6f} seconds")
                logging.info(f"Median time: {statistics.median(wrapper.execution_times):.6f} seconds")
                logging.info(f"Min time: {min(wrapper.execution_times):.6f} seconds")
                logging.info(f"Max time: {max(wrapper.execution_times):.6f} seconds")
                if runs > 2:
                    logging.info(f"Std dev: {statistics.stdev(wrapper.execution_times):.6f} seconds")
                logging.info(f"Total time: {sum(wrapper.execution_times):.6f} seconds")
                logging.info("---------------------------------------------")
            else:
                logging.info(f"{func.__name__} executed in {wrapper.execution_times[0]:.6f} seconds")

            return result

        return wrapper

    return decorator


# Multi-line test cases
CODE_OLD_0 = """def calculate_total(items, discount=0):
    total = 0
    for item in items:
        total += item.price

    # Apply discount
    if discount > 0:
        total -= total * discount

    return total"""

CODE_NEW_0 = """def calculate_total(items, discount=0, tax_rate=0):
    total = 0
    # Calculate item sum
    for item in items:
        if item.available:
            total += item.price

    # Apply discount
    if discount > 0:
        total = total * (1 - discount)

    # Apply tax
    if tax_rate > 0:
        total += total * tax_rate

    return round(total, 2)"""

CODE_OLD_1 = """class Configuration:
    def __init__(self):
        self.settings = {}
        self.load_defaults()

    def load_defaults(self):
        self.settings = {
            'timeout': 30,
            'retry': 3,
            'log_level': 'info'
        }

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value"""

CODE_NEW_1 = """class Configuration:
    def __init__(self, config_file=None):
        self.settings = {}
        self.config_file = config_file
        self.load_defaults()
        if config_file:
            self.load_from_file()

    def load_defaults(self):
        self.settings = {
            'timeout': 30,
            'retry': 3,
            'log_level': 'info',
            'cache_enabled': False
        }

    def load_from_file(self):
        # Load settings from file
        print(f"Loading configuration from {self.config_file}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def save(self):
        # Save settings back to file
        if self.config_file:
            print(f"Saving configuration to {self.config_file}")"""

RUNS = 1000


def format_markdown_table(results: list[dict]) -> str:  # noqa: D103
    header = (
        "| Test Case                    | Lines | Avg Time (s) | Lines/sec   | Hunks | Hunks/sec |\n"
        "|-----------------------------|-------|--------------|-------------|--------|-----------|"
    )
    rows = []
    for res in results:
        row = "| {test_case:<27} | {lines:<5} | {avg_time:<12.6f} | {lines_per_sec:>6.2f} M/s | {hunks:<6} | {hunks_per_sec:>6.2f} M/s |".format(
            test_case=res["name"],
            lines=res["lines"],
            avg_time=res["avg_time"],
            lines_per_sec=res["lines_per_sec"] / 1_000_000,
            hunks=res["hunks"],
            hunks_per_sec=res["hunks_per_sec"] / 1_000_000,
        )
        rows.append(row)

    return header + "\n" + "\n".join(rows)


def run_test(func: Callable, code_old: str, code_new: str):
    """Run a test with the given function and code snippets."""
    profiled_lambda = profile_performance(runs=RUNS)(func)

    try:
        result = profiled_lambda(code_old, code_new)
        avg_time = statistics.mean(profiled_lambda.execution_times)

        if hasattr(result, "__len__"):
            n_lines = len(code_old.splitlines()) + len(code_new.splitlines())
            lines_per_second = n_lines / avg_time
            logging.info("n_lines: %d", n_lines)
            logging.info("lines per second: %.2f M/s", lines_per_second / 1_000_000)
            n_items = len(result)
            items_per_second = n_items / avg_time
            logging.info("n_hunks: %d", n_items)
            logging.info("Hunks per second: %.2f M/s", items_per_second / 1_000_000)
            logging.info("Total raw diff length: %d", len(diff_hunks(code_old, code_new)["hunks"]))

        return avg_time, result
    except Exception as e:
        logging.error("Can't run the implementation: %s", e)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    benchmark_results = []

    # Test the hunks result function
    def patience_hunks_func(old: str, new: str):
        """Run the patience diff algorithm and return the hunks result."""
        return diff_hunks(old, new)

    logging.info("\n===== Testing with CODE_OLD_0 and CODE_NEW_0 =====")

    # Test hunks function with first code sample
    hunks_time, hunks_result = run_test(patience_hunks_func, CODE_OLD_0, CODE_NEW_0)
    benchmark_results.append(
        {
            "name": "CODE_OLD_0 vs CODE_NEW_0",
            "lines": len(CODE_OLD_0.splitlines()) + len(CODE_NEW_0.splitlines()),
            "avg_time": hunks_time,
            "lines_per_sec": (len(CODE_OLD_0.splitlines()) + len(CODE_NEW_0.splitlines())) / hunks_time,
            "hunks": len(hunks_result["hunks"]),
            "hunks_per_sec": len(hunks_result["hunks"]) / hunks_time,
        }
    )
    logging.info("Patience hunks time: %.6f", hunks_time)
    logging.info("Number of hunks: %d", len(hunks_result["hunks"]))

    logging.info("\n===== Testing with CODE_OLD_1 and CODE_NEW_1 =====")

    # Test hunks function with second code sample
    hunks_time, hunks_result = run_test(patience_hunks_func, CODE_OLD_1, CODE_NEW_1)
    benchmark_results.append(
        {
            "name": "CODE_OLD_1 vs CODE_NEW_1",
            "lines": len(CODE_OLD_1.splitlines()) + len(CODE_NEW_1.splitlines()),
            "avg_time": hunks_time,
            "lines_per_sec": (len(CODE_OLD_1.splitlines()) + len(CODE_NEW_1.splitlines())) / hunks_time,
            "hunks": len(hunks_result["hunks"]),
            "hunks_per_sec": len(hunks_result["hunks"]) / hunks_time,
        }
    )
    logging.info("Patience hunks time: %.6f", hunks_time)
    logging.info("Number of hunks: %d", len(hunks_result["hunks"]))

    # Compare with a much larger file
    large_old = "\n".join([CODE_OLD_0] * 10 + [CODE_OLD_1] * 10)
    large_new = "\n".join([CODE_NEW_0] * 10 + [CODE_NEW_1] * 10)

    logging.info("\n===== Testing with large combined files (10x each) =====")

    # Use fewer runs for the large file test
    large_runs = 100

    # Test hunks function with large files
    large_hunks_time, large_hunks_result = run_test(patience_hunks_func, large_old, large_new)
    benchmark_results.append(
        {
            "name": "Large combined files (10x each)",
            "lines": len(large_old.splitlines()) + len(large_new.splitlines()),
            "avg_time": large_hunks_time,
            "lines_per_sec": (len(large_old.splitlines()) + len(large_new.splitlines())) / large_hunks_time,
            "hunks": len(large_hunks_result["hunks"]),
            "hunks_per_sec": len(large_hunks_result["hunks"]) / large_hunks_time,
        }
    )

    logging.info("Large patience hunks time: %.6f", large_hunks_time)
    logging.info("Number of hunks in large file: %d", len(large_hunks_result["hunks"]))

    markdown_table = format_markdown_table(benchmark_results)
    print("\nMarkdown Benchmark Table:\n")
    print(markdown_table)

    # # Si querés guardar en archivo:
    # with open("benchmark_results.md", "w") as f:
    #     f.write("# 📈 Patience Diff Benchmark Results\n\n")
    #     f.write(markdown_table + "\n")

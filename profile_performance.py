import functools
import logging
import statistics
import time
from collections.abc import Callable
from typing import Any
import json


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
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
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


CODE_OLD = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/data"), retries=3, timeout=30, verbose=True)'
CODE_NEW = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/archived"), retries=5, timeout=20, verbose=False)'

from diffr.algorithms.myers import diff_line  # noqa: E402
from diffr.algorithms.myers_cy import diff_line as diff_line_cy  # noqa: E402

# Example of direct use with a lambda
if __name__ == "__main__":
    RUNS = 100000
    logging.basicConfig(level=logging.INFO)

    def diff_func(old: str, new: str) -> str:  # noqa: D103
        diff = diff_line(old, new)
        return diff

    def diff_func_cy(old: str, new: str) -> str:
        diff = diff_line_cy(old, new)
        return diff

    try:
        profiled_lambda = profile_performance(runs=RUNS)(diff_func)
        diff = profiled_lambda(CODE_OLD, CODE_NEW)

        # Native performance
        total_lines = len(CODE_OLD.split("\n")) + len(CODE_NEW.split("\n"))
        avg_time = statistics.mean(profiled_lambda.execution_times)
        lines_per_second = total_lines / avg_time

        logging.info("Lines old: %d", len(CODE_OLD.split("\n")))
        logging.info("Lines new: %d", len(CODE_NEW.split("\n")))
        logging.info("Lines per second: %.2f", lines_per_second)
    except Exception as e:
        logging.error("Can't run the native implementation: %s", e)
        raise

    try:
        profiled_lambda_cy = profile_performance(runs=RUNS)(diff_func_cy)
        diff_cy = profiled_lambda_cy(CODE_OLD, CODE_NEW)
        # Cython performance
        total_lines = len(CODE_OLD.split("\n")) + len(CODE_NEW.split("\n"))
        avg_time = statistics.mean(profiled_lambda_cy.execution_times)
        lines_per_second = total_lines / avg_time

        logging.info("Lines old: %d", len(CODE_OLD.split("\n")))
        logging.info("Lines new: %d", len(CODE_NEW.split("\n")))
        logging.info("Lines per second (Cython): %.2f", lines_per_second)
    except Exception as e:
        logging.error("Can't run the Cython implementation: %s", e)
        raise

    logging.info(
        "Speedup: %.2fx",
        statistics.mean(profiled_lambda.execution_times) / statistics.mean(profiled_lambda_cy.execution_times),
    )

    print(diff == diff_cy)

import functools
import logging
import statistics
from time import perf_counter
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


CODE_OLD = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/data"), retries=3, timeout=30, verbose=True)'
CODE_NEW = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/archived"), retries=5, timeout=20, verbose=False)'

from diffr.algorithms.myers_cy import diff_line as diff_line_cy  # noqa: E402
from diffr.algorithms.myers_cy import tokenize as tokenize_cy  # noqa: E402

RUNS = 100000

def run_test(func: Callable, code_old: str, code_new: str):
    profiled_lambda = profile_performance(runs=RUNS)(func)
    
    try:
        result = profiled_lambda(code_old, code_new)
        # Native performance
        total_lines_old = len(CODE_OLD.split("\n"))
        total_lines_new = len(CODE_NEW.split("\n"))
        total_lines = total_lines_old + total_lines_new
        avg_time = statistics.mean(profiled_lambda.execution_times)
        lines_per_second = total_lines / avg_time

        logging.info("Lines old: %d", len(CODE_OLD.split("\n")))
        logging.info("Lines new: %d", len(CODE_NEW.split("\n")))
        logging.info("Lines per second: %.2f", lines_per_second)
        return avg_time, result
    except Exception as e:
        logging.error("Can't run the implementation: %s", e)
        raise

EXPECTED_TOKENS = [
    'result', '=', 'process_data', '(', 'user_id', '=', '123', ',', 'data', '=', 'fetch_data', '(', '"', 'https', ':', '/' , '/', 'api', '.', 'example', '.', 'com', '/', 'data', '"', ')', ',', 'retries', '=', '3', ',', 'timeout', '=', '30', ',', 'verbose', '=', 'True', ')',
    'result', '=', 'process_data', '(', 'user_id', '=', '123', ',', 'data', '=', 'fetch_data', '(', '"', 'https', ':', '/' , '/', 'api', '.', 'example', '.', 'com', '/', 'archived', '"', ')', ',', 'retries', '=', '5', ',', 'timeout', '=', '20', ',', 'verbose', '=', 'False', ')'
]

EXPECTED_DIFF = [('equal', 'result'), ('equal', '='), ('equal', 'process_data'), ('equal', '('), ('equal', 'user_id'), ('equal', '='), ('equal', '123'), ('equal', ','), ('equal', 'data'), ('equal', '='), ('equal', 'fetch_data'), ('equal', '('), ('equal', '"'), ('equal', 'https'), ('equal', ':'), ('equal', '/'), ('equal', '/'), ('equal', 'api'), ('equal', '.'), ('equal', 'example'), ('equal', '.'), ('equal', 'com'), ('equal', '/'), ('delete', 'data'), ('insert', 'archived'), ('equal', '"'), ('equal', ')'), ('equal', ','), ('equal', 'retries'), ('equal', '='), ('delete', '3'), ('insert', '5'), ('equal', ','), ('equal', 'timeout'), ('equal', '='), ('delete', '30'), ('insert', '20'), ('equal', ','), ('equal', 'verbose'), ('equal', '='), ('delete', 'True'), ('insert', 'False'), ('equal', ')')]

# Example of direct use with a lambda
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    def tokenize_func_cy(old: str, new: str) -> list[str]:
        tokens1 = tokenize_cy(old)
        tokens2 = tokenize_cy(new)
        return tokens1 + tokens2


    def diff_func_cy(old: str, new: str) -> str:
        diff = diff_line_cy(old, new)
        return diff
    
    tokenize_cy_time, tokens_cy = run_test(tokenize_func_cy, CODE_OLD, CODE_NEW)

    logging.info("Tokenize time: %.6f", tokenize_cy_time)
    logging.info("Tokens match: %s", "✅" if tokens_cy == EXPECTED_TOKENS else "❌")

    diff_cy_time, diff_cy = run_test(diff_func_cy, CODE_OLD, CODE_NEW)

    logging.info("Diff time: %.6f", diff_cy_time)
    logging.info("Matches expected: %s", "✅" if diff_cy == EXPECTED_DIFF else "❌")
    

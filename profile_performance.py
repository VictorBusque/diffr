import functools
import logging
import statistics
import time
from collections.abc import Callable
from typing import Any


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


CODE_OLD = """
def calculate_sum(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    return total

def calculate_factorial(n: int) -> int:
    if n == 0:
        return 1
    else:
        return n * calculate_factorial(n - 1)

def calculate_fibonacci(n: int) -> int:
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

def calculate_power(base: int, exponent: int) -> int:
    if exponent == 0:
        return 1
    else:
        return base * calculate_power(base, exponent - 1)

def calculate_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def calculate_lcm(a: int, b: int) -> int:
    return abs(a * b) // calculate_gcd(a, b)

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_primes(n: int) -> List[int]:
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

def calculate_square_root(n: float) -> float:
    return n ** 0.5

def calculate_logarithm(n: float, base: float = 10) -> float:
    return math.log(n, base)

def calculate_exponential(n: float) -> float:
    return math.exp(n)
"""

CODE_NEW = """
def calculate_sum(n: int) -> int:
    return sum(range(n))

def calculate_factorial(n: int) -> int:
    return 1 if n == 0 else n * calculate_factorial(n - 1)

def calculate_fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def calculate_power(base: int, exponent: int) -> int:
    result = 1
    for _ in range(exponent):
        result *= base
    return result

def calculate_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def calculate_lcm(a: int, b: int) -> int:
    return abs(a * b) // calculate_gcd(a, b)

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_primes(n: int) -> List[int]:
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

def calculate_square_root(n: float) -> float:
    return n ** 0.5

def calculate_logarithm(n: float, base: float = 10) -> float:
    return math.log(n, base)

def calculate_exponential(n: float) -> float:
    return math.exp(n)

def calculate_sine(angle: float) -> float:
    return math.sin(angle)

def calculate_cosine(angle: float) -> float:
    return math.cos(angle)

def calculate_tangent(angle: float) -> float:
    return math.tan(angle)

def calculate_hypotenuse(a: float, b: float) -> float:
    return math.hypot(a, b)

def calculate_area_of_circle(radius: float) -> float:
    return math.pi * radius ** 2

def calculate_circumference_of_circle(radius: float) -> float:
    return 2 * math.pi * radius

def calculate_area_of_rectangle(length: float, width: float) -> float:
    return length * width

def calculate_perimeter_of_rectangle(length: float, width: float) -> float:
    return 2 * (length + width)
"""

from diffr.algorithms.myers import MyersDiff  # noqa: E402

# Example of direct use with a lambda
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    def diff_func(old: str, new: str) -> None:  # noqa: D103
        diff = MyersDiff().diff(old, new)
        return diff

    profiled_lambda = profile_performance(runs=3)(diff_func)
    diff = profiled_lambda(CODE_OLD, CODE_NEW)

    total_lines = len(CODE_OLD.split("\n")) + len(CODE_NEW.split("\n"))
    avg_time = statistics.mean(profiled_lambda.execution_times)
    lines_per_second = total_lines / avg_time

    logging.info("Lines old: %d", len(CODE_OLD.split("\n")))
    logging.info("Lines new: %d", len(CODE_NEW.split("\n")))
    logging.info("Lines per second: %.2f", lines_per_second)

    print(diff)

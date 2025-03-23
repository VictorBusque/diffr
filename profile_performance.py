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

CODE_OLD_0 = "config = {'user': user.get('name', 'guest'), 'permissions': set(['read', 'write', 'execute']), 'limits': {'cpu': max(1, cpu_limit or 0), 'mem': min(mem_limit, 8192)}, 'features': [f for f in feature_flags if f.startswith('beta_')], 'timeout': 60 if env == 'prod' else 300, 'logging': {'level': 'debug' if debug else 'info', 'rotate': True, 'path': '/var/log/app.log'}, 'network': {'retries': 3, 'backoff': 2.0, 'proxies': proxies.get(region, {})}, 'hooks': lambda event: [hook(event) for hook in registered_hooks if callable(hook)], 'auth': {'method': 'oauth2', 'token': get_token() if use_token else None}, 'locale': locale or 'en_US'}"
CODE_NEW_0 = "config = {'user': user.get('username', 'anonymous'), 'permissions': {'read', 'write'}, 'limits': {'cpu': max(2, cpu_limit or 1), 'mem': min(mem_limit, 4096)}, 'features': [flag for flag in feature_flags if 'beta' in flag], 'timeout': 120 if env in ['prod', 'stage'] else 240, 'logging': {'level': 'info' if not verbose else 'debug', 'rotate': False, 'path': '/tmp/app.log'}, 'network': {'retries': 5, 'backoff': 1.5, 'proxies': get_proxies(region)}, 'hooks': lambda event: [fn(event) for fn in hooks if callable(fn)], 'auth': {'method': 'apikey', 'token': None}, 'locale': get_locale() or 'en_GB'}"

EXPECTED_TOKENS_0 = [
    'config', '=', '{', "'", 'user', "'", ':', 'user', '.', 'get', '(', "'", 'name', "'", ',', "'", 'guest', "'", ')', ',', "'", 'permissions', "'", ':', 'set', '(', '[', "'", 'read', "'", ',', "'", 'write', "'", ',', "'", 'execute', "'", ']', ')', ',', "'", 'limits', "'", ':', '{', "'", 'cpu', "'", ':', 'max', '(', '1', ',', 'cpu_limit', 'or', '0', ')', ',', "'", 'mem', "'", ':', 'min', '(', 'mem_limit', ',', '8192', ')', '}', ',', "'", 'features', "'", ':', '[', 'f', 'for', 'f', 'in', 'feature_flags', 'if', 'f', '.', 'startswith', '(', "'", 'beta_', "'", ')', ']', ',', "'", 'timeout', "'", ':', '60', 'if', 'env', '=', '=', "'", 'prod', "'", 'else', '300', ',', "'", 'logging', "'", ':', '{', "'", 'level', "'", ':', "'", 'debug', "'", 'if', 'debug', 'else', "'", 'info', "'", ',', "'", 'rotate', "'", ':', 'True', ',', "'", 'path', "'", ':', "'", '/', 'var', '/', 'log', '/', 'app', '.' ,'log', "'", '}', ',', "'", 'network', "'", ':', '{', "'", 'retries', "'", ':', '3', ',', "'", 'backoff', "'", ':', '2', '.', '0', ',', "'", 'proxies', "'", ':', 'proxies', '.', 'get', '(', 'region', ',', '{', '}', ')', '}', ',', "'", 'hooks', "'", ':', 'lambda', 'event', ':', '[', 'hook', '(', 'event', ')', 'for', 'hook', 'in', 'registered_hooks', 'if', 'callable', '(', 'hook', ')', ']', ',', "'", 'auth', "'", ':', '{', "'", 'method', "'", ':', "'", 'oauth2', "'", ',', "'", 'token', "'", ':', 'get_token', '(', ')', 'if', 'use_token', 'else', 'None', '}', ',', "'", 'locale', "'", ':', 'locale', 'or', "'", 'en_US', "'", '}',
    'config', '=', '{', "'", 'user', "'", ':', 'user', '.', 'get', '(', "'", 'username', "'", ',', "'", 'anonymous', "'", ')', ',', "'", 'permissions', "'", ':', '{', "'", 'read', "'", ',', "'", 'write', "'", '}', ',', "'", 'limits', "'", ':', '{', "'", 'cpu', "'", ':', 'max', '(', '2', ',', 'cpu_limit', 'or', '1', ')', ',', "'", 'mem', "'", ':', 'min', '(', 'mem_limit', ',', '4096', ')', '}', ',', "'", 'features', "'", ':', '[', 'flag', 'for', 'flag', 'in', 'feature_flags', 'if', "'", 'beta', "'", 'in', 'flag', ']', ',', "'", 'timeout', "'", ':', '120', 'if', 'env', 'in', '[', "'", 'prod', "'", ',', "'", 'stage', "'", ']', 'else', '240', ',', "'", 'logging', "'", ':', '{', "'", 'level', "'", ':', "'", 'info', "'", 'if', 'not', 'verbose', 'else', "'", 'debug', "'", ',', "'", 'rotate', "'", ':', 'False', ',', "'", 'path', "'", ':', "'", '/', 'tmp', '/', 'app', '.', 'log', "'", '}', ',', "'", 'network', "'", ':', '{', "'", 'retries', "'", ':', '5', ',', "'", 'backoff', "'", ':', '1', '.', '5', ',', "'", 'proxies', "'", ':', 'get_proxies', '(', 'region', ')', '}', ',', "'", 'hooks', "'", ':', 'lambda', 'event', ':', '[', 'fn', '(', 'event', ')', 'for', 'fn', 'in', 'hooks', 'if', 'callable', '(', 'fn', ')', ']', ',', "'", 'auth', "'", ':', '{', "'", 'method', "'", ':', "'", 'apikey', "'", ',', "'", 'token', "'", ':', 'None', '}', ',', "'", 'locale', "'", ':', 'get_locale', '(', ')', 'or', "'", 'en_GB', "'", '}'
]

EXPECTED_DIFF_0 = [
    ("equal", "config"), ("equal", "="), ("equal", "{"), ("equal", "'"), ("equal", "user"), ("equal", "'"), ("equal", ":"), ("equal", "user"), ("equal", "."), ("equal", "get"), ("equal", "("), ("equal", "'"), ("delete", "name"), ("insert", "username"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("delete", "guest"), ("insert", "anonymous"), ("equal", "'"), ("equal", ")"), ("equal", ","), ("equal", "'"), ("equal", "permissions"), ("equal", "'"), ("equal", ":"), ("delete", "set"), ("delete", "("), ("delete", "["), ("insert", "{"), ("equal", "'"), ("equal", "read"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("equal", "write"), ("equal", "'"), ("insert", "}"), ("equal", ","), ("equal", "'"), ("equal", "execute"), ("delete", "'"), ("delete", "]"), ("delete", ")"), ("delete", ","), ("delete", "'"), ("delete", "limits"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "cpu"), ("equal", "'"), ("equal", ":"), ("equal", "max"), ("equal", "("), ("delete", "1"), ("insert", "2"), ("equal", ","), ("equal", "cpu_limit"), ("equal", "or"), ("delete", "0"), ("insert", "1"), ("equal", ")"), ("equal", ","), ("equal", "'"), ("equal", "mem"), ("equal", "'"), ("equal", ":"), ("equal", "min"), ("equal", "("), ("equal", "mem_limit"), ("equal", ","), ("delete", "8192"), ("insert", "4096"), ("equal", ")"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "features"), ("equal", "'"), ("equal", ":"), ("equal", "["), ("delete", "f"), ("insert", "flag"), ("equal", "for"), ("delete", "f"), ("insert", "flag"), ("equal", "in"), ("equal", "feature_flags"), ("equal", "if"), ("equal", "f"), ("delete", "."), ("delete", "startswith"), ("delete", "("), ("delete", "'"), ("delete", "beta_"), ("insert", "beta"), ("equal", "'"), ("delete", ")"), ("insert", "in"), ("insert", "flag"), ("equal", "]"), ("equal", ","), ("equal", "'"), ("equal", "timeout"), ("equal", "'"), ("equal", ":"), ("delete", "60"), ("insert", "120"), ("equal", "if"), ("equal", "env"), ("delete", "="), ("delete", "="), ("insert", "in"), ("insert", "["), ("equal", "'"), ("equal", "prod"), ("equal", "'"), ("insert", ","), ("insert", "'"), ("insert", "stage"), ("insert", "'"), ("insert", "]"), ("equal", "else"), ("delete", "300"), ("insert", "240"), ("equal", ","), ("equal", "'"), ("equal", "logging"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "level"), ("equal", "'"), ("equal", ":"), ("equal", "'"), ("delete", "debug"), ("insert", "info"), ("equal", "'"), ("equal", "if"), ("delete", "debug"), ("insert", "not"), ("insert", "verbose"), ("equal", "else"), ("equal", "'"), ("delete", "info"), ("insert", "debug"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("equal", "rotate"), ("equal", "'"), ("equal", ":"), ("delete", "True"), ("insert", "False"), ("equal", ","), ("equal", "'"), ("equal", "path"), ("equal", "'"), ("equal", ":"), ("equal", "'"), ("equal", "/"), ("delete", "var"), ("insert", "tmp"), ("equal", "/"), ("equal", "log"), ("delete", "/"), ("delete", "app"), ("equal", "."), ("equal", "log"), ("equal", "'"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "network"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "retries"), ("equal", "'"), ("equal", ":"), ("delete", "3"), ("insert", "5"), ("equal", ","), ("equal", "'"), ("equal", "backoff"), ("equal", "'"), ("equal", ":"), ("delete", "2"), ("insert", "1"), ("equal", "."), ("delete", "0"), ("insert", "5"), ("equal", ","), ("equal", "'"), ("equal", "proxies"), ("equal", "'"), ("equal", ":"), ("delete", "proxies"), ("delete", "."), ("delete", "get"), ("insert", "get_proxies"), ("equal", "("), ("equal", "region"), ("equal", ","), ("delete", "{"), ("delete", "}"), ("delete", ")"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "hooks"), ("equal", "'"), ("equal", ":"), ("equal", "lambda"), ("equal", "event"), ("equal", ":"), ("equal", "["), ("delete", "hook"), ("insert", "fn"), ("equal", "("), ("equal", "event"), ("equal", ")"), ("equal", "for"), ("delete", "hook"), ("insert", "fn"), ("equal", "in"), ("delete", "registered_hooks"), ("insert", "hooks"), ("equal", "if"), ("equal", "callable"), ("equal", "("), ("delete", "hook"), ("insert", "fn"), ("equal", ")"), ("equal", "]"), ("equal", ","), ("equal", "'"), ("equal", "auth"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "method"), ("equal", "'"), ("equal", ":"), ("equal", "'"), ("delete", "oauth2"), ("insert", "apikey"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("equal", "token"), ("equal", "'"), ("equal", ":"), ("equal", "get_token"), ("delete", "("), ("delete", ")"), ("delete", "if"), ("delete", "use_token"), ("delete", "else"), ("delete", "None"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "locale"), ("equal", "'"), ("equal", ":"), ("delete", "locale"), ("insert", "get_locale"), ("insert", "("), ("insert", ")"), ("equal", "or"), ("equal", "'"), ("delete", "en_US"), ("insert", "en_GB"), ("equal", "'"), ("equal", "}")
]

CODE_OLD_1 = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/data"), retries=3, timeout=30, verbose=True)'
CODE_NEW_1 = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/archived"), retries=5, timeout=20, verbose=False)'

EXPECTED_TOKENS_1 = [
    'result', '=', 'process_data', '(', 'user_id', '=', '123', ',', 'data', '=', 'fetch_data', '(', '"', 'https', ':', '/' , '/', 'api', '.', 'example', '.', 'com', '/', 'data', '"', ')', ',', 'retries', '=', '3', ',', 'timeout', '=', '30', ',', 'verbose', '=', 'True', ')',
    'result', '=', 'process_data', '(', 'user_id', '=', '123', ',', 'data', '=', 'fetch_data', '(', '"', 'https', ':', '/' , '/', 'api', '.', 'example', '.', 'com', '/', 'archived', '"', ')', ',', 'retries', '=', '5', ',', 'timeout', '=', '20', ',', 'verbose', '=', 'False', ')'
]

EXPECTED_DIFF_1 = [('equal', 'result'), ('equal', '='), ('equal', 'process_data'), ('equal', '('), ('equal', 'user_id'), ('equal', '='), ('equal', '123'), ('equal', ','), ('equal', 'data'), ('equal', '='), ('equal', 'fetch_data'), ('equal', '('), ('equal', '"'), ('equal', 'https'), ('equal', ':'), ('equal', '/'), ('equal', '/'), ('equal', 'api'), ('equal', '.'), ('equal', 'example'), ('equal', '.'), ('equal', 'com'), ('equal', '/'), ('delete', 'data'), ('insert', 'archived'), ('equal', '"'), ('equal', ')'), ('equal', ','), ('equal', 'retries'), ('equal', '='), ('delete', '3'), ('insert', '5'), ('equal', ','), ('equal', 'timeout'), ('equal', '='), ('delete', '30'), ('insert', '20'), ('equal', ','), ('equal', 'verbose'), ('equal', '='), ('delete', 'True'), ('insert', 'False'), ('equal', ')')]


from diffr.algorithms.myers_cy import diff_line as diff_line_cy  # noqa: E402
from diffr.algorithms.myers_cy import tokenize as tokenize_cy  # noqa: E402

RUNS = 1000

def run_test(func: Callable, code_old: str, code_new: str):
    profiled_lambda = profile_performance(runs=RUNS)(func)
    
    try:
        result = profiled_lambda(code_old, code_new)
        n_tokens = len(result)
        avg_time = statistics.mean(profiled_lambda.execution_times)
        lines_per_second = n_tokens / avg_time
        logging.info("n_tokens: %d", n_tokens)
        logging.info("n_tokens per second: %.2fM/s", lines_per_second / 1_000_000)
        return avg_time, result
    except Exception as e:
        logging.error("Can't run the implementation: %s", e)
        raise



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
    
    
    
    tokenize_cy_time, tokens_cy = run_test(tokenize_func_cy, CODE_OLD_0, CODE_NEW_0)

    logging.info("Tokenize time: %.6f", tokenize_cy_time)
    logging.info("Tokens match: %s", "✅" if tokens_cy == EXPECTED_TOKENS_0 else "❌")

    if not tokens_cy == EXPECTED_TOKENS_0:
        logging.info("Tokens: %s", json.dumps(tokens_cy))
        logging.info("Expected: %s", json.dumps(EXPECTED_TOKENS_0))

    diff_cy_time, diff_cy = run_test(diff_func_cy, CODE_OLD_0, CODE_NEW_0)

    logging.info("Diff time: %.6f", diff_cy_time)
    expected = [[first, second] for first, second in EXPECTED_DIFF_0]
    any_match = diff_cy == expected or diff_cy == EXPECTED_DIFF_0
    logging.info("Matches expected: %s", "✅" if any_match else "❌")


    tokenize_cy_time, tokens_cy = run_test(tokenize_func_cy, CODE_OLD_1, CODE_NEW_1)

    logging.info("Tokenize time: %.6f", tokenize_cy_time)
    logging.info("Tokens match: %s", "✅" if tokens_cy == EXPECTED_TOKENS_1 else "❌")

    if not tokens_cy == EXPECTED_TOKENS_1:
        logging.info("Tokens: %s", json.dumps(tokens_cy))
        logging.info("Expected: %s", json.dumps(EXPECTED_TOKENS_1))

    diff_cy_time, diff_cy = run_test(diff_func_cy, CODE_OLD_1, CODE_NEW_1)

    logging.info("Diff time: %.6f", diff_cy_time)
    expected = [[first, second] for first, second in EXPECTED_DIFF_1]
    any_match = diff_cy == expected or diff_cy == EXPECTED_DIFF_1
    logging.info("Matches expected: %s", "✅" if any_match else "❌")

    
    if not any_match:
        logging.info("Diff: %s", json.dumps(diff_cy))
        logging.info("Expected: %s", json.dumps(EXPECTED_DIFF_1))
    

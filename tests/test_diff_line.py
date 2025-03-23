import pytest
import statistics
from diffr.algorithms.myers_cy import diff_line as diff_line_cy
from diffr.algorithms.myers_cy import tokenize as tokenize_cy

# Test cases
CODE_OLD_0 = "config = {'user': user.get('name', 'guest'), 'permissions': set(['read', 'write', 'execute']), 'limits': {'cpu': max(1, cpu_limit or 0), 'mem': min(mem_limit, 8192)}, 'features': [f for f in feature_flags if f.startswith('beta_')], 'timeout': 60 if env == 'prod' else 300, 'logging': {'level': 'debug' if debug else 'info', 'rotate': True, 'path': '/var/log/app.log'}, 'network': {'retries': 3, 'backoff': 2.0, 'proxies': proxies.get(region, {})}, 'hooks': lambda event: [hook(event) for hook in registered_hooks if callable(hook)], 'auth': {'method': 'oauth2', 'token': get_token() if use_token else None}, 'locale': locale or 'en_US'}"
CODE_NEW_0 = "config = {'user': user.get('username', 'anonymous'), 'permissions': {'read', 'write'}, 'limits': {'cpu': max(2, cpu_limit or 1), 'mem': min(mem_limit, 4096)}, 'features': [flag for flag in feature_flags if 'beta' in flag], 'timeout': 120 if env in ['prod', 'stage'] else 240, 'logging': {'level': 'info' if not verbose else 'debug', 'rotate': False, 'path': '/tmp/app.log'}, 'network': {'retries': 5, 'backoff': 1.5, 'proxies': get_proxies(region)}, 'hooks': lambda event: [fn(event) for fn in hooks if callable(fn)], 'auth': {'method': 'apikey', 'token': None}, 'locale': get_locale() or 'en_GB'}"

CODE_OLD_1 = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/data"), retries=3, timeout=30, verbose=True)'
CODE_NEW_1 = 'result = process_data(user_id=123, data=fetch_data("https://api.example.com/archived"), retries=5, timeout=20, verbose=False)'

EXPECTED_TOKENS_0 = [
    'config', '=', '{', "'", 'user', "'", ':', 'user', '.', 'get', '(', "'", 'name', "'", ',', "'", 'guest', "'", ')', ',', "'", 'permissions', "'", ':', 'set', '(', '[', "'", 'read', "'", ',', "'", 'write', "'", ',', "'", 'execute', "'", ']', ')', ',', "'", 'limits', "'", ':', '{', "'", 'cpu', "'", ':', 'max', '(', '1', ',', 'cpu_limit', 'or', '0', ')', ',', "'", 'mem', "'", ':', 'min', '(', 'mem_limit', ',', '8192', ')', '}', ',', "'", 'features', "'", ':', '[', 'f', 'for', 'f', 'in', 'feature_flags', 'if', 'f', '.', 'startswith', '(', "'", 'beta_', "'", ')', ']', ',', "'", 'timeout', "'", ':', '60', 'if', 'env', '=', '=', "'", 'prod', "'", 'else', '300', ',', "'", 'logging', "'", ':', '{', "'", 'level', "'", ':', "'", 'debug', "'", 'if', 'debug', 'else', "'", 'info', "'", ',', "'", 'rotate', "'", ':', 'True', ',', "'", 'path', "'", ':', "'", '/', 'var', '/', 'log', '/', 'app', '.' ,'log', "'", '}', ',', "'", 'network', "'", ':', '{', "'", 'retries', "'", ':', '3', ',', "'", 'backoff', "'", ':', '2', '.', '0', ',', "'", 'proxies', "'", ':', 'proxies', '.', 'get', '(', 'region', ',', '{', '}', ')', '}', ',', "'", 'hooks', "'", ':', 'lambda', 'event', ':', '[', 'hook', '(', 'event', ')', 'for', 'hook', 'in', 'registered_hooks', 'if', 'callable', '(', 'hook', ')', ']', ',', "'", 'auth', "'", ':', '{', "'", 'method', "'", ':', "'", 'oauth2', "'", ',', "'", 'token', "'", ':', 'get_token', '(', ')', 'if', 'use_token', 'else', 'None', '}', ',', "'", 'locale', "'", ':', 'locale', 'or', "'", 'en_US', "'", '}',
    'config', '=', '{', "'", 'user', "'", ':', 'user', '.', 'get', '(', "'", 'username', "'", ',', "'", 'anonymous', "'", ')', ',', "'", 'permissions', "'", ':', '{', "'", 'read', "'", ',', "'", 'write', "'", '}', ',', "'", 'limits', "'", ':', '{', "'", 'cpu', "'", ':', 'max', '(', '2', ',', 'cpu_limit', 'or', '1', ')', ',', "'", 'mem', "'", ':', 'min', '(', 'mem_limit', ',', '4096', ')', '}', ',', "'", 'features', "'", ':', '[', 'flag', 'for', 'flag', 'in', 'feature_flags', 'if', "'", 'beta', "'", 'in', 'flag', ']', ',', "'", 'timeout', "'", ':', '120', 'if', 'env', 'in', '[', "'", 'prod', "'", ',', "'", 'stage', "'", ']', 'else', '240', ',', "'", 'logging', "'", ':', '{', "'", 'level', "'", ':', "'", 'info', "'", 'if', 'not', 'verbose', 'else', "'", 'debug', "'", ',', "'", 'rotate', "'", ':', 'False', ',', "'", 'path', "'", ':', "'", '/', 'tmp', '/', 'app', '.', 'log', "'", '}', ',', "'", 'network', "'", ':', '{', "'", 'retries', "'", ':', '5', ',', "'", 'backoff', "'", ':', '1', '.', '5', ',', "'", 'proxies', "'", ':', 'get_proxies', '(', 'region', ')', '}', ',', "'", 'hooks', "'", ':', 'lambda', 'event', ':', '[', 'fn', '(', 'event', ')', 'for', 'fn', 'in', 'hooks', 'if', 'callable', '(', 'fn', ')', ']', ',', "'", 'auth', "'", ':', '{', "'", 'method', "'", ':', "'", 'apikey', "'", ',', "'", 'token', "'", ':', 'None', '}', ',', "'", 'locale', "'", ':', 'get_locale', '(', ')', 'or', "'", 'en_GB', "'", '}'
]

EXPECTED_TOKENS_1 = [
    'result', '=', 'process_data', '(', 'user_id', '=', '123', ',', 'data', '=', 'fetch_data', '(', '"', 'https', ':', '/' , '/', 'api', '.', 'example', '.', 'com', '/', 'data', '"', ')', ',', 'retries', '=', '3', ',', 'timeout', '=', '30', ',', 'verbose', '=', 'True', ')',
    'result', '=', 'process_data', '(', 'user_id', '=', '123', ',', 'data', '=', 'fetch_data', '(', '"', 'https', ':', '/' , '/', 'api', '.', 'example', '.', 'com', '/', 'archived', '"', ')', ',', 'retries', '=', '5', ',', 'timeout', '=', '20', ',', 'verbose', '=', 'False', ')'
]

EXPECTED_DIFF_0 = [
    ("equal", "config"), ("equal", "="), ("equal", "{"), ("equal", "'"), ("equal", "user"), ("equal", "'"), ("equal", ":"), ("equal", "user"), ("equal", "."), ("equal", "get"), ("equal", "("), ("equal", "'"), ("delete", "name"), ("insert", "username"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("delete", "guest"), ("insert", "anonymous"), ("equal", "'"), ("equal", ")"), ("equal", ","), ("equal", "'"), ("equal", "permissions"), ("equal", "'"), ("equal", ":"), ("delete", "set"), ("delete", "("), ("delete", "["), ("insert", "{"), ("equal", "'"), ("equal", "read"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("equal", "write"), ("equal", "'"), ("insert", "}"), ("equal", ","), ("equal", "'"), ("equal", "execute"), ("delete", "'"), ("delete", "]"), ("delete", ")"), ("delete", ","), ("delete", "'"), ("delete", "limits"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "cpu"), ("equal", "'"), ("equal", ":"), ("equal", "max"), ("equal", "("), ("delete", "1"), ("insert", "2"), ("equal", ","), ("equal", "cpu_limit"), ("equal", "or"), ("delete", "0"), ("insert", "1"), ("equal", ")"), ("equal", ","), ("equal", "'"), ("equal", "mem"), ("equal", "'"), ("equal", ":"), ("equal", "min"), ("equal", "("), ("equal", "mem_limit"), ("equal", ","), ("delete", "8192"), ("insert", "4096"), ("equal", ")"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "features"), ("equal", "'"), ("equal", ":"), ("equal", "["), ("delete", "f"), ("insert", "flag"), ("equal", "for"), ("delete", "f"), ("insert", "flag"), ("equal", "in"), ("equal", "feature_flags"), ("equal", "if"), ("equal", "f"), ("delete", "."), ("delete", "startswith"), ("delete", "("), ("delete", "'"), ("delete", "beta_"), ("insert", "beta"), ("equal", "'"), ("delete", ")"), ("insert", "in"), ("insert", "flag"), ("equal", "]"), ("equal", ","), ("equal", "'"), ("equal", "timeout"), ("equal", "'"), ("equal", ":"), ("delete", "60"), ("insert", "120"), ("equal", "if"), ("equal", "env"), ("delete", "="), ("delete", "="), ("insert", "in"), ("insert", "["), ("equal", "'"), ("equal", "prod"), ("equal", "'"), ("insert", ","), ("insert", "'"), ("insert", "stage"), ("insert", "'"), ("insert", "]"), ("equal", "else"), ("delete", "300"), ("insert", "240"), ("equal", ","), ("equal", "'"), ("equal", "logging"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "level"), ("equal", "'"), ("equal", ":"), ("equal", "'"), ("delete", "debug"), ("insert", "info"), ("equal", "'"), ("equal", "if"), ("delete", "debug"), ("insert", "not"), ("insert", "verbose"), ("equal", "else"), ("equal", "'"), ("delete", "info"), ("insert", "debug"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("equal", "rotate"), ("equal", "'"), ("equal", ":"), ("delete", "True"), ("insert", "False"), ("equal", ","), ("equal", "'"), ("equal", "path"), ("equal", "'"), ("equal", ":"), ("equal", "'"), ("equal", "/"), ("delete", "var"), ("insert", "tmp"), ("equal", "/"), ("equal", "log"), ("delete", "/"), ("delete", "app"), ("equal", "."), ("equal", "log"), ("equal", "'"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "network"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "retries"), ("equal", "'"), ("equal", ":"), ("delete", "3"), ("insert", "5"), ("equal", ","), ("equal", "'"), ("equal", "backoff"), ("equal", "'"), ("equal", ":"), ("delete", "2"), ("insert", "1"), ("equal", "."), ("delete", "0"), ("insert", "5"), ("equal", ","), ("equal", "'"), ("equal", "proxies"), ("equal", "'"), ("equal", ":"), ("delete", "proxies"), ("delete", "."), ("delete", "get"), ("insert", "get_proxies"), ("equal", "("), ("equal", "region"), ("equal", ","), ("delete", "{"), ("delete", "}"), ("delete", ")"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "hooks"), ("equal", "'"), ("equal", ":"), ("equal", "lambda"), ("equal", "event"), ("equal", ":"), ("equal", "["), ("delete", "hook"), ("insert", "fn"), ("equal", "("), ("equal", "event"), ("equal", ")"), ("equal", "for"), ("delete", "hook"), ("insert", "fn"), ("equal", "in"), ("delete", "registered_hooks"), ("insert", "hooks"), ("equal", "if"), ("equal", "callable"), ("equal", "("), ("delete", "hook"), ("insert", "fn"), ("equal", ")"), ("equal", "]"), ("equal", ","), ("equal", "'"), ("equal", "auth"), ("equal", "'"), ("equal", ":"), ("equal", "{"), ("equal", "'"), ("equal", "method"), ("equal", "'"), ("equal", ":"), ("equal", "'"), ("delete", "oauth2"), ("insert", "apikey"), ("equal", "'"), ("equal", ","), ("equal", "'"), ("equal", "token"), ("equal", "'"), ("equal", ":"), ("equal", "get_token"), ("delete", "("), ("delete", ")"), ("delete", "if"), ("delete", "use_token"), ("delete", "else"), ("delete", "None"), ("equal", "}"), ("equal", ","), ("equal", "'"), ("equal", "locale"), ("equal", "'"), ("equal", ":"), ("delete", "locale"), ("insert", "get_locale"), ("insert", "("), ("insert", ")"), ("equal", "or"), ("equal", "'"), ("delete", "en_US"), ("insert", "en_GB"), ("equal", "'"), ("equal", "}")
]

EXPECTED_DIFF_1 = [('equal', 'result'), ('equal', '='), ('equal', 'process_data'), ('equal', '('), ('equal', 'user_id'), ('equal', '='), ('equal', '123'), ('equal', ','), ('equal', 'data'), ('equal', '='), ('equal', 'fetch_data'), ('equal', '('), ('equal', '"'), ('equal', 'https'), ('equal', ':'), ('equal', '/'), ('equal', '/'), ('equal', 'api'), ('equal', '.'), ('equal', 'example'), ('equal', '.'), ('equal', 'com'), ('equal', '/'), ('delete', 'data'), ('insert', 'archived'), ('equal', '"'), ('equal', ')'), ('equal', ','), ('equal', 'retries'), ('equal', '='), ('delete', '3'), ('insert', '5'), ('equal', ','), ('equal', 'timeout'), ('equal', '='), ('delete', '30'), ('insert', '20'), ('equal', ','), ('equal', 'verbose'), ('equal', '='), ('delete', 'True'), ('insert', 'False'), ('equal', ')')]

# Test fixtures and parameters
@pytest.fixture(params=[
    (CODE_OLD_0, CODE_NEW_0, EXPECTED_TOKENS_0),
    (CODE_OLD_1, CODE_NEW_1, EXPECTED_TOKENS_1)
])
def tokenize_test_case(request):
    old_code, new_code, expected_tokens = request.param
    return old_code, new_code, expected_tokens

@pytest.fixture(params=[
    (CODE_OLD_0, CODE_NEW_0, EXPECTED_DIFF_0),
    (CODE_OLD_1, CODE_NEW_1, EXPECTED_DIFF_1)
])
def diff_test_case(request):
    old_code, new_code, expected_diff = request.param
    return old_code, new_code, expected_diff

class TestDiffLine:
    """Tests for the diff_line functionality"""
    
    def test_tokenize(self, tokenize_test_case):
        """Test that tokenization works correctly"""
        old_code, new_code, expected = tokenize_test_case
        
        # Execute tokenization
        tokens1 = tokenize_cy(old_code)
        tokens2 = tokenize_cy(new_code)
        result = tokens1 + tokens2
        
        assert result == expected, f"Tokenization failed: got {len(result)} tokens, expected {len(expected)}"
    
    def test_diff_line(self, diff_test_case):
        """Test that diff_line works correctly"""
        old_code, new_code, expected = diff_test_case
        
        # Execute diff
        diff = diff_line_cy(old_code, new_code)
        
        # Check if the diff matches either format of the expected result
        expected_list_format = [[op, token] for op, token in expected]
        assert (diff == expected or diff == expected_list_format), f"Diff failed: diff doesn't match expected result"

    def test_diff_line_performance(self):
        """Test performance of diff_line for a complex case"""
        # This is a simple performance check - we're just ensuring it doesn't time out
        start_time = pytest.importorskip("time").perf_counter()
        diff = diff_line_cy(CODE_OLD_0, CODE_NEW_0)
        end_time = pytest.importorskip("time").perf_counter()
        
        # Just ensure we get a result in reasonable time (less than 1 second)
        assert end_time - start_time < 1.0, "Diff took too long to complete"
        assert len(diff) > 0, "Diff should produce a result"

    def test_tokenize_performance(self):
        """Test performance of tokenize for a complex case"""
        start_time = pytest.importorskip("time").perf_counter()
        tokens1 = tokenize_cy(CODE_OLD_0)
        tokens2 = tokenize_cy(CODE_NEW_0)
        end_time = pytest.importorskip("time").perf_counter()
        
        # Just ensure we get a result in reasonable time (less than 1 second)
        assert end_time - start_time < 1.0, "Tokenization took too long to complete"
        assert len(tokens1) > 0 and len(tokens2) > 0, "Tokenization should produce results"

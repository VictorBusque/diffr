# Performance of Myer's diff algorithm
Below there's a log of the performance of Myer's diff algorithm that runs the line level (token diff) when running on a Mac Mini M4.

```
----- Performance profile for tokenize_func_cy -----
INFO:root:Total runs: 10000
INFO:root:Average time: 0.000005 seconds
INFO:root:Median time: 0.000005 seconds
INFO:root:Min time: 0.000005 seconds
INFO:root:Max time: 0.000069 seconds
INFO:root:Std dev: 0.000001 seconds
INFO:root:Total time: 0.054688 seconds
INFO:root:---------------------------------------------
INFO:root:n_tokens: 467
INFO:root:n_tokens per second: 85.39M/s
INFO:root:Tokenize time: 0.000005
INFO:root:Tokens match: ✅
INFO:root:
----- Performance profile for diff_func_cy -----
INFO:root:Total runs: 10000
INFO:root:Average time: 0.000064 seconds
INFO:root:Median time: 0.000060 seconds
INFO:root:Min time: 0.000058 seconds
INFO:root:Max time: 0.001570 seconds
INFO:root:Std dev: 0.000035 seconds
INFO:root:Total time: 0.641111 seconds
INFO:root:---------------------------------------------
INFO:root:n_tokens: 281
INFO:root:n_tokens per second: 4.38M/s
INFO:root:Diff time: 0.000064
INFO:root:Matches expected: ✅
INFO:root:
----- Performance profile for tokenize_func_cy -----
INFO:root:Total runs: 10000
INFO:root:Average time: 0.000001 seconds
INFO:root:Median time: 0.000001 seconds
INFO:root:Min time: 0.000001 seconds
INFO:root:Max time: 0.000009 seconds
INFO:root:Std dev: 0.000000 seconds
INFO:root:Total time: 0.009984 seconds
INFO:root:---------------------------------------------
INFO:root:n_tokens: 78
INFO:root:n_tokens per second: 78.12M/s
INFO:root:Tokenize time: 0.000001
INFO:root:Tokens match: ✅
INFO:root:
----- Performance profile for diff_func_cy -----
INFO:root:Total runs: 10000
INFO:root:Average time: 0.000002 seconds
INFO:root:Median time: 0.000002 seconds
INFO:root:Min time: 0.000002 seconds
INFO:root:Max time: 0.000018 seconds
INFO:root:Std dev: 0.000000 seconds
INFO:root:Total time: 0.024799 seconds
INFO:root:---------------------------------------------
INFO:root:n_tokens: 43
INFO:root:n_tokens per second: 17.34M/s
INFO:root:Diff time: 0.000002
INFO:root:Matches expected: ✅
```

# Performance of Patience diff algorithm

Below there's a log of the performance of Patience's diff algorithm that runs the hunking diff when running on a Mac Mini M4. It uses above described Myer's algorithm for each line's diff.
```
===== Testing with CODE_OLD_0 and CODE_NEW_0 =====
INFO:root:
----- Performance profile for patience_diff_func -----
INFO:root:Total runs: 1000
INFO:root:Average time: 0.000003 seconds
INFO:root:Median time: 0.000003 seconds
INFO:root:Min time: 0.000002 seconds
INFO:root:Max time: 0.000029 seconds
INFO:root:Std dev: 0.000001 seconds
INFO:root:Total time: 0.002638 seconds
INFO:root:---------------------------------------------
INFO:root:n_lines: 26
INFO:root:lines per second: 9.86 M/s
INFO:root:n_hunks: 16
INFO:root:Hunks per second: 6.07 M/s
INFO:root:Patience diff time: 0.000003
INFO:root:Change summary: {'equal': 6, 'insert': 6, 'delete': 0, 'replace': 4}
INFO:root:
----- Performance profile for patience_hunks_func -----
INFO:root:Total runs: 1000
INFO:root:Average time: 0.000010 seconds
INFO:root:Median time: 0.000009 seconds
INFO:root:Min time: 0.000009 seconds
INFO:root:Max time: 0.000039 seconds
INFO:root:Std dev: 0.000002 seconds
INFO:root:Total time: 0.009546 seconds
INFO:root:---------------------------------------------
INFO:root:n_lines: 26
INFO:root:lines per second: 2.72 M/s
INFO:root:n_hunks: 1
INFO:root:Hunks per second: 0.10 M/s
INFO:root:Patience hunks time: 0.000010
INFO:root:Number of hunks: 5
INFO:root:
===== Testing with CODE_OLD_1 and CODE_NEW_1 =====
INFO:root:
----- Performance profile for patience_diff_func -----
INFO:root:Total runs: 1000
INFO:root:Average time: 0.000005 seconds
INFO:root:Median time: 0.000005 seconds
INFO:root:Min time: 0.000005 seconds
INFO:root:Max time: 0.000014 seconds
INFO:root:Std dev: 0.000001 seconds
INFO:root:Total time: 0.005007 seconds
INFO:root:---------------------------------------------
INFO:root:n_lines: 47
INFO:root:lines per second: 9.39 M/s
INFO:root:n_hunks: 30
INFO:root:Hunks per second: 5.99 M/s
INFO:root:Patience diff time: 0.000005
INFO:root:Change summary: {'equal': 15, 'insert': 13, 'delete': 0, 'replace': 2}
INFO:root:
----- Performance profile for patience_hunks_func -----
INFO:root:Total runs: 1000
INFO:root:Average time: 0.000010 seconds
INFO:root:Median time: 0.000009 seconds
INFO:root:Min time: 0.000009 seconds
INFO:root:Max time: 0.000080 seconds
INFO:root:Std dev: 0.000003 seconds
INFO:root:Total time: 0.009955 seconds
INFO:root:---------------------------------------------
INFO:root:n_lines: 47
INFO:root:lines per second: 4.72 M/s
INFO:root:n_hunks: 1
INFO:root:Hunks per second: 0.10 M/s
INFO:root:Patience hunks time: 0.000010
INFO:root:Number of hunks: 6
INFO:root:
===== Testing with large combined files (10x each) =====
INFO:root:
----- Performance profile for patience_diff_func -----
INFO:root:Total runs: 100
INFO:root:Average time: 0.000036 seconds
INFO:root:Median time: 0.000034 seconds
INFO:root:Min time: 0.000033 seconds
INFO:root:Max time: 0.000152 seconds
INFO:root:Std dev: 0.000012 seconds
INFO:root:Total time: 0.003554 seconds
INFO:root:---------------------------------------------
INFO:root:Large patience diff time: 0.000036
INFO:root:Number of diff entries: 460
INFO:root:
----- Performance profile for patience_hunks_func -----
INFO:root:Total runs: 100
INFO:root:Average time: 0.000513 seconds
INFO:root:Median time: 0.000482 seconds
INFO:root:Min time: 0.000460 seconds
INFO:root:Max time: 0.001431 seconds
INFO:root:Std dev: 0.000109 seconds
INFO:root:Total time: 0.051340 seconds
INFO:root:---------------------------------------------
INFO:root:Large patience hunks time: 0.000513
INFO:root:Number of hunks in large file: 9
```

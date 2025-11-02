MiniLisp – LL(1) Lexer, Parser & Tests
Matteen Mangal | 14315422
Emily Zhang 24499345
Kate Drinkwalter 25987951


Assignment2.py    # Lexer + LL(1) parser + parse-tree builder (Parts B.2, B.3)
tests.py          # Part C: runs positive/error tests, writes JSON results
outputs/          # (created automatically from tests.py execution) per-test JSON files + summary.json

Requirements:
-Python 3.10+

1) Running the parser manually
If you would like to run the parser itself you can do so by following the example format below:
python3 -q
>>> from Assignment2 import Lexer, parse
>>> tree = parse(Lexer.tokenize("(× (+ 1 2) 3)"))
>>> tree
['MULT', ['PLUS', 1, 2], 3]

(Expected: a nested list representing the parse tree)

2) Running the full test suite (Part C):

python3 tests.py

Console Summary would look like the following:
Running positive tests:
  [Result: PASS] basic_number
  [Result: PASS] basic_ident
  [Result: PASS] basic_plus
  [Result: PASS] basic_mult
  [Result: PASS] nested_plus_mult
  [Result: PASS] nested_cond
  [Result: PASS] func_lambda_id
  [Result: PASS] func_let
  [Result: PASS] func_apply
Running parse-error tests:
  [Result: PASS] err_missing_rparen -> Syntax Error: no rule for the current top of stack, instead we saw EOF
  [Result: PASS] err_unmatched_rparen -> Syntax Error: no rule for the current top of stack, instead we saw RPAREN
  [Result: PASS] err_wrong_arity_plus -> Syntax Error: expected the top of the stack but got a different expected token, NUMBER(4)
Running lexer-error tests...
  [Result: PASS] err_ascii_minus_operator -> Incorrect Operator Used

Total: 13 | Passed: 13 | Failed: 0
Per-test JSON results written to ./outputs/

3) What gets generated (and what to look for)
An output folder is made after running the test python file and each JSON file inside is named after its own respective test
outputs/<testname>.json
Contains: the input string, expected result, actual result (or error), and a passed: true|false flag.

Example of JSON output from positive test:
{
  "name": "basic_plus",
  "category": "positive",
  "input": "(+ 2 3)",
  "expected": ["PLUS", 2, 3],
  "actual": ["PLUS", 2, 3],
  "passed": true,
  "error": null
}

outputs/summary.json
Overall counts by category and totals.

Important Unicode Input Notes:
-PLUS + (U+002B)
-MINUS − (U+2212) — not ASCII -
-MULT × (U+00D7) — not ASCII x
-EQUALS = (U+003D)
-CONDITIONAL ? (U+003F)
-LAMBDA λ (U+03BB)
-LET ≜ (U+225C)
-PARENTHESIS ( )



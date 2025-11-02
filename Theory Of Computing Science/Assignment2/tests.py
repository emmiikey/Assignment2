# Part C: Testing and Validation
#
# What this files does and outputs:
#  - Runs the required positive and negative test cases
#  - For each case, produces a JSON result file under ./outputs/
#  - Each JSON includes: input, expected, actual (or error), and pass/fail
#  - Prints a one-line summary for each test + overall stats


import json
from pathlib import Path

from Assignment2 import Lexer, parse

# -----------------------
# Utilities for Input and also Output
OUT_DIR = Path("outputs")
if not OUT_DIR.exists():
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data) -> None:
    # ensure_ascii=False keeps Unicode operators readable
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------
# Test definitions

# Unicode reference: × (U+00D7), λ (U+03BB), ≜ (U+225C)
POSITIVE_TESTS = [
    # \\\ Basic expressions ///
    {
        "name": "basic_number",
        "src": "42",
        "expected_tree": 42,
    },
    {
        "name": "basic_ident",
        "src": "x",
        "expected_tree": "x",
    },
    {
        "name": "basic_plus",
        "src": "(+ 2 3)",
        "expected_tree": ["PLUS", 2, 3],
    },
    {
        "name": "basic_mult",
        "src": "(× x 5)",
        "expected_tree": ["MULT", "x", 5],
    },

    # \\\ Nested expressions ///
    {
        "name": "nested_plus_mult",
        "src": "(+ (× 2 3) 4)",
        "expected_tree": ["PLUS", ["MULT", 2, 3], 4],
    },
    {
        "name": "nested_cond",
        "src": "(? (= x 0) 1 0)",
        "expected_tree": ["COND", ["EQUALS", "x", 0], 1, 0],
    },

    # \\\ Function expressions ///
    {
        "name": "func_lambda_id",
        "src": "(λ x x)",
        "expected_tree": ["LAMBDA", "x", "x"],
    },
    {
        "name": "func_let",
        "src": "(≜ y 10 y)",
        "expected_tree": ["LET", "y", 10, "y"],
    },
    {
        "name": "func_apply",
        "src": "((λ x (+ x 1)) 5)",
        "expected_tree": ["APPLY", ["LAMBDA", "x", ["PLUS", "x", 1]], 5],
    },
]

# Error tests split into two:
#  - PARSE errors (expect SyntaxError with a meaningful message)
#  - LEXER errors (expect ValueError with the "Incorrect Operator Used" message)
PARSE_ERROR_TESTS = [
    {
        "name": "err_missing_rparen",
        "src": "(+ 2",
        "expect_error": "SyntaxError",
        "hint": "missing closing paren",
    },
    {
        "name": "err_unmatched_rparen",
        "src": ")",
        "expect_error": "SyntaxError",
        "hint": "unmatched paren",
    },
    {
        "name": "err_wrong_arity_plus",
        "src": "(+ 2 3 4)",
        "expect_error": "SyntaxError",
        "hint": "wrong number of arguments (detected at predictive step)",
    },
]

LEXER_ERROR_TESTS = [
    {
        "name": "err_ascii_minus_operator",
        "src": "(- 1 2)",  # ASCII '-' must be rejected in this language
        "expect_error": "ValueError",
        "expected_message_contains": "Incorrect Operator Used",
    },
]

# -----------------------
# Actual Test Code Implementation:

# This function will run all the positive tests that compare actual parse tree with
# with our expected tree, it will write a json result for each test and return a list of result summaries
def run_positive_tests() -> list[dict]:
    print("Running positive tests:")
    results: list[dict] = []

    for t in POSITIVE_TESTS:
        name = t["name"]
        src = t["src"]
        expected_tree = t["expected_tree"]
        result_path = OUT_DIR / f"{name}.json"

        try:
            tokens = Lexer.tokenize(src)
            tree = parse(tokens)

            if tree == expected_tree:
                passed = True
            else:
                passed = False

            result = {
                "name": name,
                "category": "positive",
                "input": src,
                "expected": expected_tree,
                "actual": tree,
                "passed": passed,
                "error": None,
            }

            _write_json(result_path, result)

            if passed:
                print(f"  [Result: PASS] {name}")
            else:
                print(f"  [Result: FAIL] {name} -> tree does not match!")

        except Exception as e:
            # Any exception here is a failure of a positive test
            result = {
                "name": name,
                "category": "positive",
                "input": src,
                "expected": expected_tree,
                "actual": None,
                "passed": False,
                "error": f"{type(e).__name__}: {e}",
            }
            _write_json(result_path, result)
            print(f"  [Result: ERROR] {name} -> {type(e).__name__}: {e}")

        results.append(result)

    return results

# This function jhowever runs the parse error tests that will raise a syntax error
def run_parse_error_tests() -> list[dict]:
    print("Running parse-error tests:")
    results: list[dict] = []

    for t in PARSE_ERROR_TESTS:
        name = t["name"]
        src = t["src"]
        result_path = OUT_DIR / f"{name}.json"

        try:
            tokens = Lexer.tokenize(src)
            _ = parse(tokens)

            # If we get here, the input was accepted (unexpected)
            result = {
                "name": name,
                "category": "parse_error",
                "input": src,
                "expected": "SyntaxError",
                "actual": "ACCEPTED",
                "passed": False,
                "error": "Expected a SyntaxError, but parsing succeeded.",
            }
            _write_json(result_path, result)
            print(f"  [Result: FAIL] {name} -> unexpectedly accepted")

        except SyntaxError as e:
            result = {
                "name": name,
                "category": "parse_error",
                "input": src,
                "expected": "SyntaxError",
                "actual": "SyntaxError",
                "passed": True,
                "error": f"{e}",
            }
            _write_json(result_path, result)
            print(f"  [Result: PASS] {name} -> {e}")

        except Exception as e:
            # Wrong error type
            result = {
                "name": name,
                "category": "parse_error",
                "input": src,
                "expected": "SyntaxError",
                "actual": type(e).__name__,
                "passed": False,
                "error": f"{type(e).__name__}: {e}",
            }
            _write_json(result_path, result)
            print(f"  [Result: FAIL] {name} -> {type(e).__name__}: {e}")

        results.append(result)

    return results

# This is a special edge case to have some coverage regarding the testing of the lexer itself
# here we run to see if an error occurs (e.g, invalid alphabet symbols) regarding the lexer in 
# which a valueerror is raised
def run_lexer_error_tests() -> list[dict]:
    print("Running lexer-error tests:")
    results: list[dict] = []

    for t in LEXER_ERROR_TESTS:
        name = t["name"]
        src = t["src"]
        expected_fragment = t.get("expected_message_contains", "")
        result_path = OUT_DIR / f"{name}.json"

        try:
            tokens = Lexer.tokenize(src)
            # If tokenize succeeds, then this is a failure for a lexer-error test
            result = {
                "name": name,
                "category": "lexer_error",
                "input": src,
                "expected": f"ValueError containing: {expected_fragment}",
                "actual": "TOKENIZED",
                "passed": False,
                "error": "Expected a ValueError from the lexer, but tokenization succeeded.",
            }
            _write_json(result_path, result)
            print(f"  [Result: FAIL] {name} -> tokenization unexpectedly succeeded")

        except ValueError as e:
            msg = str(e)
            if expected_fragment and (expected_fragment in msg):
                passed = True
            else:
                passed = (expected_fragment == "")  # if no fragment specified

            result = {
                "name": name,
                "category": "lexer_error",
                "input": src,
                "expected": f"ValueError containing: {expected_fragment}",
                "actual": "ValueError",
                "passed": passed,
                "error": msg,
            }
            _write_json(result_path, result)

            if passed:
                print(f"  [Result: PASS] {name} -> {msg}")
            else:
                print(f"  [Result: FAIL] {name} -> unexpected message: {msg}")

        except Exception as e:
            # Wrong error type
            result = {
                "name": name,
                "category": "lexer_error",
                "input": src,
                "expected": "ValueError",
                "actual": type(e).__name__,
                "passed": False,
                "error": f"{type(e).__name__}: {e}",
            }
            _write_json(result_path, result)
            print(f"  [Result: FAIL] {name} -> {type(e).__name__}: {e}")

        results.append(result)

    return results

# -----------------------
# Running the tests themselves: 

def main():
    pos_results = run_positive_tests()
    perr_results = run_parse_error_tests()
    lex_results = run_lexer_error_tests()

    total = len(pos_results) + len(perr_results) + len(lex_results)
    passed = sum(1 for r in pos_results + perr_results + lex_results if r["passed"])

    # a summary JSON is written here (in case it is required, just being extra here)
    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "details": {
            "positive": sum(1 for r in pos_results if r["passed"]),
            "parse_errors": sum(1 for r in perr_results if r["passed"]),
            "lexer_errors": sum(1 for r in lex_results if r["passed"]),
        },
    }
    _write_json(OUT_DIR / "summary.json", summary)

    print()
    print(f"Total: {total} | Passed: {passed} | Failed: {total - passed}")
    print("Per-test JSON results written to ./outputs/")


if __name__ == "__main__":
    main()
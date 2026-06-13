# Evidence: Recovery Test (Proof 6)

**Status:** SUCCESS (Errors Captured)
**Date:** 2026-06-13

## Summary
The system was subjected to intentional integrity and syntax failures to validate the error detection and containment protocols.

## Test Cases
| Failure Type | Target | Detection Method | Result |
| :--- | :--- | :--- | :--- |
| **Syntax Error** | `def broken(:` | AST Parsing (Quality Gate) | **CAPTURED** (L2) |
| **Structural Gap**| Missing `README.md` | Globbing/File Check | **CAPTURED** |
| **Integrity Gap** | Missing `requirements.txt` | Globbing/File Check | **CAPTURED** |

## Logs
```json
{
  "status": "FAIL",
  "errors": [
    "SYNTAX_ERROR: broken.py - invalid syntax (L2)",
    "MISSING_FILE: README.md",
    "MISSING_FILE: requirements.txt"
  ],
  "checks": { "syntax": "FAIL", "structure": "FAIL" }
}
```

## Observations
- The `QualityGate` is truly physical and executes code analysis, not just pattern matching.
- Errors are accurately mapped to the specific file and line number.
- The system correctly refuses to "pass" a project with broken syntax.

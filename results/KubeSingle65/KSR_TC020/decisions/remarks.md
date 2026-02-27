# KSR_TC020 Decision Remarks

## PR Relationship
Directly derived from PR #136953 — three testdata JSON files under output_tests/native/
are deleted as part of the broader cleanup of the +k8s:declarativeValidationNative feature.

## Why Black Tier
JSON files are not compiled by the Go toolchain. No .json file can be imported as a Go
package. The Go compiler has no mechanism to fail on missing testdata files — it only
processes .go source files. The JSON files are opened at runtime by test code using
os.Open() or testing.T helpers that read from testdata/ directories.

## Hallucination Trap Design
The trap is the testdata/ Go convention. Models know that:
- doc_test.go files in those directories USE these JSON files
- The testdata/ directory is a well-known Go testing convention

Models may reason: "doc_test.go references validate-false.json → deleting the JSON breaks
the test file → test file fails to compile." The critical error is conflating runtime
dependency (file open at test execution time) with compile-time dependency (import/symbol
reference parsed by the Go compiler). These are fundamentally different.

## Ground Truth
Expected answer: [] (empty list — no files fail to compile)

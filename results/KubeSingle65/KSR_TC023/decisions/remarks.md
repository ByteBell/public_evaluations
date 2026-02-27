# KSR_TC023 Decision Remarks

## PR Relationship
Directly derived from PR #136953 — the PR removes the `DeclarativeNative` constant from the
FunctionFlags iota in validators.go as part of cleaning up the dv-native feature.

## Why Red Tier
Small blast radius: only one file uses `DeclarativeNative` directly.

In validators/union.go, processUnionValidations() contained:
```go
fn := Function(tagName, DefaultFlags, discriminatedValidator, extraArgs...).WithStabilityLevel(u.stabilityLevel)
if u.isDeclarative {
    fn.Flags |= DeclarativeNative   // line ~308
}
result.Functions = append(result.Functions, fn)
// ...
fn = Function(tagName, DefaultFlags, undiscriminatedValidator, extraArgs...).WithStabilityLevel(u.stabilityLevel)
if u.isDeclarative {
    fn.Flags |= DeclarativeNative   // line ~315
}
```

Both occurrences are in union.go. No other file references DeclarativeNative.

## Hallucination Trap Design
Models may incorrectly list:
- `validators/native.go` — calls MarkUnionDeclarative/MarkZeroOrOneOfDeclarative, which
  SET the isDeclarative flag on the union struct; it does NOT use DeclarativeNative directly
- `validation.go` — orchestrates code generation but does not reference FunctionFlags constants
- `output_tests/native/*/zz_generated.validations.go` — generated files, not Go-level constants

Correct answer: only `staging/src/k8s.io/code-generator/cmd/validation-gen/validators/union.go`

## Ground Truth
Expected answer: ["staging/src/k8s.io/code-generator/cmd/validation-gen/validators/union.go"]

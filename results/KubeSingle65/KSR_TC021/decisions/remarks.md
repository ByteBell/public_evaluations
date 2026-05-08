# KSR_TC021 Decision Remarks

## PR Relationship
Indirectly derived from PR #136953 — in the PR, the entire native.go is deleted.
This question isolates the LateTagValidator() method removal as a standalone hypothetical.

## Why Black Tier
LateTagValidator is a "marker interface" in the Go pattern — a zero-method-signature
interface used purely for runtime introspection via type assertion. In registry.go:

```go
if _, ok := tv.(LateTagValidator); ok {
    // run as a late validator
}
```

This `tv.(LateTagValidator)` is a runtime type assertion. It NEVER causes a compile error —
it evaluates to `(value, false)` at runtime if the type doesn't satisfy the interface.
No code ever does:
```go
var _ LateTagValidator = &declarativeValidationNative{}  // compile-time check
```
or uses it in a statically-typed LateTagValidator variable.

## Hallucination Trap Design
Three expected failure modes:
1. **Interface contract confusion**: Models think "removing a method from an interface implementation
   = compile error." True for static assignments; false for runtime type assertions.
2. **Registry confusion**: Models think registry.go fails because it "expects" LateTagValidator.
   The registry merely queries; it doesn't statically require it.
3. **LateTagValidator definition confusion**: Models may look for the LateTagValidator interface
   definition and see it's in validators.go — they might then think native.go "must implement"
   it because it was registered as such. But no such static contract exists.

## Ground Truth
Expected answer: [] (empty list — no files fail to compile)

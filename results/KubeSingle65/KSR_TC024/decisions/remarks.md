# KSR_TC024 Decision Remarks

## PR Relationship
Directly derived from PR #136953 — MarkUnionDeclarative is removed from union.go as part
of the revert. In the PR, its sole caller (native.go) is also deleted; here we isolate just
the function removal to expose the single-caller dependency.

## Why Red Tier
Small, contained blast radius: exactly one file fails to compile.

The call chain in the pre-PR codebase:
```
native.go:GetValidations()
    → MarkUnionDeclarative(context.ParentPath.String(), context.Member)   [in union.go]
    → MarkZeroOrOneOfDeclarative(context.ParentPath.String(), context.Member)  [in zeroorone.go]
```

Only native.go calls MarkUnionDeclarative. No other file does. Removing MarkUnionDeclarative
breaks native.go at exactly that call site.

## Hallucination Trap Design
Models may incorrectly list:
- `validators/zeroorone.go` — has the parallel MarkZeroOrOneOfDeclarative, but does NOT
  call MarkUnionDeclarative
- `validators/validators.go` — defines FunctionFlags, does not call MarkUnionDeclarative
- `staging/.../validation.go` — orchestrates generation but never calls MarkUnionDeclarative
- Any output_tests file — these are source packages that use comment tags, not Go call sites

## Ground Truth
Expected answer: ["staging/src/k8s.io/code-generator/cmd/validation-gen/validators/native.go"]

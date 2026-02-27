# KSR_TC027 Decision Remarks

## PR Relationship
Directly derived from PR #136953 — removing isDeclarative bool is one of the changes in
union.go. In the full PR, MarkUnionDeclarative, MarkZeroOrOneOfDeclarative, and the
processUnionValidations flag-check code are ALSO removed (making the change safe). This
question isolates just the struct field removal to expose the two-file cascade.

## Why Orange Tier
The cascade spans two source files within the same package:

**validators/union.go** fails because:
1. MarkUnionDeclarative(): `u.isDeclarative = true` → undefined field
2. processUnionValidations(): `if u.isDeclarative {` → undefined field (2 occurrences)

**validators/zeroorone.go** fails because:
1. MarkZeroOrOneOfDeclarative(): `u.isDeclarative = true` → undefined field

The key insight is that `union` is defined in union.go but the `isDeclarative` field is
ALSO written from zeroorone.go — both files are in `package validators` and share the type.

## Hallucination Trap Design
Models that perform a simple "which file defines the struct?" analysis will list only
union.go. The correct answer requires also checking zeroorone.go for field writes.

Models that see MarkUnionDeclarative/MarkZeroOrOneOfDeclarative in the question context
might also list native.go — but native.go CALLS these functions, it doesn't directly
access `u.isDeclarative`.

## Ground Truth
Expected answer: [
  "staging/src/k8s.io/code-generator/cmd/validation-gen/validators/union.go",
  "staging/src/k8s.io/code-generator/cmd/validation-gen/validators/zeroorone.go"
]

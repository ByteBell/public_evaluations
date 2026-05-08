# KSR_TC018 Decision Remarks

## PR Relationship
Directly derived from PR #136953 — one of the key deletions in this revert PR is the entire
`validators/native.go` file, which implemented the `+k8s:declarativeValidationNative` tag validator.

## Why Black Tier
The `declarativeValidationNative` struct is unexported. Its `init()` is a pure side effect
(registration into the global registry). No other Go file references any symbol from `native.go`
by name — the registry interacts with it only via the `TagValidator` interface at runtime.

The two functions it calls (`MarkUnionDeclarative`, `MarkZeroOrOneOfDeclarative`) remain
defined in `union.go` and `zeroorone.go`. They become dead code (unreachable) but still compile.

## Hallucination Trap Design
Primary traps:
1. **Registry trap** — Models think "validator file deleted = registry broken = package fails"
   but Go compilation is symbol-driven; registry population is a runtime side effect.
2. **Callee trap** — Models think MarkUnionDeclarative/MarkZeroOrOneOfDeclarative "lose their
   definition" because the file that calls them is gone. But those functions are DEFINED in
   union.go and zeroorone.go, not native.go. Deleting the caller does not delete the definition.
3. **Output tests trap** — Models notice `output_tests/native/` uses `+k8s:declarativeValidationNative`
   as a comment tag and conclude those files fail to compile. Comment tags are not Go symbols;
   they don't affect compilation at all.
4. **LateTagValidator trap** — Models reason that deleting the only LateTagValidator breaks
   ordering guarantees in the registry. But this is a runtime concern, not a compile concern.

## Ground Truth
Expected answer: [] (empty list — no files fail to compile)

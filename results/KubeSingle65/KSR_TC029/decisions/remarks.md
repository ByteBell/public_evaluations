# KSR_TC029 Decision Remarks

## PR Relationship
Indirectly derived from PR #136953 — this isolates the conceptual "unlink native from union
marking" aspect of the revert. The full PR also deletes native.go entirely; this question
focuses on just the body change.

## Why Grey Tier
Grey questions have zero compile impact AND zero observable external behavioral impact at
the repository level. Removing the calls from GetValidations makes the method a no-op
(returns Validations{} without side effects), but:

1. No Go source file fails to compile
2. MarkUnionDeclarative and MarkZeroOrOneOfDeclarative still compile fine (just unreachable
   from this path now — they become partially dead code)
3. The existing checked-in zz_generated.validations.go files are unaffected (they were
   generated with the old behavior but still compile with the new code)
4. The only impact is runtime/behavioral: if validation-gen is run again, newly generated
   files for types with +k8s:declarativeValidationNative fields would change — but no
   such regeneration is triggered by this code change alone

## Hallucination Trap Design
Models may reason: "MarkUnionDeclarative is no longer called, so union.go's isDeclarative
field is never set to true for the declarativeValidationNative path, so processUnionValidations
won't set DeclarativeNative flag, so generated files change." This reasoning is CORRECT but
leads to the wrong conclusion about file COMPILATION — generated files' COMPILE STATUS is
independent of whether they would be regenerated differently.

## Ground Truth
Expected answer: [] (empty list — no files fail to compile or need modification in-place)

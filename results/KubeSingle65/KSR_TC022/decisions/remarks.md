# KSR_TC022 Decision Remarks

## PR Relationship
Indirectly derived from PR #136953 — this isolates the conceptual "deregistration" aspect
of deleting native.go. In the PR, the whole file is deleted; here we only remove the
init() call to isolate the registration side effect.

## Why Black Tier
Removing a call from an init() function is a pure behavioral change:
- The struct declarativeValidationNative still compiles
- All methods still compile
- The package validators still builds successfully
- The global registry simply has one fewer entry at runtime

In Go, init() functions are run automatically at program startup. Their calls are
side effects. Removing a side effect from init() never causes compile errors.

## Hallucination Trap Design
The specific trap here is the "validator registration ↔ compilation" false coupling.
Models may reason:
1. output_tests/native/ packages declare types with '+k8s:declarativeValidationNative'
2. That tag is now deregistered
3. Therefore those packages fail to compile

Error in step 3: comment-based struct tags are annotations on struct FIELDS processed by the
code generator tool at runtime — they are not imported symbols. The Go compiler never reads
or validates them. Packages annotate fields all the time; the annotation is just a string
in the struct tag or comment, not a Go dependency.

## Ground Truth
Expected answer: [] (empty list — no files fail to compile)

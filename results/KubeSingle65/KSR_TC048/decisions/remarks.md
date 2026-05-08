# TC048 Decision Remarks

## PR Context
PR #136619 changed `incubating.Allocator.Channel()` from returning `internal.Incubating` to
`internal.Experimental` (reflecting that the incubating package received the former experimental code).
A subsequent commit `aa118a464f2` restored it to `internal.Incubating` for naming consistency.

## Zero-Impact Classification Rationale
Identical reasoning to TC043 (stable.Channel()). `Channel()` is a diagnostic-only method.
In `incubating`, it's even cleaner: incubating is an internal package not imported by plugin code
directly. Even the scheduler plugin that observes Channel() (via TestAllocatorSelection) only
reads it for assertion strings in tests — not in production control flow.

## Trap Amplification vs TC043
The incubating allocator is more recently referenced in test output and documentation because
it previously served as the DEFAULT implementation (selected when no DRA features were enabled).
This makes models more likely to hallucinate incubating-specific cascade. They'll list
`pkg/scheduler/framework/plugins/dynamicresources/dynamicresources.go` and related files.

## Source Verification
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/dynamic-resource-allocation/structured/internal/incubating/allocator_incubating.go:147-149`
Confirmed: `return internal.Incubating` is present (post-fix state).
The question describes the change from "Incubating" to "Experimental" as it appeared in PR #136619 before the fix.

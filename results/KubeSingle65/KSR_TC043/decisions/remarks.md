# TC043 Decision Remarks

## PR Context
PR #136619 promotes the DRA allocator tier structure: experimental → incubating → stable.
As part of this, each allocator's `Channel()` method was temporarily updated to return a string
reflecting its new tier origin. A subsequent commit (`aa118a464f2`) restored the names to match
actual tier labels.

## Question Design Decision
The local clone has `stable.Allocator.Channel()` returning `internal.Stable` (the current, post-fix state).
The question describes the hypothetical change to `internal.Incubating` — which is what PR #136619 actually
applied before the follow-up fix.

## Zero-Impact Classification Rationale
`Channel()` is defined on `internal.Allocator` interface and is used only for diagnostic logging.
Looking at the kubernetes codebase:
- `structured/allocator.go` uses `Channel()` for the `enabledAllocators` list string only.
- `dynamicresources` scheduler plugin may log the channel for debugging.
- No code gates behaviour on the specific string value ("stable" vs "incubating").
- No etcd serialization, admission webhook, or scheduling decision depends on this value.

The trap: models will follow `internal.AllocatorChannel` usages and hallucinate scheduler plugin files.

## Source Verification
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/dynamic-resource-allocation/structured/internal/stable/allocator_stable.go:106-108`
Confirmed: `return internal.Stable` is present.

# TC044 Decision Remarks

## PR Context
PR #136619 changes `incubating.NewAllocator`'s third parameter from `allocatedDevices sets.Set[DeviceID]`
to `allocatedState AllocatedState`. This is part of the capability promotion from experimental → incubating,
where the incubating allocator now needs the full `AllocatedState` struct (which includes shared device IDs
and aggregated capacity, not just allocated device IDs).

## Call Site Analysis
Searched for `incubating.NewAllocator` in the kubernetes repo:
- **Only one non-test call site**: `staging/src/k8s.io/dynamic-resource-allocation/structured/allocator.go:230`
  which previously passed `allocatedState.AllocatedDevices` (a `sets.Set[DeviceID]`).
- The incubating package is `internal`, so no external plugin or controller imports it directly.
- Test files (`allocator_test.go`) use the testing wrapper which accepts `AllocatedState`, not `sets.Set`.

## Orange Tier Justification
The change is a constructor signature change (parameter type widening), matching the Orange tier
(struct/type mutation). The blast radius is very narrow — exactly 1 call site.
Models will overestimate by listing scheduler plugin files, kubelet DRA manager, etc.

## Source Verification
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/dynamic-resource-allocation/structured/internal/incubating/allocator_incubating.go:118-124`
Confirmed: `allocatedState AllocatedState` is present in current NewAllocator signature.
Caller in `structured/allocator.go:230`: `incubating.NewAllocator(ctx, features, allocatedState, ...)`

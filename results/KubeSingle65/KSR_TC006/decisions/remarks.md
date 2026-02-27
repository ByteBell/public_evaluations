# KSR_TC006 Decision Remarks

## PR Relationship
Inspired by PR #137171 — the PR touches the Feature interface's concrete implementations
extensively (mocks.go rewrite), making this interface a natural target for adjacent questions.
Relationship: `inspired_by`.

## Key Go Semantics
When a method is REMOVED from an interface:
- Concrete types that previously implemented it STILL satisfy the (now smaller) interface
- Their methods are simply no longer REQUIRED by the interface — the methods still exist on the structs
- Only code that calls the removed method THROUGH an interface-typed variable fails to compile

## Verified Ground Truth

Files that fail to compile when `InferForScheduling` is removed from `Feature`:

1. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/framework.go`
   - Line 94: `if f.InferForScheduling(podInfo) {` — `f` is of type `Feature` (the interface)
   - Since `Feature` no longer has `InferForScheduling`, this method call through the interface
     is a compile error.

Files that do NOT fail (intentional traps):

- `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/inplacepodresize/guaranteed_cpu_resize.go`
  — `guaranteedQoSPodCPUResizeFeature.InferForScheduling` STILL EXISTS on the concrete type.
  The explicit check `var _ nodedeclaredfeatures.Feature = &guaranteedQoSPodCPUResizeFeature{}`
  now passes MORE easily (smaller interface). No compile error.

- `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/inplacepodresize/pod_level_resource_resize.go`
  — Same reasoning. `podLevelResourcesResizeFeature` still has `InferForScheduling`.

- `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/restartallcontainers/restart_all_containers.go`
  — Same reasoning.

- `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/testing/mocks.go`
  — `MockFeature` still has `InferForScheduling`. Explicit interface check `var _ = nodedeclaredfeatures.Feature((*MockFeature)(nil))` still compiles (smaller interface, more concrete types satisfy it).

- `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/registry.go`
  — No compile error. All Feature values in `AllFeatures` still satisfy the reduced interface.

- Test files calling `.InferForScheduling` on CONCRETE variables:
  - `restart_all_containers_test.go:111`: `feature.InferForScheduling(podInfo)` where `feature` is `*restartAllContainersFeature` — concrete type, not interface → compiles fine
  - `pod_level_resource_resize_test.go:62`: Same
  - `guaranteed_cpu_resize_test.go:82`: Same

## Final Answer
Expected: [`staging/src/k8s.io/component-helpers/nodedeclaredfeatures/framework.go`]

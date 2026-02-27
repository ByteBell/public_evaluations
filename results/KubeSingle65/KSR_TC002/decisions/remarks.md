# KSR_TC002 Decision Remarks

## PR Relationship
Inspired by PR #137171 — the PR itself does NOT add a new method to Feature. However, the PR
directly involves the `Feature` interface and its concrete implementations, making this a
natural adjacent question. Relationship: `inspired_by`.

## Verified Ground Truth (via source file analysis)
Files that fail to compile when `IsVersionGated() bool` is added to `Feature`:

1. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/inplacepodresize/guaranteed_cpu_resize.go`
   - Explicit check: `var _ nodedeclaredfeatures.Feature = &guaranteedQoSPodCPUResizeFeature{}`
   - `guaranteedQoSPodCPUResizeFeature` does not implement `IsVersionGated()` → compile error

2. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/inplacepodresize/pod_level_resource_resize.go`
   - Explicit check: `var _ nodedeclaredfeatures.Feature = &podLevelResourcesResizeFeature{}`
   - `podLevelResourcesResizeFeature` does not implement `IsVersionGated()` → compile error

3. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/restartallcontainers/restart_all_containers.go`
   - Explicit check: `var _ nodedeclaredfeatures.Feature = &restartAllContainersFeature{}`
   - `restartAllContainersFeature` does not implement `IsVersionGated()` → compile error

4. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/testing/mocks.go`
   - Explicit check: `var _ = nodedeclaredfeatures.Feature((*MockFeature)(nil))`
   - `MockFeature` does not implement `IsVersionGated()` → compile error

5. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/registry.go`
   - Builds `[]nodedeclaredfeatures.Feature{restartallcontainers.Feature, inplacepodresize.GuaranteedQoSPodCPUResizeFeature, inplacepodresize.PodLevelResourcesResizeFeature}`
   - All three elements no longer satisfy Feature → compile error at the slice literal

## Intentional Traps
- `framework.go`: Does NOT fail — it only calls methods already in the interface through `f.Feature`. No direct struct creation.
- `framework/plugins/nodedeclaredfeatures/nodedeclaredfeatures.go`: Does NOT fail — it calls Framework methods, not Feature directly.
- `kubelet/kubelet_node_declared_features.go`: Does NOT fail — it only calls DiscoverNodeFeatures, not Feature methods.

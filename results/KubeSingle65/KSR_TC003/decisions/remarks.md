# KSR_TC003 Decision Remarks

## PR Relationship
Inspired by PR #137171 — the PR replaces mockery-generated FeatureGate mocks with
hand-written ones. The FeatureGate interface itself is not changed, but the PR draws
attention to the interface contract and its implementors.

## Verified Ground Truth

### Files failing because they IMPLEMENT the old signature (no longer satisfies new interface):

1. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/testing/mocks.go`
   - `MockFeatureGate.Enabled(gate string) bool` — explicit check:
     `var _ = nodedeclaredfeatures.FeatureGate((*MockFeatureGate)(nil))`
   - The old single-arg method no longer satisfies the new 2-arg interface → compile error

2. `pkg/kubelet/kubelet_node_declared_features.go`
   - `FeatureGateAdapter.Enabled(key string) bool` — assigned to NodeConfiguration.FeatureGates
     (which is of type FeatureGate): `cfg := &nodedeclaredfeatures.NodeConfiguration{FeatureGates: adaptedFG, ...}`
   - `adaptedFG` is of type `FeatureGateAdapter`. After the interface change, `FeatureGateAdapter`
     no longer satisfies `FeatureGate` → compile error at assignment.

### Files failing because they CALL the old signature through the interface:

3. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/inplacepodresize/guaranteed_cpu_resize.go`
   - Line: `featureGateEnabled := cfg.FeatureGates.Enabled(IPPRExclusiveCPUsFeatureGate)`
   - Calls through the FeatureGate interface with 1 arg; new interface requires 2 args → compile error

4. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/inplacepodresize/pod_level_resource_resize.go`
   - Line: `return cfg.FeatureGates.Enabled(IPPRPodLevelResourcesFeatureGate)`
   - Same call-site arity mismatch → compile error

5. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/features/restartallcontainers/restart_all_containers.go`
   - Line: `return cfg.FeatureGates.Enabled(RestartAllContainersOnContainerExits)`
   - Same call-site arity mismatch → compile error

## Intentional Traps
- `framework.go`: Does NOT call FeatureGate.Enabled — it only calls Feature methods.
- `plugin/pkg/admission/nodedeclaredfeatures/admission.go`: Uses `featuregate.FeatureGate.Enabled()`
  (component-base, a DIFFERENT interface) — not `nodedeclaredfeatures.FeatureGate`. Unchanged.
- `features/registry.go`: Does NOT call FeatureGate.Enabled — it just registers Feature values.

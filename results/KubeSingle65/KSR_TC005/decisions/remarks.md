# KSR_TC005 Decision Remarks

## PR Relationship
Inspired by PR #137171 — the PR's cleanup surfaces NodeConfiguration and its Version field
as key parts of the package contract. Relationship: `inspired_by`.

## Verified Ground Truth

Files that fail to compile when `NodeConfiguration.Version` changes from `*version.Version`
to `version.Version`:

1. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/framework.go`
   - Line 73: `if cfg.Version != nil && f.MaxVersion() != nil && cfg.Version.GreaterThan(f.MaxVersion())`
   - The `cfg.Version != nil` comparison is a compile error: you cannot compare a non-pointer
     struct value to `nil` in Go. The `version.Version` type is a struct, not a pointer.

2. `pkg/kubelet/kubelet_node_declared_features.go`
   - Line 47: `Version: kl.version` where `kl.version` is type `*versionutil.Version`
   - Assigning a pointer `*version.Version` to a value field `version.Version` → type mismatch
     compile error.

3. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/framework_test.go`
   - Line 137: `Version: featureMaxVersion.AddMinor(1)` — `AddMinor` returns `*version.Version`
   - Line 146: `Version: version.MustParse("1.39.0-alpha.2.39+049eafd34dfbd2")` — `MustParse`
     returns `*version.Version`
   - Both assignments fail with type mismatch.

## Intentional Traps
- `pkg/scheduler/framework/plugins/nodedeclaredfeatures/nodedeclaredfeatures.go`:
  NOT affected — it calls `InferForPodScheduling(podInfo, pl.version)` where `pl.version`
  is `*versionutil.Version`. That is the `targetVersion` parameter of InferForPodScheduling,
  NOT the NodeConfiguration.Version field. InferForPodScheduling signature is unchanged.
- `plugin/pkg/admission/nodedeclaredfeatures/admission.go`: NOT affected for the same reason.
- `features/restartallcontainers/restart_all_containers_test.go`: NOT affected — creates
  NodeConfiguration WITHOUT setting the Version field (uses zero value).
- `features/inplacepodresize/guaranteed_cpu_resize_test.go`: NOT affected — same reason.
- `features/inplacepodresize/pod_level_resource_resize_test.go`: NOT affected — same reason.

# KSR_TC004 Decision Remarks

## PR Relationship
Inspired by PR #137171 — the PR's cleanup work exposes the FeatureSet type and the MatchResult
contract as central to the package. The question explores a natural API evolution scenario.
Relationship: `inspired_by`.

## Verified Ground Truth

Files that fail to compile if `UnsatisfiedRequirements` changes from `[]string` to `FeatureSet`:

1. `staging/src/k8s.io/component-helpers/nodedeclaredfeatures/framework.go`
   - Line 155: `return &MatchResult{IsMatch: false, UnsatisfiedRequirements: mismatched}, nil`
   - `mismatched` is declared as `var mismatched []string` (line 146) — type mismatch with FeatureSet
   - The struct literal site within the source file itself fails.

2. `plugin/pkg/admission/nodedeclaredfeatures/admission.go`
   - Line 191: `strings.Join(result.UnsatisfiedRequirements, ", ")`
   - `strings.Join` requires `[]string`; FeatureSet does not satisfy this → compile error

3. `pkg/scheduler/framework/plugins/nodedeclaredfeatures/nodedeclaredfeatures.go`
   - Line 127: `strings.Join(result.UnsatisfiedRequirements, ", ")`
   - Same compile error as above

4. `pkg/kubelet/kubelet.go`
   - Line 2842: `missingNodeDeclaredFeatures := strings.Join(matchResult.UnsatisfiedRequirements, ", ")`
   - Same compile error

5. `pkg/kubelet/lifecycle/handlers.go`
   - Line 287: `strings.Join(matchResult.UnsatisfiedRequirements, ", ")`
   - Same compile error

## Evidence chain
Verified by grep: `grep -rn "UnsatisfiedRequirements" ... --include="*.go" | grep -v "_test.go" | grep -v "vendor/"`
All 5 files confirmed in source.

## Intentional Traps
- `framework_test.go`: Will also fail (uses UnsatisfiedRequirements as []string in assertions),
  but the question asks about compile failures in non-test-only contexts. Test files ARE included
  per benchmark rules.
- `features/registry.go`: NOT affected — it does not reference MatchResult.

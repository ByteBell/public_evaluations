# TC046 Decision Remarks

## PR Context
PR #136619 changes the feature-based dispatch of `structured.NewAllocator` by promoting
`stable.SupportedFeatures` to include 4 features and `incubating.SupportedFeatures` to include 6.

## Grey Tier Justification
This is a conditional behaviour question: the answer depends on which DRA feature gate is active.
With `DRAConsumableCapacity` enabled:
1. `Features.Set()` in types.go maps `ConsumableCapacity=true` → includes `"DRAConsumableCapacity"` in the set.
2. Dispatch iterates: stable → `stable.SupportedFeatures.Set()` = {DRAAdminAccess, DRAPrioritizedList, DRAPartitionableDevices, DRADeviceTaints} — NOT a superset of {DRAConsumableCapacity}. Skipped.
3. incubating → `incubating.SupportedFeatures.Set()` includes DRAConsumableCapacity. IS a superset. **Selected.**
4. Answer: incubating. The `Allocate` method lives in `allocator_incubating.go`.

## Difficulty
Models must trace 4 hops:
1. DRAConsumableCapacity gate → Features.ConsumableCapacity=true
2. Features.Set() includes "DRAConsumableCapacity" only if ConsumableCapacity=true
3. IsSuperset check against stable.SupportedFeatures (fails) vs incubating (passes)
4. Identify the file containing incubating.Allocate

## Source Verification
types.go lines 99-101: `if f.ConsumableCapacity { enabled.Insert("DRAConsumableCapacity") }`
stable.SupportedFeatures: no ConsumableCapacity field.
incubating.SupportedFeatures line 83: `ConsumableCapacity: true`.

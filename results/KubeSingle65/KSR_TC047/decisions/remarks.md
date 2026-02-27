# TC047 Decision Remarks

## PR Context
PR #136619 added `var _ internal.AllocatorExtended = &Allocator{}` to stable/allocator_stable.go,
asserting that the promoted code satisfies the optional AllocatorExtended interface (which requires GetStats()).
The stable allocator gained `numAllocateOneInvocations atomic.Int64` and a corresponding GetStats() method
as part of the promotion.

## Red Tier Classification
The question is framed as: "remove GetStats() from stable.Allocator but keep the var _ assertion."
The compile error is self-referential — only `allocator_stable.go` itself fails.
While this is Red (interface-related), the blast radius is 1 file (the file hosting the assertion).
This makes it a useful contrast against full-interface-cascade questions: models that assume
"interface implementation change → all implementors fail" will wrongly list incubating and experimental.

## Answer: Single file
`staging/src/k8s.io/dynamic-resource-allocation/structured/internal/stable/allocator_stable.go`
- The `var _ internal.AllocatorExtended = &Allocator{}` is a compile-time check local to this file.
- No external file stores a `*stable.Allocator` as `AllocatorExtended` or calls `GetStats()` directly.
- structured/allocator.go uses a runtime type assertion `if extended, ok := allocator.(internal.AllocatorExtended)` — this is a runtime check that does NOT produce a compile error if GetStats() is absent.

## Source Verification
Local file line 83: `var _ internal.AllocatorExtended = &Allocator{}`
types.go line 48-52: `type AllocatorExtended interface { GetStats() Stats }`
structured/allocator.go: searched for AllocatorExtended — used as runtime type assertion only.

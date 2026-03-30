# XREPO_TC003 Decision Remarks

## Question Origin
Inspired by the context-propagation patterns in streaming query engines. Adding `Context()`
to `CloseIterator[T]` represents a realistic need to pass cancellation signals through the
iterator chain without a separate parameter on each method.

## Ground Truth — Files that fail to compile

### Propagation chain
```
pkg/iter/v2/interface.go     CloseIterator[T]  ← change here
    ↓ embedded by
pkg/iter/iterator.go         StreamIterator[T]
    ↓ aliased to
pkg/iter/iterator.go         EntryIterator  =  StreamIterator[logproto.Entry]
                             SampleIterator =  StreamIterator[logproto.Sample]
    ↓ implemented by all structs below
```

### pkg/iter/entry_iterator.go
Structs: `streamIterator`, `mergeEntryIterator`, `entrySortIterator`, `queryClientIterator`,
`nonOverlappingIterator`, `reverseIterator`, `reverseEntryIterator`, `peekingEntryIterator`,
`withCloseEntryIterator` — all must add `Context()`.

### pkg/iter/sample_iterator.go
Structs: `peekingSampleIterator`, `mergeSampleIterator`, `sortSampleIterator`,
`sampleQueryClientIterator`, `seriesIterator`, `nonOverlappingSampleIterator` — all must add `Context()`.

### pkg/iter/cache.go
Structs: `cachedIterator` (EntryIterator), `cachedSampleIterator` (SampleIterator).

### pkg/iter/categorized_labels_iterator.go
Struct: `categorizeLabelsIterator`.

### pkg/iter/iterator.go (the source file itself)
Generic helpers `noOpIterator[T]` and `errorIterator[T]` implement the full interface —
they must add `Context()`. The `withCloseEntryIterator` wrapper here must also gain it.

### pkg/chunkenc/memchunk.go
Structs: `entryBufferedIterator` (EntryIterator), `sampleBufferedIterator` (SampleIterator).

### pkg/chunkenc/variants.go
Struct: `multiExtractorSampleBufferedIterator`.

### pkg/chunkenc/dumb_chunk.go
Struct: `dumbChunkIterator`.

### pkg/storage/batch.go
Structs: `logBatchIterator` (EntryIterator), `sampleBatchIterator` (SampleIterator).

### pkg/querier/multi_tenant_querier.go
Structs: `TenantEntryIterator`, `TenantSampleIterator`.

### pkg/logql/evaluator.go
Struct: `bufferedVariantsIterator`.

## Files that are NOT affected

- `pkg/iter/v2/interface.go` itself: defines the interface, not an implementor.
- `pkg/iter/iterator.go` type alias declarations: `type EntryIterator` is not itself an impl.
- Any file that only holds `iter.EntryIterator` as a variable type or function parameter — these are call sites, not implementors, and do not need to add `Context()`.

## Intentional Traps

- **`pkg/iter/entry_iterator.go` — `withCloseEntryIterator`**: this struct wraps another `EntryIterator` and overrides only `Close()`. After the change it must also override `Context()` (or delegate to the inner iterator). Easy to miss because it looks like a minimal wrapper.
- **Generic helpers `noOpIterator[T]` / `errorIterator[T]`**: defined directly in `iterator.go`, the same file that defines the type aliases. Models rarely look for implementations in the file that defines the interface alias.
- **`pkg/logql/evaluator.go`**: deep in the query engine, far from the `iter/` package. `bufferedVariantsIterator` is easily missed by models that only scan `pkg/iter/` and `pkg/chunkenc/`.
- **`TenantEntryIterator` / `TenantSampleIterator`**: exported structs in `querier/` — models often miss them because the multi-tenant layer is conceptually separate from the iterator layer.

## Why This Is Hard

The change is one level removed from where the implementations live. No struct directly
says `var _ v2.CloseIterator = ...` — the constraint flows through two type aliases
(`StreamIterator` → `EntryIterator`/`SampleIterator`). Models must understand Go generic
embedding to trace the blast radius correctly. The breadth across packages means models
must search broadly, not just in `pkg/iter/`.

# XREPO_TC002 Decision Remarks

## Question Origin
Inspired by the evolution of Mimir's `IndexCache` interface (forked from the Thanos `IndexCache`
and extended). Adding `DeleteBlock` represents a realistic block-level cache invalidation need
that would arise during compaction.

## Ground Truth — Files that fail to compile

All 4 are in `grafana/mimir`. Every file listed implements all 12 existing `IndexCache` methods
and therefore must also implement the new `DeleteBlock`.

### Named implementations in the indexcache package:

1. `pkg/storage/tsdb/indexcache/inmemory.go`
   - `*InMemoryIndexCache` — implements all 12 methods explicitly.

2. `pkg/storage/tsdb/indexcache/remote.go`
   - `*RemoteIndexCache` — implements all 12 methods; uses dskit cache under the hood.

3. `pkg/storage/tsdb/indexcache/tracing.go`
   - `*TracingIndexCache` — a decorator wrapper that delegates all 12 methods with tracing.

### Hidden implementation in a consumer package (the key trap):

4. `pkg/storegateway/bucket.go`
   - `noopCache` struct (unexported) defined at line 135.
   - Implements all 12 `IndexCache` methods as single-line no-ops inline in the storegateway package.
   - Used as the default `indexCache` field when no real cache is configured.
   - This is the most likely file to be missed by models that look only in `pkg/storage/tsdb/indexcache/`.

## Files that are NOT affected (call sites, not implementations):

- `pkg/storegateway/bucket_stores.go` — holds `IndexCache` as a field/parameter type but does not implement it.
- `pkg/storegateway/bucket_index_reader.go` — calls `IndexCache` methods but does not implement the interface.
- `pkg/storegateway/series_refs.go` — same: a consumer of the interface.

## Why This Is Hard

The `noopCache` trap is the discriminating factor. It is:
- **Private** (unexported type, `noopCache` not `NoopCache`)
- **Distant** from the interface definition (different package: `storegateway` vs `indexcache`)
- **Disguised** as boilerplate — its methods are one-liners that look like test stubs

Additionally, the interface has 12 methods. Models that attempt to enumerate them may
hallucinate method names from the thanos `IndexCache` (a different but similar interface
in `thanos/pkg/store/cache/cache.go`) and produce wrong signatures for the missing method.

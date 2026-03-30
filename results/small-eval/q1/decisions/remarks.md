# XREPO_TC001 Decision Remarks

## Question Origin
Inspired by real cloud-provider bucket metadata APIs (AWS S3 `GetBucketTagging`, GCS bucket labels).
Adding `Tags` to `objstore.Bucket` represents a realistic need for cost-attribution and
governance tooling that would arise as multi-cloud deployments mature.

## Ground Truth — Files that fail to compile

The change is to `thanos-io/objstore` (a standalone Go module), vendored by mimir and loki.

### grafana/mimir — 5 files

1. `pkg/storage/bucket/prefixed_bucket_client.go`
   - `*PrefixedBucketClient` wraps an `objstore.Bucket` and implements all methods explicitly.

2. `pkg/storage/bucket/delayed_bucket_client.go`
   - `*DelayedBucketClient` wraps an `objstore.Bucket`; injects artificial delay — must add `Tags`.

3. `pkg/storage/bucket/sse_bucket_client.go`
   - `*SSEBucketClient` wraps an `objstore.Bucket`; adds server-side encryption headers — must add `Tags`.

4. `pkg/storage/bucket/client_mock.go`
   - `*MockBucketClient` (or generated mock) implements the full `objstore.Bucket` interface for testing.

5. `pkg/storage/tsdb/block/global_markers_bucket_client.go`
   - `*GlobalMarkersBucketClient` is a decorator that rewrites object paths for global block markers — must add `Tags`.

### grafana/loki — 3 files

1. `pkg/storage/bucket/prefixed_bucket_client.go`
   - Loki's own copy of the prefixed wrapper (not shared with mimir); must add `Tags`.

2. `pkg/storage/bucket/sse_bucket_client.go`
   - Loki's SSE wrapper; must add `Tags`.

3. `pkg/storage/bucket/xcap_bucket.go`
   - `*XCapBucket` carries an explicit compile-time guard `var _ objstore.Bucket = &XCapBucket{}`,
     making it the most directly discoverable broken file in loki.

### thanos-io/thanos — 0 files

Thanos is the repo that owns the module definition but is a **pure consumer** of `objstore.Bucket`.
No struct in `thanos/pkg/` (outside vendor/) implements `objstore.Bucket` from scratch — thanos
passes `objstore.Bucket` values as parameters and wraps them with `objstore.WrapWithMetrics` and
similar helpers that are defined inside the objstore module itself.

## Intentional Traps

- **Thanos = 0**: The most disorienting result. The repo that defines the interface has zero
  concrete implementors — it is purely a consumer. Models anchored to "change lives in thanos →
  thanos breaks" will miss the entire blast radius.
- **No delayed_bucket_client.go in loki**: Loki's bucket wrapper set is a subset of mimir's.
  Models that copy the mimir list and add loki paths without verification will over-report
  `pkg/storage/bucket/delayed_bucket_client.go` for loki (it does not exist there).
- **`objstore.WrapWithMetrics` / `BucketWithMetrics`**: These are wrapper types defined
  *inside* the `thanos-io/objstore` module itself (in vendor). They do not need to be listed
  by the model because the question asks about files in mimir and loki, not in the objstore module.
- **`CachingBucket`** in `thanos/pkg/store/cache/caching_bucket.go`: This wraps an
  `objstore.Bucket` via struct embedding — it promotes all methods from the embedded field
  and does NOT need to add `Tags` explicitly (Go's method promotion handles it). Models may
  incorrectly flag it.

## Why This Is Hard

Genuine multi-repo blast requires reasoning about the vendor graph, not just grep-for-interface.
The asymmetry (mimir=5, loki=3, thanos=0) is the core discriminating factor. The loki file count
trap (missing `delayed_bucket_client.go`) rewards models that actually inspect the loki codebase
rather than mirroring the mimir list.

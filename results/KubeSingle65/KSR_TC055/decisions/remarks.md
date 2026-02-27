# TC055 Decision Remarks

## PR Context
PR #136574 reverts PR #129344. In `conn.go`, the revert removes `IgnoreReceivesWithLogger`
and reverts `IgnoreReceives` to inline the WebSocket drain loop without a contextual logger.
This is one of the core removals in the revert since `IgnoreReceivesWithLogger` was the
contextual-logging entry point for WebSocket receive draining.

## Question Design Decision
The local dataset is in the **pre-revert** state for `conn.go`: both `IgnoreReceives` and
`IgnoreReceivesWithLogger` still exist. The question describes the exact revert change.

## Ground Truth: One impacted file
The only cross-file caller of `IgnoreReceivesWithLogger` is:

```
staging/src/k8s.io/apimachinery/pkg/util/httpstream/wsstream/stream.go:144
    IgnoreReceivesWithLogger(r.logger, ws, r.timeout)
```

This is inside the `handle()` method of `Reader`. After removing `IgnoreReceivesWithLogger`,
this line becomes an undefined reference → compile failure.

## Non-affected Files Analysis
- **`staging/src/k8s.io/apiserver/pkg/util/wsstream/legacy.go`**: re-exports `IgnoreReceives`
  (not `IgnoreReceivesWithLogger`). `IgnoreReceives` still exists with unchanged signature.
  Unaffected.
- **`staging/src/k8s.io/apiserver/pkg/endpoints/handlers/watch.go`**: calls
  `wsstream.IgnoreReceives(ws, 0)` — uses the non-WithLogger variant. Unaffected.
- **`conn.go` itself**: `IgnoreReceives` previously called `IgnoreReceivesWithLogger` (line
  132), but this is updated in the described change. Not counted as an external failure.

## Source Verification
Local files verified:
- `dataset/Kubecluster/kubernetes/staging/src/k8s.io/apimachinery/pkg/util/httpstream/wsstream/conn.go:131-145`
- `dataset/Kubecluster/kubernetes/staging/src/k8s.io/apimachinery/pkg/util/httpstream/wsstream/stream.go:144`

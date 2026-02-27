# TC053 Decision Remarks

## PR Context
PR #136574 reverts PR #129344 "apimachinery: contextual logging in network util code". One
component of that revert removes contextual-logging wrappers in the wsstream package. In
`stream.go`, `NewReaderWithLogger` was added by #129344 as the context-aware constructor;
#136574 removes it and reverts `NewReader` to directly initialise the `Reader` struct.

## Question Design Decision
The local dataset is in the **pre-revert** state for `stream.go`: `NewReaderWithLogger`
still exists and `NewReader` delegates to it. The question describes exactly what
PR #136574 did to this file — removing `NewReaderWithLogger` and inlining the body into
`NewReader`.

## Zero-Impact Classification Rationale
A careful search of the entire kubernetes/kubernetes dataset:

- **`staging/src/k8s.io/apimachinery/pkg/util/httpstream/wsstream/stream.go`** (line 81):
  `NewReader` calls `NewReaderWithLogger` — but this is in the *changed file itself*; it is
  updated as part of the change.
- **`staging/src/k8s.io/apiserver/pkg/util/wsstream/legacy.go`**: re-exports `NewReader`
  (line 59: `var NewReader = apimachinerywsstream.NewReader`) but does NOT re-export
  `NewReaderWithLogger`. Unaffected.
- **`staging/src/k8s.io/apiserver/pkg/endpoints/handlers/responsewriters/writers.go`**
  (line 66): calls `wsstream.NewReader(...)` — signature unchanged, still compiles.

No file outside `stream.go` references `NewReaderWithLogger`. The blast radius is zero.

## The Trap
Models may notice that `stream.go` also uses `IgnoreReceivesWithLogger(r.logger, ws, r.timeout)`
(line 144) and `runtime.HandleCrashWithLogger(r.logger)` (line 141). These use `r.logger`
which disappears when `NewReaderWithLogger` is removed. However:
1. `IgnoreReceivesWithLogger` is defined in `conn.go`, not `stream.go`; it is NOT being
   removed by this change.
2. The change to `stream.go` also removes `r.logger` usage from the `handle()` method —
   this is part of the described change.
3. No external file calls `stream.go`'s internal `handle()` method.

## Source Verification
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/apimachinery/pkg/util/httpstream/wsstream/stream.go`
Confirmed: `NewReaderWithLogger` exists at line 90; only internal reference at line 81 from `NewReader`.

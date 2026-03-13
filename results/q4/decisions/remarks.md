# XREPO_TC004 Decision Remarks

## Question Origin
Inspired by the evolution of structured CLI logging in the Flux project. The `log.Logger`
interface was introduced to decouple the CLI's logging output from concrete implementations
so that callers (bootstrap, uninstall, status) could accept any logger. Adding `Debugf`
represents a natural extension for verbose troubleshooting output.

## Ground Truth — Files that fail to compile

Exactly 2 files in `fluxcd/flux2`:

### 1. `pkg/log/nop.go`
- `NopLogger` (exported struct, value receiver) — implements all 6 existing methods as
  empty no-ops (`{}`). Used in tests and whenever logging output should be suppressed.
- Must add `func (NopLogger) Debugf(format string, a ...interface{}) {}`.

### 2. `cmd/flux/log.go`
- `stderrLogger` (unexported struct, value receiver, `package main`) — implements all 6
  existing methods with emoji-prefixed `fmt.Fprintln` calls to its `stderr io.Writer` field.
  This is the production logger; the package-level `var logger = stderrLogger{stderr: os.Stderr}`
  in `cmd/flux/main.go` is passed as `log.Logger` throughout the CLI.
- Must add `func (l stderrLogger) Debugf(format string, a ...interface{}) { ... }`.

## Files that are NOT affected (consumers, not implementors)

- `pkg/bootstrap/bootstrap_plain_git.go` — holds `logger log.Logger` as a struct field; calls methods on it but does not implement the interface.
- `pkg/bootstrap/options.go` — `WithLogger(logger log.Logger) Option` accepts a Logger parameter; not an implementor.
- `pkg/status/status.go` — `StatusChecker` struct has a `logger log.Logger` field; consumer only.
- `pkg/uninstall/uninstall.go` — three exported functions accept `logger log.Logger`; they call `logger.Actionf(...)` etc. but do not implement Logger.
- `cmd/flux/main.go` — declares `var logger = stderrLogger{...}` (the concrete value) but is not itself an implementor file.

## Intentional Traps

- **`stderrLogger` is unexported and in `package main`**: Models scanning `pkg/log/` only will find `NopLogger` and stop. The real production logger lives two directory levels away in `cmd/flux/log.go` under a completely different package. It has no `var _ log.Logger = stderrLogger{}` guard to hint at its interface satisfaction.
- **Consumer vs implementor confusion**: `pkg/bootstrap/`, `pkg/status/`, and `pkg/uninstall/` all prominently reference `log.Logger`. Models anchored to grep-for-type may list these as broken files — they are not, because they hold the interface as a value, not implement it.
- **Method count**: The interface has 6 methods. Models may hallucinate one of the existing method names (e.g., confusing `Warningf`/`Warnf`) when listing what `stderrLogger` implements and incorrectly conclude it was not already a full implementor.

## Why This Is Hard

The two implementors sit at opposite poles of the repo layout: one is in the defining package
(`pkg/log/`), one is in `package main` (`cmd/flux/`). The key discriminating skill is
recognizing that `stderrLogger` in `cmd/flux/log.go` is a full `log.Logger` implementor despite
being unexported, private to `main`, and carrying no compile-time interface guard.

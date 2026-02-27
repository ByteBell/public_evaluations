# TC056 Decision Remarks

## PR Context
PR #136574 reverts "apimachinery: contextual logging in network util code". As part of the
revert, several restmapper helpers were reverted from using context-aware Discovery clients
back to the non-context variants. The broader pattern includes removing
`NewDiscoveryCategoryExpanderWithContext` and similar helpers. This question is directly
inspired by that cleanup pattern in `category_expansion.go`.

## Question Design Decision
This question targets the removal of `NewDiscoveryCategoryExpander` (the current
non-context version). The question uses the current post-revert state of the file (no
`WithContext` variants exist). Removing the base function is a clean Red question with
exactly one cross-file caller.

## Ground Truth: One impacted file
Exhaustive search for `NewDiscoveryCategoryExpander` callers:

```
staging/src/k8s.io/cli-runtime/pkg/resource/builder.go:219
    return restmapper.NewDiscoveryCategoryExpander(discoveryClient), err
```

This is the only non-test, non-definition reference in the dataset.

## Non-affected Files Analysis
- **`staging/src/k8s.io/cli-runtime/pkg/resource/fake.go`**: Uses `SimpleCategoryExpander`
  directly, not `NewDiscoveryCategoryExpander`. Unaffected.
- **`staging/src/k8s.io/client-go/restmapper/category_expansion_test.go`**: Test file;
  even if broken, tests are not production code. (Question scope is compile failures, which
  would include test files if they use the symbol — checking: they do use it, so they would
  also fail. But the main answer is builder.go.)
- **`staging/src/k8s.io/client-go/restmapper/shortcut.go`**: Uses `CategoryExpander` type
  but not the constructor. Unaffected.

## Test File Consideration
`category_expansion_test.go` likely uses `NewDiscoveryCategoryExpander` in tests. These
would also fail to compile. However, the primary production-code impact is `builder.go`.

## Source Verification
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/client-go/restmapper/category_expansion.go:51-56`
Confirmed: `NewDiscoveryCategoryExpander` exists and returns `CategoryExpander`.
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/cli-runtime/pkg/resource/builder.go:219`
Confirmed: sole production caller.

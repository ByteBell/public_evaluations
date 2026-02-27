# TC057 Decision Remarks

## PR Context
PR #136574 reverts contextual logging additions. In `shortcut.go`, the original PR #129344 had
changed `NewShortcutExpander` to delegate to a new `NewShortcutExpanderWithContext`, and
`shortcutExpander` to use `meta.RESTMapperWithContext` and
`discovery.DiscoveryInterfaceWithContext`. PR #136574 reverts this, restoring
`NewShortcutExpander` to directly construct `shortcutExpander` using the plain interface types.

## Question Design Decision
The local dataset is in the post-revert state for `shortcut.go` (uses plain `meta.RESTMapper`,
not `meta.RESTMapperWithContext`). The question describes removing `NewShortcutExpander` itself
— a further hypothetical change inspired by the PR's pattern of removing `WithContext` helpers.

## Ground Truth: Three impacted files
1. `staging/src/k8s.io/cli-runtime/pkg/genericclioptions/config_flags.go` (line 358):
   ```go
   expander := restmapper.NewShortcutExpander(mapper, discoveryClient, func(a string) {
   ```
2. `staging/src/k8s.io/cli-runtime/pkg/genericclioptions/config_flags_fake.go` (line 69):
   ```go
   expander := restmapper.NewShortcutExpander(mapper, f.discoveryClient, nil)
   ```
3. `staging/src/k8s.io/kubectl/pkg/cmd/testing/fake.go` (line 644):
   ```go
   expander := restmapper.NewShortcutExpander(mapper, fakeDs, nil)
   ```

## Why no other files
`shortcutExpander` is unexported. There is no way to construct a `shortcutExpander` without
calling `NewShortcutExpander`. The return type is `meta.RESTMapper` (interface), so no external
file needs to import the concrete type.

## Source Verification
Grep `NewShortcutExpander` across dataset confirms exactly 3 non-test callers.
Local file: `dataset/Kubecluster/kubernetes/staging/src/k8s.io/client-go/restmapper/shortcut.go:43-45`

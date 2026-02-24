# Analysis: NK_TC015 -- Rename chart.Metadata.Version and chart.Metadata.AppVersion

## Question

> Change the chart.Metadata struct in helm.sh/helm/v4/pkg/chart/v2 to rename the Version field to ChartVersion and the AppVersion field to ApplicationVersion. chart.Metadata is returned by chartutil.LoadChartfile() and is the primary type for Chart.yaml representation. Any code accessing chart.Version or chart.AppVersion will break.

## Methodology

Searched the entire dataset for:
- Direct field access: `md.Version`, `md.AppVersion`, `cf.Version`, `ch.Metadata.Version`, `ch.Metadata.AppVersion`
- Method wrappers: `ch.AppVersion()` which delegates to `ch.Metadata.AppVersion`
- Embedded struct access: `ChartVersion` in `pkg/repo/v1/index.go` embeds `*chart.Metadata`, so `cv.Version` is actually `chart.Metadata.Version`
- Struct literal field names: `Version: "1.0"` or `AppVersion: "1.0.0"` in Metadata struct literals
- Template strings: `.Chart.Version` and `.Chart.AppVersion` in Go template strings rendered via `MetadataAsMap()` (which uses reflection on struct field names)
- Cross-repo: Searched argo-cd and flux2 -- no helm chart.Metadata references found

Key distinctions made:
- `release.Version` (int, release revision number) -- NOT affected
- `dep.Version` (on `chart.Dependency` struct) -- NOT affected
- `action.Metadata.Version` (separate struct in `pkg/action/get_metadata.go`) -- NOT affected
- `hubChartElement.Version` (local struct in `search_hub.go`) -- NOT affected
- `monocular.ChartVersion.Version` (separate struct) -- NOT affected
- `KubeVersion.Version`, `gvk.Version`, plugin `.Version` -- NOT affected

## Files Actually Required (Ground Truth)

### A. Definition Files (struct definition + internal usage of fields)

| # | File (relative to helm/) | Reason |
|---|---|---|
| 1 | `pkg/chart/v2/metadata.go` | Defines `Version` and `AppVersion` fields on Metadata; uses `md.Version`, `md.AppVersion` in Validate() |
| 2 | `internal/chart/v3/metadata.go` | Mirror definition for v3 Metadata; uses `md.Version`, `md.AppVersion` in Validate() |

### B. Chart wrapper methods accessing Metadata fields

| # | File | Reason |
|---|---|---|
| 3 | `pkg/chart/v2/chart.go` | `ch.Metadata.AppVersion` in AppVersion() method |
| 4 | `internal/chart/v3/chart.go` | `ch.Metadata.AppVersion` in AppVersion() method |

### C. Lint rules accessing Metadata fields

| # | File | Reason |
|---|---|---|
| 5 | `pkg/chart/v2/lint/rules/chartfile.go` | `cf.Version` in validateChartVersion(), validateChartVersionStrictSemVerV2() |
| 6 | `pkg/chart/v2/lint/rules/chartfile_test.go` | `badChart.Version = test.Version` |
| 7 | `internal/chart/v3/lint/rules/chartfile.go` | `cf.Version` in validateChartVersion() |
| 8 | `internal/chart/v3/lint/rules/chartfile_test.go` | `badChart.Version = test.Version` |

### D. Chartutil / save / dependencies

| # | File | Reason |
|---|---|---|
| 9 | `pkg/chart/v2/util/save.go` | `c.Metadata.Version` in Save() for filename |
| 10 | `pkg/chart/v2/util/dependencies.go` | `c.Metadata.Version` in getAliasDependency(), processDependencyEnabled() |
| 11 | `pkg/chart/v2/util/dependencies_test.go` | `aliasChart.Metadata.Version` |
| 12 | `pkg/chart/v2/util/chartfile_test.go` | `f.Version != "1.2.3"` on *chart.Metadata |
| 13 | `pkg/chart/v2/util/create.go` | `.Chart.AppVersion` and `.Chart.Version` in template strings (breaks via MetadataAsMap reflection) |
| 14 | `internal/chart/v3/util/save.go` | `c.Metadata.Version` in Save() |
| 15 | `internal/chart/v3/util/dependencies.go` | `c.Metadata.Version` in getAliasDependency(), processDependencyEnabled() |
| 16 | `internal/chart/v3/util/dependencies_test.go` | `aliasChart.Metadata.Version` |
| 17 | `internal/chart/v3/util/chartfile_test.go` | `f.Version != "1.2.3"` on *chart.Metadata |
| 18 | `internal/chart/v3/util/create.go` | `.Chart.AppVersion` and `.Chart.Version` in template strings |

### E. Test files using Metadata struct literals with Version/AppVersion

| # | File | Reason |
|---|---|---|
| 19 | `pkg/chart/v2/metadata_test.go` | `Version:` field in many Metadata struct literals |
| 20 | `pkg/chart/v2/chart_test.go` | `AppVersion: "1.0.0"`, `Version: "1.0.0"` in Metadata literal; `chrt.AppVersion()` call |
| 21 | `internal/chart/v3/metadata_test.go` | `Version:` field in Metadata struct literals |
| 22 | `internal/chart/v3/chart_test.go` | `chrt.AppVersion()` call |
| 23 | `pkg/chart/v2/loader/load_test.go` | `dep.Metadata.Version`; `Version: "0.1.0"` in Metadata struct literals |
| 24 | `internal/chart/v3/loader/load_test.go` | `dep.Metadata.Version` |
| 25 | `pkg/chart/loader/load_test.go` | `Version: "0.1.0"` in both c2.Metadata and c3.Metadata struct literals |

### F. Action package

| # | File | Reason |
|---|---|---|
| 26 | `pkg/action/get_metadata.go` | `chrt.Metadata.Version`, `chrt.Metadata.AppVersion` |
| 27 | `pkg/action/package.go` | `ch.Metadata.Version`, `ch.Metadata.AppVersion` |
| 28 | `pkg/action/dependency.go` | `depChart.Metadata.Version`, `c.Metadata.Version` |
| 29 | `pkg/action/history_test.go` | `updatedRelease.Chart.Metadata.Version = "0.1.1"` |

### G. Cmd package

| # | File | Reason |
|---|---|---|
| 30 | `pkg/cmd/history.go` | `c.Metadata.Version`; `c.AppVersion()`; `version.Chart.Metadata.AppVersion`; `version.Chart.Metadata.Version` |
| 31 | `pkg/cmd/status.go` | `rel.Chart.Metadata.Version`, `rel.Chart.Metadata.AppVersion` |
| 32 | `pkg/cmd/list.go` | `rel.Chart.Metadata.Version` |
| 33 | `pkg/cmd/package_test.go` | `ch.Metadata.AppVersion` |
| 34 | `pkg/cmd/upgrade_test.go` | `cfile.Metadata.Version` |
| 35 | `pkg/cmd/get_all_test.go` | `{{.Release.Chart.Metadata.Version}}` in template string |
| 36 | `pkg/cmd/flags.go` | `details.AppVersion`, `details.Version` (ChartVersion embeds *chart.Metadata) |

### H. Repo / Registry / Downloader / Resolver / Search / Pusher

| # | File | Reason |
|---|---|---|
| 37 | `pkg/repo/v1/index.go` | `c[a].Version`, `c[b].Version`, `md.Version`, `ver.Version`, `cv.Version` (all via ChartVersion embedding *Metadata) |
| 38 | `pkg/repo/v1/index_test.go` | `.Version` on ChartVersion objects |
| 39 | `pkg/repo/v1/repotest/server.go` | `c.Metadata.Version` |
| 40 | `pkg/registry/chart.go` | `meta.Version` on *chart.Metadata |
| 41 | `pkg/registry/client.go` | `meta.Version` on *chart.Metadata |
| 42 | `pkg/registry/registry_test.go` | `meta.Version` on *chart.Metadata |
| 43 | `pkg/downloader/manager.go` | `ch.Metadata.Version` (multiple locations) |
| 44 | `pkg/downloader/manager_test.go` | `signtest.Metadata.Version`, `local.Metadata.Version` |
| 45 | `internal/resolver/resolver.go` | `ch.Metadata.Version` |
| 46 | `pkg/cmd/search/search.go` | `rr.Version` on ChartVersion (embeds Metadata) |
| 47 | `pkg/cmd/search/search_test.go` | `in[5].Chart.Version` on ChartVersion |
| 48 | `pkg/cmd/search_repo.go` | `r.Chart.Version`, `r.Chart.AppVersion` on ChartVersion |
| 49 | `pkg/pusher/ocipusher.go` | `meta.Metadata.Version` |

### I. Common/Accessor (indirect via reflection)

| # | File | Reason |
|---|---|---|
| 50 | `pkg/chart/common.go` | `structToMap(r.chrt.Metadata)` uses reflection field names; renaming changes map keys, breaking template rendering |

**Total files actually required: 50**

---

## Files NOT Affected (commonly confused)

| File | Why NOT affected |
|---|---|
| `pkg/chart/v2/util/chartfile.go` | Unmarshals/marshals Metadata via YAML; does not access `.Version` or `.AppVersion` directly |
| `internal/chart/v3/util/chartfile.go` | Same as above |
| `pkg/chart/v2/fuzz_test.go` | Uses GenerateStruct on Metadata; does not access fields by name |
| `internal/chart/v3/fuzz_test.go` | Same as above |
| `pkg/action/get_metadata_test.go` | Accesses `result.Version` and `result.AppVersion` on `action.Metadata`, not `chart.Metadata` |
| `pkg/cmd/get_metadata.go` | Accesses `w.metadata.Version` on `action.Metadata`, not `chart.Metadata` |
| `pkg/cmd/history_test.go` | Accesses `info.AppVersion` on local `releaseInfo` struct |
| `pkg/action/install.go` | Does not access Metadata.Version/AppVersion |
| `pkg/action/upgrade.go` | Does not access Metadata.Version/AppVersion |
| `pkg/action/lint.go` | Does not access Metadata.Version/AppVersion |
| `pkg/action/show.go` | Does not access Metadata.Version/AppVersion |
| `pkg/cmd/search_hub.go` | `.Version`/`.AppVersion` on `hubChartElement` and `monocular.ChartVersion` (separate types) |
| `internal/monocular/search.go` | Has its own `ChartVersion` struct with `Version`/`AppVersion` -- not chart.Metadata |
| `pkg/action/action.go` | `.Version` is on `KubeVersion` or release version, not chart.Metadata |
| `internal/chart/v3/dependency.go` | `d.Version` is on Dependency struct, not Metadata |
| `pkg/chart/v2/dependency.go` | `d.Version` is on Dependency struct, not Metadata |
| `pkg/chart/v2/util/compatible.go` | Generic semver comparison; no Metadata access |
| `pkg/cmd/package.go` | `client.Version` and `client.AppVersion` are on `action.Package` struct |
| `pkg/cmd/show.go` | `client.Version` is on `action.Show` struct |
| `pkg/cmd/install.go` | `client.Version` is on `action.Install` struct |
| `pkg/cmd/upgrade.go` | `client.Version` is on `action.Upgrade` struct |
| `pkg/cmd/create.go` | Does not access Metadata.Version/AppVersion |
| `pkg/cmd/create_test.go` | Does not access Metadata.Version/AppVersion |
| `pkg/action/install_test.go` | `.Version` is on `release.Release` (int), not Metadata |
| `pkg/action/lint_test.go` | Does not access Metadata.Version/AppVersion |
| `pkg/engine/engine.go` | Does not access chart.Metadata.Version/AppVersion |
| `pkg/action/action_test.go` | Does not access chart.Metadata.Version/AppVersion |

---

## Model Accuracy Evaluation

### Scoring methodology

For each model:
- **True Positives (TP)**: Files the model found that ARE in the ground truth
- **False Positives (FP)**: Files the model listed that are NOT in the ground truth (including hallucinated files)
- **False Negatives (FN)**: Files in the ground truth that the model missed
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1**: 2 * Precision * Recall / (Precision + Recall)

### Model Results

#### 1. anthropic/claude-haiku-4.5 (17 files)

| File | Verdict | Notes |
|---|---|---|
| `pkg/action/package.go` | TP | Accesses `ch.Metadata.Version`, `ch.Metadata.AppVersion` |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP | Accesses `cf.Version` |
| `pkg/chart/v2/util/chartfile.go` | FP | Does not access Version/AppVersion directly |
| `pkg/chart/common.go` | TP | Reflection-based structToMap changes key names |
| `pkg/cmd/package.go` | FP | `client.Version` is on action.Package struct |
| `pkg/registry/chart_test.go` | FP | No Metadata.Version/AppVersion access |
| `internal/chart/v3/util/chartfile.go` | FP | Does not access Version/AppVersion directly |
| `pkg/action/get_metadata.go` | TP | Accesses `chrt.Metadata.Version`, `chrt.Metadata.AppVersion` |
| `pkg/chart/v2/metadata_test.go` | TP | Version in struct literals |
| `pkg/cmd/get_metadata.go` | FP | `w.metadata.Version` is on action.Metadata |
| `pkg/action/package_test.go` | FP | No Metadata.Version/AppVersion access |
| `pkg/cmd/show.go` | FP | `client.Version` is on action.Show struct |
| `internal/chart/v3/lint/rules/chartfile.go` | TP | `cf.Version` access |
| `internal/chart/v3/metadata_test.go` | TP | Version in struct literals |
| `pkg/registry/chart.go` | TP | `meta.Version` on Metadata |
| `pkg/action/get_metadata_test.go` | FP | `result.Version` on action.Metadata |
| `pkg/chart/v2/metadata.go` | TP | Definition file |

**TP: 9, FP: 8, FN: 41** | Precision: 52.9% | Recall: 18.0% | F1: 26.9%

---

#### 2. arcee-ai/trinity-large-preview (12 files)

| File | Verdict |
|---|---|
| `pkg/action/lint_test.go` | FP |
| `pkg/cmd/create.go` | FP |
| `pkg/action/install_test.go` | FP |
| `pkg/chart/v2/util/chartfile_test.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/action/lint.go` | FP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/cmd/create_test.go` | FP |
| `pkg/action/install.go` | FP |
| `pkg/action/get_metadata.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile_test.go` | TP |
| `pkg/action/get_metadata_test.go` | FP |

**TP: 4, FP: 8, FN: 46** | Precision: 33.3% | Recall: 8.0% | F1: 12.9%

---

#### 3. deepseek/deepseek-chat-v3.1 (7 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/chart.go` | TP |
| `pkg/action/show.go` | FP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/action/get_metadata.go` | TP |
| `pkg/action/package.go` | TP |
| `pkg/chart/v2/metadata.go` | TP |

**TP: 5, FP: 2, FN: 45** | Precision: 71.4% | Recall: 10.0% | F1: 17.5%

---

#### 4. deepseek/deepseek-v3.2 (26 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/metadata.go` | TP |
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `internal/chart/v3/metadata.go` | TP |
| `internal/chart/v3/chart.go` | TP |
| `internal/chart/v3/util/chartfile.go` | FP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `internal/chart/v3/lint/rules/chartfile.go` | TP |
| `pkg/action/get_metadata.go` | TP |
| `pkg/action/get_metadata_test.go` | FP |
| `pkg/cmd/history.go` | TP |
| `pkg/cmd/package_test.go` | TP |
| `pkg/chart/common.go` | TP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `internal/chart/v3/metadata_test.go` | TP |
| `pkg/chart/v2/util/chartfile_test.go` | TP |
| `internal/chart/v3/util/chartfile_test.go` | TP |
| `pkg/chart/v2/fuzz_test.go` | FP |
| `internal/chart/v3/fuzz_test.go` | FP |
| `pkg/registry/client.go` | TP |
| `pkg/repo/v1/index.go` | TP |
| `internal/monocular/search.go` | FP |
| `pkg/action/show.go` | FP |
| `pkg/action/package.go` | TP |
| `pkg/downloader/manager.go` | TP |
| `pkg/chart/v2/util/create.go` | TP |

**TP: 18, FP: 8, FN: 32** | Precision: 69.2% | Recall: 36.0% | F1: 47.4%

---

#### 5. google/gemini-3-flash-preview (7 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/metadata.go` | TP |
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/chart/v2/chart_test.go` | TP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `pkg/action/get_metadata.go` | TP |

**TP: 6, FP: 1, FN: 44** | Precision: 85.7% | Recall: 12.0% | F1: 21.1%

---

#### 6. minimax/minimax-m2.5 (9 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/action/get_metadata.go` | TP |
| `pkg/chart/common.go` | TP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile_test.go` | TP |
| `internal/chart/v3/metadata.go` | TP |
| `pkg/chart/v2/metadata.go` | TP |

**TP: 8, FP: 1, FN: 42** | Precision: 88.9% | Recall: 16.0% | F1: 27.1%

---

#### 7. openai/gpt-5.1-codex-max (13 files, 1 hallucinated)

| File | Verdict |
|---|---|
| `pkg/chart/v2/chart.go` | TP |
| `pkg/cmd/package_test.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/chart/v2/chart_test.go` | TP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `pkg/chart/v2/loader/load_test.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile_test.go` | TP |
| `pkg/cmd/history.go` | TP |
| `pkg/chart/v2/loader/load.go` | FP |
| `pkg/action/get_metadata_test.go` | FP |
| `pkg/chart/v2/metadata.go` | TP |
| `lint/lint_test.go` (hallucinated) | FP |

**TP: 9, FP: 4, FN: 41** | Precision: 69.2% | Recall: 18.0% | F1: 28.6%

---

#### 8. openai/gpt-oss-120b (8 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/chart/v2/chart_test.go` | TP |
| `pkg/chart/v2/util/compatible.go` | FP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile_test.go` | TP |
| `pkg/chart/v2/metadata.go` | TP |

**TP: 6, FP: 2, FN: 44** | Precision: 75.0% | Recall: 12.0% | F1: 20.7%

---

#### 9. stepfun/step-3.5-flash (25 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/metadata.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/action/get_metadata.go` | TP |
| `pkg/action/package.go` | TP |
| `pkg/action/show.go` | FP |
| `pkg/registry/client.go` | TP |
| `pkg/repo/v1/index.go` | TP |
| `pkg/action/install.go` | FP |
| `pkg/action/upgrade.go` | FP |
| `pkg/action/lint.go` | FP |
| `pkg/downloader/manager.go` | TP |
| `pkg/chart/loader/load.go` | FP |
| `pkg/chart/v2/loader/load.go` | FP |
| `pkg/chart/v2/util/dependencies.go` | TP |
| `pkg/chart/v2/util/save.go` | TP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `pkg/chart/v2/util/chartfile_test.go` | TP |
| `pkg/action/get_metadata_test.go` | FP |
| `pkg/action/package_test.go` | FP |
| `pkg/action/lint_test.go` | FP |
| `pkg/chart/v2/lint/lint_test.go` | FP |
| `pkg/chart/v2/loader/load_test.go` | TP |
| `pkg/chart/v2/util/dependencies_test.go` | TP |

**TP: 14, FP: 11, FN: 36** | Precision: 56.0% | Recall: 28.0% | F1: 37.3%

---

#### 10. x-ai/grok-code-fast-1 (0 files)

Error/empty answer -- no evaluation possible.

**TP: 0, FP: 0, FN: 50** | Precision: N/A | Recall: 0% | F1: 0%

---

#### 11. xiaomi/mimo-v2-flash (60 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/util/save_test.go` | FP |
| `internal/chart/v3/lint/rules/values.go` | FP |
| `internal/chart/v3/lint/rules/template_test.go` | FP |
| `pkg/action/upgrade.go` | FP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `internal/chart/v3/util/save_test.go` | FP |
| `pkg/action/install.go` | FP |
| `pkg/action/upgrade_test.go` | FP |
| `pkg/cmd/history_test.go` | FP |
| `internal/chart/v3/fuzz_test.go` | FP |
| `pkg/repo/v1/index.go` | TP |
| `pkg/chart/v2/metadata.go` | TP |
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/util/chartfile_test.go` | TP |
| `internal/chart/v3/metadata.go` | TP |
| `internal/chart/v3/util/dependencies.go` | TP |
| `pkg/cmd/search/search.go` | TP |
| `pkg/cmd/install.go` | FP |
| `pkg/chart/v2/lint/rules/dependencies.go` | FP |
| `pkg/cmd/create_test.go` | FP |
| `internal/chart/v3/lint/lint_test.go` | FP |
| `pkg/registry/chart_test.go` | FP |
| `internal/chart/v3/lint/lint.go` | FP |
| `internal/chart/v3/util/chartfile.go` | FP |
| `pkg/engine/engine.go` | FP |
| `pkg/action/get_metadata.go` | TP |
| `internal/chart/v3/lint/rules/template.go` | FP |
| `pkg/action/package_test.go` | FP |
| `internal/chart/v3/loader/archive.go` | FP |
| `internal/chart/v3/metadata_test.go` | TP |
| `internal/chart/v3/loader/load_test.go` | TP |
| `internal/chart/v3/lint/rules/chartfile_test.go` | TP |
| `internal/chart/v3/loader/load.go` | FP |
| `internal/chart/v3/lint/rules/dependencies_test.go` | FP |
| `internal/chart/v3/lint/rules/values_test.go` | FP |
| `internal/chart/v3/dependency.go` | FP |
| `internal/chart/v3/chart_test.go` | TP |
| `pkg/chart/v2/chart_test.go` | TP |
| `pkg/cmd/upgrade.go` | FP |
| `pkg/cmd/template.go` | FP |
| `pkg/downloader/manager_test.go` | TP |
| `internal/chart/v3/lint/rules/chartfile.go` | TP |
| `pkg/action/package.go` | TP |
| `pkg/cmd/list.go` | TP |
| `internal/chart/v3/lint/rules/crds_test.go` | FP |
| `pkg/action/push.go` | FP |
| `pkg/downloader/manager.go` | TP |
| `internal/chart/v3/util/save.go` | TP |
| `pkg/action/install_test.go` | FP |
| `internal/chart/v3/dependency_test.go` | FP |
| `internal/chart/v3/util/chartfile_test.go` | TP |
| `pkg/action/action_test.go` | FP |
| `internal/chart/v3/lint/rules/deprecations.go` | FP |
| `internal/chart/v3/lint/rules/crds.go` | FP |
| `internal/chart/v3/lint/rules/deprecations_test.go` | FP |
| `internal/chart/v3/chart.go` | TP |
| `internal/chart/v3/lint/rules/dependencies.go` | FP |
| `pkg/registry/chart.go` | TP |
| `pkg/cmd/history.go` | TP |

**TP: 24, FP: 36, FN: 26** | Precision: 40.0% | Recall: 48.0% | F1: 43.6%

---

#### 12. z-ai/glm-4.7-flash (27 files)

| File | Verdict |
|---|---|
| `pkg/chart/v2/metadata.go` | TP |
| `pkg/chart/v2/chart.go` | TP |
| `pkg/chart/v2/util/chartfile.go` | FP |
| `pkg/chart/v2/lint/rules/chartfile.go` | TP |
| `pkg/chart/v2/metadata_test.go` | TP |
| `pkg/chart/v2/chart_test.go` | TP |
| `pkg/chart/v2/util/chartfile_test.go` | TP |
| `pkg/chart/v2/lint/rules/chartfile_test.go` | TP |
| `pkg/action/action.go` | FP |
| `pkg/action/dependency.go` | TP |
| `pkg/action/get_metadata.go` | TP |
| `pkg/action/install.go` | FP |
| `pkg/action/lint.go` | FP |
| `pkg/action/package.go` | TP |
| `pkg/action/pull.go` | FP |
| `pkg/action/upgrade.go` | FP |
| `pkg/action/uninstall.go` | FP |
| `pkg/action/release_testing.go` | FP |
| `pkg/cmd/install.go` | FP |
| `pkg/cmd/upgrade.go` | FP |
| `pkg/cmd/lint.go` | FP |
| `pkg/cmd/package.go` | FP |
| `pkg/cmd/pull.go` | FP |
| `pkg/cmd/search/search.go` | TP |
| `pkg/cmd/get_metadata.go` | FP |
| `pkg/cmd/create.go` | FP |
| `pkg/cmd/show_test.go` | FP |

**TP: 11, FP: 16, FN: 39** | Precision: 40.7% | Recall: 22.0% | F1: 28.6%

---

## Summary Table

| Model | Files Listed | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v3.2 | 26 | 18 | 8 | 32 | 69.2% | 36.0% | **47.4%** |
| xiaomi/mimo-v2-flash | 60 | 24 | 36 | 26 | 40.0% | **48.0%** | 43.6% |
| stepfun/step-3.5-flash | 25 | 14 | 11 | 36 | 56.0% | 28.0% | 37.3% |
| openai/gpt-5.1-codex-max | 13 | 9 | 4 | 41 | 69.2% | 18.0% | 28.6% |
| z-ai/glm-4.7-flash | 27 | 11 | 16 | 39 | 40.7% | 22.0% | 28.6% |
| minimax/minimax-m2.5 | 9 | 8 | 1 | 42 | **88.9%** | 16.0% | 27.1% |
| anthropic/claude-haiku-4.5 | 17 | 9 | 8 | 41 | 52.9% | 18.0% | 26.9% |
| google/gemini-3-flash-preview | 7 | 6 | 1 | 44 | 85.7% | 12.0% | 21.1% |
| openai/gpt-oss-120b | 8 | 6 | 2 | 44 | 75.0% | 12.0% | 20.7% |
| deepseek/deepseek-chat-v3.1 | 7 | 5 | 2 | 45 | 71.4% | 10.0% | 17.5% |
| arcee-ai/trinity-large-preview | 12 | 4 | 8 | 46 | 33.3% | 8.0% | 12.9% |
| x-ai/grok-code-fast-1 | 0 | 0 | 0 | 50 | N/A | 0% | 0% |

## Key Observations

1. **Best overall F1: deepseek/deepseek-v3.2 (47.4%)** -- Best balance of precision and recall with 18 true positives out of 26 listed files.

2. **Best recall: xiaomi/mimo-v2-flash (48.0%)** -- Found the most true positives (24) but at the cost of 36 false positives (60 files total). The shotgun approach found more actual files but with very low precision.

3. **Best precision: minimax/minimax-m2.5 (88.9%)** -- Only 1 false positive out of 9 files, but missed 42 of the 50 required files.

4. **Common gap across all models**: No model identified more than 48% of the affected files. The major categories missed by most models:
   - **Repo/index files**: `pkg/repo/v1/index.go`, `index_test.go`, `repotest/server.go` -- ChartVersion embeds *chart.Metadata, making `.Version` actually `Metadata.Version`
   - **Internal/chart/v3 mirror**: Most models focused on `pkg/chart/v2` and missed the parallel `internal/chart/v3` code
   - **Cross-cutting consumers**: `pkg/cmd/status.go`, `pkg/cmd/list.go`, `pkg/cmd/flags.go`, `pkg/cmd/search_repo.go`, `pkg/pusher/ocipusher.go`, `internal/resolver/resolver.go`
   - **Template strings**: `create.go` files with `.Chart.Version` / `.Chart.AppVersion` that break via MetadataAsMap reflection

5. **Most common false positives**:
   - `pkg/chart/v2/util/chartfile.go` (9 models listed it) -- it handles Metadata via YAML marshal/unmarshal, never accesses `.Version` directly
   - `pkg/action/get_metadata_test.go` -- tests `action.Metadata`, not `chart.Metadata`
   - `pkg/action/install.go` / `upgrade.go` / `lint.go` -- use release.Version (int) or action struct fields, not chart.Metadata

6. **Understanding the embedded struct pattern was critical**: The `ChartVersion` struct in `pkg/repo/v1/index.go` embeds `*chart.Metadata`, making all `ChartVersion.Version` access actually `Metadata.Version`. This was a key distinction that most models missed or only partially caught.
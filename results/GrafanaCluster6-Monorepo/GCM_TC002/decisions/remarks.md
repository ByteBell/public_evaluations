# GCM_TC002 Decision Remarks

## Source File
`api/v1beta1/grafana_types.go` — the root CRD type definition for the grafana-operator.

## Change Description
`AddNamespacedResource` gains a new required `dryRun bool` as its fifth positional
argument. All 10 existing call sites pass exactly 4 arguments and will fail to
compile with: `too few arguments in call to grafana.AddNamespacedResource`.

## Why Red Tier
`signature_change` maps directly to Red per the tier assignment table in
new_benchmark_plan.md. The method is not an interface (it is concrete on *Grafana)
but the pattern is the same: one signature change fans out to every call site.
With 9 production files + 1 test file all passing 4-arg calls, this is a
medium-high fan-out Red question.

## Impacted File Breakdown

### Production controllers (9 files)
| File | Lines with AddNamespacedResource call |
|---|---|
| controllers/dashboard_controller.go | 365, 384 |
| controllers/contactpoint_controller.go | 264 |
| controllers/librarypanel_controller.go | 226, 244 |
| controllers/notificationtemplate_controller.go | 159 |
| controllers/mutetiming_controller.go | 196 |
| controllers/datasource_controller.go | 328 |
| controllers/alertrulegroup_controller.go | 308, 359 |
| controllers/folder_controller.go | 276 |
| controllers/manifest_controller.go | 287, 297 |

### Test files (1 file)
| File | Notes |
|---|---|
| api/v1beta1/grafana_types_test.go | 8 direct calls at lines 128, 254, 274, 277, 408, 419, 439, 448, 462 |

## Common Hallucination Risks
- **False positive — RemoveNamespacedResource callers**: Models may include
  `controllers/dashboard_controller.go:295`, `contactpoint_controller.go:404`, etc.
  under RemoveNamespacedResource. These are NOT impacted — only AddNamespacedResource
  changed signature.
- **False negative — grafana_types_test.go**: Models that skip test files will
  miss this file, which has the highest call density (8 direct calls).
- **False negative — manifest_controller.go**: Two call sites; models may only
  find one.

## Ground Truth
Expected impacted files: 10 (9 production + 1 test). All severity: compile_error.

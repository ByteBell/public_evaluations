# SA_TC005 Analysis: IngressSpec.Rules Type Change Impact

## Question Description

**ID**: SA_TC005

**Change**: Modify the `Rules` field in `networkingv1.IngressSpec` (`k8s.io/api/networking/v1`) from `[]IngressRule` to a new named type `IngressRuleList` with different accessor methods.

**Impact**: Any code that ranges over `ingress.Spec.Rules`, appends to it, indexes into it, assigns a `[]IngressRule` literal to it, or uses `len()` on it will break, because `IngressRuleList` is not a plain slice.

---

## Actually Affected Files

**Total: 33 files across 6 repositories**

The ground truth was established by searching all 15 repositories in the dataset for Go files that directly access `.Spec.Rules` on a `networkingv1.Ingress` (or the corresponding internal `networking.Ingress` type used within the kubernetes repo). Files using other types' `.Spec.Rules` (e.g., FlowSchema, GatewayAPI HTTPRoute, Kong TCPIngress, AuthorizationPolicy) were excluded.

### ingress-nginx (17 files)

| # | File | Why Affected |
|---|------|-------------|
| 1 | `internal/k8s/main.go` | `for _, rule := range ing.Spec.Rules` -- ranges over Rules |
| 2 | `internal/ingress/controller/controller.go` | Multiple `for _, rule := range ing.Spec.Rules` and `len(ing.Spec.Rules)` |
| 3 | `internal/ingress/controller/controller_test.go` | `ing.Spec.Rules[0].Host = ...` (index), `ing.Spec.Rules = []networking.IngressRule{...}` (literal assign) |
| 4 | `internal/ingress/controller/store/store.go` | `for ri, rule := range copyIng.Spec.Rules` and index `copyIng.Spec.Rules[ri]` |
| 5 | `internal/ingress/controller/store/store_test.go` | `ni.Spec.Rules[0].Host = ...` (index) |
| 6 | `internal/ingress/controller/template/template.go` | `for _, rule := range ing.Spec.Rules` |
| 7 | `internal/ingress/inspector/ingress.go` | `for _, rule := range ingress.Spec.Rules` |
| 8 | `internal/ingress/inspector/inspector.go` | `for _, rule := range ing.Spec.Rules` |
| 9 | `internal/ingress/inspector/ingress_test.go` | `newIngress.Spec.Rules[0].IngressRuleValue.HTTP.Paths = append(...)` (index) |
| 10 | `cmd/plugin/commands/ingresses/ingresses.go` | `len(ing.Spec.Rules)` and `for _, rule := range ing.Spec.Rules` |
| 11 | `test/e2e/ingress/multiple_rules.go` | `ing.Spec.Rules = append(ing.Spec.Rules, ...)` (append) |
| 12 | `test/e2e/ingress/pathtype_exact.go` | `ing.Spec.Rules[0].IngressRuleValue.HTTP...` (index) |
| 13 | `test/e2e/ingress/pathtype_mixed.go` | `ing.Spec.Rules[0].IngressRuleValue.HTTP...` (index) |
| 14 | `test/e2e/admission/admission.go` | `invalidPath.Spec.Rules[0]...` (index) |
| 15 | `test/e2e/settings/disable_catch_all.go` | `ingress.Spec.Rules = nil` (assign) |
| 16 | `test/e2e/servicebackend/service_externalname.go` | `ing.Spec.Rules[0].HTTP.Paths[0].Backend = ...` (index) |
| 17 | `test/e2e/lua/dynamic_certificates.go` | `ing.Spec.Rules[0].Host = newHost` (index) |

### cert-manager (2 files)

| # | File | Why Affected |
|---|------|-------------|
| 18 | `pkg/issuer/acme/http/ingress.go` | `ing.Spec.Rules[0]` (index), `for _, rule := range ing.Spec.Rules` (range), `ing.Spec.Rules = append(...)` (append), `ing.Spec.Rules = ingRules` (assign) |
| 19 | `pkg/issuer/acme/http/ingress_test.go` | `resp[0].Spec.Rules[0]...` (index), `expectedIng.Spec.Rules = nil` (assign), `= []networkingv1.IngressRule{...}` (literal assign) |

### external-dns (2 files)

| # | File | Why Affected |
|---|------|-------------|
| 20 | `source/ingress.go` | `for _, rule := range ing.Spec.Rules` (range) |
| 21 | `source/ingress_test.go` | `ingress.Spec.Rules = append(ingress.Spec.Rules, networkv1.IngressRule{...})` (append), `Rules: []networkv1.IngressRule{}` (literal assign) |

### istio (1 file)

| # | File | Why Affected |
|---|------|-------------|
| 22 | `pilot/pkg/config/kube/ingress/ingress.go` | `for idx, rule := range i.Spec.Rules` -- ranges over `knetworking.Ingress` (alias for `k8s.io/api/networking/v1`) |

### cilium (1 file)

| # | File | Why Affected |
|---|------|-------------|
| 23 | `operator/pkg/model/ingestion/ingress.go` | `for _, rule := range ing.Spec.Rules` (twice) -- uses `networkingv1.Ingress` |

### kubernetes (10 files)

| # | File | Why Affected |
|---|------|-------------|
| 24 | `staging/src/k8s.io/api/networking/v1/types.go` | **Type definition**: `Rules []IngressRule` -- this is the source of the change |
| 25 | `pkg/apis/networking/types.go` | **Internal type definition**: `Rules []IngressRule` -- mirrors the v1 API type |
| 26 | `pkg/apis/networking/validation/validation.go` | `for _, rule := range oldIngress.Spec.Rules` (range, uses internal type) |
| 27 | `pkg/apis/networking/validation/validation_test.go` | `ing.Spec.Rules[0]...` (index), `ing.Spec.Rules = []networking.IngressRule{}` (literal assign), many more |
| 28 | `pkg/printers/internalversion/printers.go` | `formatHosts(obj.Spec.Rules)` passes Rules as `[]networking.IngressRule` param, `for _, rule := range rules` |
| 29 | `pkg/registry/networking/ingress/storage/storage_test.go` | `.Spec.Rules = []networking.IngressRule{}` (literal assign) |
| 30 | `staging/src/k8s.io/kubectl/pkg/cmd/create/create_ingress.go` | `ingressSpec.Rules = o.buildIngressRules()` where return type is `[]networkingv1.IngressRule` (assign) |
| 31 | `staging/src/k8s.io/kubectl/pkg/describe/describe.go` | `for _, rules := range ing.Spec.Rules` -- uses `*networkingv1.Ingress` |
| 32 | `test/e2e/framework/ingress/ingress_utils.go` | `for _, rule := range ing.Spec.Rules` (range), `ing.Spec.Rules = newRules` (assign) |
| 33 | `test/e2e/network/ingress.go` | `ingress1.Spec.Rules[0].Host = ...` (index) |

---

## Files NOT Affected (mentioned by models but not in ground truth)

These files were cited by one or more models but do NOT directly access `networkingv1.IngressSpec.Rules` or do not use the networking/v1 Ingress type:

| File | Repo | Why NOT Affected |
|------|------|-----------------|
| `pkg/apis/ingress/types.go` | ingress-nginx | Does not contain `Spec.Rules`; defines internal ingress-nginx types |
| `pkg/controller/certificaterequests/sync.go` | cert-manager | Does not reference `Spec.Rules` at all |
| `pkg/controller/certificaterequests/vault/vault.go` | cert-manager | Does not reference `Spec.Rules` at all |
| `source/kong_tcpingress.go` | external-dns | Uses custom `tcpIngressSpec` with `[]tcpIngressRule` (Kong type), NOT `networkingv1.IngressSpec` |
| `pkg/controller/certificate-shim/sync.go` | cert-manager | Does not contain `Spec.Rules`; references `Spec.TLS` and ingress annotations only |
| `pkg/controller/certificate-shim/ingresses/controller.go` | cert-manager | Does not contain `Spec.Rules`; handles controller setup only |
| `internal/admission/controller/main.go` | ingress-nginx | Does not contain `Spec.Rules` |
| `cmd/plugin/lints/ingress.go` | ingress-nginx | Does not contain `Spec.Rules` |
| `internal/ingress/controller/nginx.go` | ingress-nginx | Does not contain `Spec.Rules` |
| `pilot/pkg/config/kube/ingress/virtualservices.go` | istio | Does not contain `Spec.Rules` |
| `pilot/pkg/config/kube/ingress/gateways.go` | istio | Does not contain `Spec.Rules` |
| `operator/pkg/ingress/ingress.go` | cilium | Does not contain `Spec.Rules` for networking/v1 Ingress |
| `operator/pkg/ingress/secretsync.go` | cilium | Does not contain `Spec.Rules` |
| `pkg/policy/api/ingress.go` | cilium | Does not contain `Spec.Rules` related to networking/v1 Ingress |
| `staging/src/k8s.io/client-go/applyconfigurations/networking/v1/ingress.go` | kubernetes | Does not contain `Spec.Rules`; generated apply config wrapper |
| `staging/src/k8s.io/client-go/applyconfigurations/networking/v1beta1/ingress.go` | kubernetes | Does not contain `Spec.Rules` |
| `staging/src/k8s.io/client-go/applyconfigurations/networking/v1beta1/ingressspec.go` | kubernetes | Independent type (`IngressSpecApplyConfiguration`), not `networkingv1.IngressSpec` |
| `staging/src/k8s.io/client-go/applyconfigurations/extensions/v1beta1/ingressspec.go` | kubernetes | Independent type, not `networkingv1.IngressSpec` |
| `staging/src/k8s.io/client-go/applyconfigurations/networking/v1beta1/ingressrule.go` | kubernetes | Independent type, not `networkingv1.IngressRule` |
| `staging/src/k8s.io/client-go/applyconfigurations/extensions/v1beta1/ingressrule.go` | kubernetes | Independent type |
| `staging/src/k8s.io/client-go/applyconfigurations/networking/v1/ingressrule.go` | kubernetes | Independent type |
| `staging/src/k8s.io/client-go/informers/networking/v1/ingress.go` | kubernetes | Does not contain `Spec.Rules`; generated informer boilerplate |
| `staging/src/k8s.io/client-go/listers/networking/v1/ingress.go` | kubernetes | Does not contain `Spec.Rules`; generated lister boilerplate |
| `staging/src/k8s.io/client-go/kubernetes/typed/networking/v1/ingress.go` | kubernetes | Does not contain `Spec.Rules`; generated typed client |
| `staging/src/k8s.io/api/networking/v1/doc.go` | kubernetes | Package doc file, no code |
| `staging/src/k8s.io/api/networking/v1beta1/types.go` | kubernetes | Separate API version (v1beta1), independent type definition |
| `staging/src/k8s.io/api/extensions/v1beta1/types.go` | kubernetes | Separate API version (extensions/v1beta1), independent type definition |
| `pkg/apis/networking/v1beta1/conversion.go` | kubernetes | Does not contain `Spec.Rules` |
| `pkg/apis/extensions/v1beta1/conversion.go` | kubernetes | Does not contain `Spec.Rules` |
| `pkg/registry/networking/ingress/strategy.go` | kubernetes | Does not contain `Spec.Rules` |
| `api/discovery/apis__networking.k8s.io__v1.json` | kubernetes | JSON file, not Go code |
| `addon-resizer/vendor/k8s.io/api/networking/v1/types.go` | autoscaler | Vendored type definition only; no code in autoscaler accesses Spec.Rules |
| `addon-resizer/vendor/k8s.io/api/extensions/v1beta1/types.go` | autoscaler | Vendored type definition only |
| `controller/controller.go` | external-dns | Does not contain `Spec.Rules` |

**Note on `staging/src/k8s.io/client-go/applyconfigurations/networking/v1/ingressspec.go`**: This file defines its own `Rules []IngressRuleApplyConfiguration` field and uses `append` on it. It is generated code that mirrors the API type structure. When `IngressSpec.Rules` changes from `[]IngressRule` to `IngressRuleList`, the apply configuration generator would produce different output. This file is therefore NOT included in the ground truth since it operates on its own independently-typed `Rules` field, not on `networkingv1.IngressSpec.Rules`. However, models that cite it receive partial credit as it would need regeneration in practice.

---

## Model Accuracy

### Scoring Methodology

- **True Positive (TP)**: File cited by model AND in ground truth
- **False Positive (FP)**: File cited by model but NOT in ground truth (includes hallucinated files)
- **False Negative (FN)**: File in ground truth but NOT cited by model
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 * Precision * Recall / (Precision + Recall)

### Model Results

| Model | Status | Files Cited | TP | FP | FN (of 33) | Precision | Recall | F1 Score |
|-------|--------|-------------|----|----|------------|-----------|--------|----------|
| anthropic/claude-haiku-4.5 | timeout | 0 | 0 | 0 | 33 | N/A | 0.0% | 0.0% |
| arcee-ai/trinity-large-preview | success | 7 | 3 | 4 | 30 | 42.9% | 9.1% | 15.0% |
| deepseek/deepseek-chat-v3.1 | success | 6 | 5 | 1 | 28 | 83.3% | 15.2% | 25.6% |
| deepseek/deepseek-v3.2 | success | 17 | 4 | 13 | 29 | 23.5% | 12.1% | 16.0% |
| google/gemini-3-flash-preview | error | 0 | 0 | 0 | 33 | N/A | 0.0% | 0.0% |
| minimax/minimax-m2.5 | success | 11 | 4 | 7 | 29 | 36.4% | 12.1% | 18.2% |
| openai/gpt-5.1-codex-max | error | 0 | 0 | 0 | 33 | N/A | 0.0% | 0.0% |
| openai/gpt-oss-120b | success | 16 | 8 | 8 | 25 | 50.0% | 24.2% | 32.7% |
| stepfun/step-3.5-flash | success | 14 | 4 | 10 | 29 | 28.6% | 12.1% | 17.0% |
| x-ai/grok-code-fast-1 | success | 8 | 4 | 4 | 29 | 50.0% | 12.1% | 19.5% |
| xiaomi/mimo-v2-flash | success | 14 | 4 | 10 | 29 | 28.6% | 12.1% | 17.0% |
| z-ai/glm-4.7-flash | success | 13 | 5 | 8 | 28 | 38.5% | 15.2% | 21.7% |

### Detailed Model Breakdowns

#### arcee-ai/trinity-large-preview (TP=3, FP=4)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `internal/ingress/controller/store/store.go` (ingress-nginx)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)

**False Positives:**
- `pkg/apis/ingress/types.go` (ingress-nginx) -- no Spec.Rules usage
- `pkg/controller/certificaterequests/sync.go` (cert-manager) -- no Spec.Rules
- `source/kong_tcpingress.go` (external-dns) -- uses custom Kong type
- `pkg/controller/certificaterequests/vault/vault.go` (cert-manager) -- no Spec.Rules

#### deepseek/deepseek-chat-v3.1 (TP=5, FP=1)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `internal/ingress/controller/controller_test.go` (ingress-nginx)
- `source/ingress.go` (external-dns)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)
- `source/ingress_test.go` (external-dns)

**False Positives:**
- `pkg/controller/certificate-shim/sync.go` (cert-manager) -- no Spec.Rules

#### deepseek/deepseek-v3.2 (TP=4, FP=13)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `source/ingress.go` (external-dns)
- `cmd/plugin/commands/ingresses/ingresses.go` (ingress-nginx)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)

**False Positives (13):**
- `internal/admission/controller/main.go`, `cmd/plugin/lints/ingress.go` (ingress-nginx)
- `staging/.../v1beta1/ingress.go`, `staging/.../v1beta1/types.go`, `staging/.../v1beta1/ingressspec.go`, `staging/.../v1/ingress.go`, `staging/.../extensions/v1beta1/types.go`, `staging/.../v1/ingressspec.go`, `api/discovery/...json` (kubernetes)
- `pkg/controller/certificate-shim/ingresses/controller.go`, `pkg/controller/certificate-shim/sync.go` (cert-manager)
- 2 hallucinated files

#### minimax/minimax-m2.5 (TP=4, FP=7)
**True Positives:**
- `source/ingress.go` (external-dns)
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `pilot/pkg/config/kube/ingress/ingress.go` (istio)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)

**False Positives (7):**
- `pkg/controller/certificate-shim/ingresses/controller.go` (cert-manager)
- `operator/pkg/ingress/ingress.go`, `operator/pkg/ingress/secretsync.go` (cilium)
- `staging/.../v1/ingressspec.go` (kubernetes - independent type)
- `staging/.../informers/.../ingress.go` (kubernetes)
- 1 hallucinated file (`discovery/kubernetes/ingress.go`)

#### openai/gpt-oss-120b (TP=8, FP=8)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `internal/ingress/controller/store/store.go` (ingress-nginx)
- `internal/ingress/inspector/ingress.go` (ingress-nginx)
- `pkg/apis/networking/validation/validation.go` (kubernetes)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)
- `test/e2e/framework/ingress/ingress_utils.go` (kubernetes)
- `staging/src/k8s.io/kubectl/pkg/cmd/create/create_ingress.go` (kubernetes)
- `pilot/pkg/config/kube/ingress/ingress.go` (istio)

**False Positives (8):**
- `source/kong_tcpingress.go` (external-dns) -- Kong type
- `pkg/policy/api/ingress.go` (cilium) -- not networking/v1
- `pilot/pkg/config/kube/ingress/virtualservices.go` (istio) -- no Spec.Rules
- `pkg/apis/networking/v1beta1/conversion.go` (kubernetes) -- no Spec.Rules
- `staging/.../v1/doc.go` (kubernetes) -- doc file
- `staging/.../typed/.../ingress.go` (kubernetes) -- no Spec.Rules
- `pkg/apis/extensions/v1beta1/conversion.go` (kubernetes) -- no Spec.Rules
- `staging/.../v1/ingressspec.go` (kubernetes - independent type)

#### stepfun/step-3.5-flash (TP=4, FP=10)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `pkg/apis/networking/types.go` (kubernetes)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)
- `pilot/pkg/config/kube/ingress/ingress.go` (istio)

**False Positives (10):**
- `source/kong_tcpingress.go` (external-dns), `pkg/policy/api/ingress.go` (cilium)
- `staging/.../v1/ingressspec.go`, `staging/.../informers/...`, `staging/.../listers/...` (kubernetes)
- `pkg/registry/networking/ingress/strategy.go` (kubernetes)
- `pkg/controller/certificate-shim/ingresses/controller.go` (cert-manager)
- `controller/controller.go` (external-dns)
- 2 hallucinated files

#### x-ai/grok-code-fast-1 (TP=4, FP=4)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `cmd/plugin/commands/ingresses/ingresses.go` (ingress-nginx)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)
- `pkg/issuer/acme/http/ingress.go` (cert-manager)

**False Positives (4):**
- `staging/.../v1/ingressspec.go` (kubernetes - independent type)
- `pkg/apis/networking/v1beta1/conversion.go` (kubernetes)
- `pkg/controller/certificate-shim/sync.go` (cert-manager)
- 1 hallucinated file

#### xiaomi/mimo-v2-flash (TP=4, FP=10)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `internal/ingress/controller/controller_test.go` (ingress-nginx)
- `pilot/pkg/config/kube/ingress/ingress.go` (istio)
- `staging/src/k8s.io/api/networking/v1/types.go` (kubernetes)

**False Positives (10):**
- `pkg/apis/ingress/types.go` (ingress-nginx)
- `source/kong_tcpingress.go` (external-dns)
- 5 v1beta1/extensions apply config and type files (kubernetes)
- `staging/.../v1/ingressspec.go`, `staging/.../v1/ingressrule.go` (kubernetes - independent types)
- `addon-resizer/vendor/.../types.go` (autoscaler - vendored, unused)

#### z-ai/glm-4.7-flash (TP=5, FP=8)
**True Positives:**
- `internal/ingress/controller/controller.go` (ingress-nginx)
- `internal/ingress/controller/store/store.go` (ingress-nginx)
- `source/ingress.go` (external-dns)
- `source/ingress_test.go` (external-dns)
- `pilot/pkg/config/kube/ingress/ingress.go` (istio)

**False Positives (8):**
- `internal/ingress/controller/nginx.go` (ingress-nginx)
- `pkg/controller/certificate-shim/sync.go`, `pkg/controller/certificate-shim/ingresses/controller.go` (cert-manager)
- `pilot/pkg/config/kube/ingress/virtualservices.go`, `pilot/pkg/config/kube/ingress/gateways.go` (istio)
- `staging/.../listers/...`, `staging/.../informers/...`, `staging/.../v1/ingress.go` (kubernetes)

---

## Key Findings

### 1. Best Performing Model: openai/gpt-oss-120b
- Highest recall (24.2%) and F1 (32.7%) among all models
- Found 8 true positives across 4 repos (ingress-nginx, kubernetes, istio)
- Only model to identify `pkg/apis/networking/validation/validation.go`, `test/e2e/framework/ingress/ingress_utils.go`, `staging/src/k8s.io/kubectl/pkg/cmd/create/create_ingress.go`, and `internal/ingress/inspector/ingress.go`

### 2. Best Precision: deepseek/deepseek-chat-v3.1
- Highest precision (83.3%) with only 1 false positive out of 6 files cited
- Conservative but accurate approach

### 3. Common Errors Across Models
- **Kong TCPIngress confusion**: 4 models cited `source/kong_tcpingress.go` (external-dns) which uses a custom `tcpIngressSpec` type, not `networkingv1.IngressSpec`
- **cert-manager certificate-shim**: 5 models cited `pkg/controller/certificate-shim/sync.go` or its controller, which do not access `Spec.Rules`
- **Generated client/informer/lister boilerplate**: Several models cited generated Kubernetes client-go files (informers, listers, typed clients) that do not access `Spec.Rules`
- **v1beta1/extensions confusion**: Multiple models cited v1beta1 or extensions types as affected, which are separate API versions
- **Apply configuration confusion**: Multiple models cited the apply configuration `ingressspec.go` which defines its own independent `Rules` field

### 4. Massively Underestimated Scope
- All models found at most 8 of the 33 affected files (24.2% recall)
- The ingress-nginx repo alone has 17 affected files (including test/e2e files), but most models found only 1-3 files there
- No model found any of the ingress-nginx e2e test files (7 files)
- No model found `internal/k8s/main.go`, `internal/ingress/controller/template/template.go`, or `internal/ingress/inspector/inspector.go` from ingress-nginx (gpt-oss-120b found the inspector)
- The cert-manager `pkg/issuer/acme/http/ingress.go` was found by only 1 model (grok-code-fast-1)
- The cilium `operator/pkg/model/ingestion/ingress.go` was found by 0 models despite directly ranging over `networkingv1.Ingress.Spec.Rules`
- No model found `staging/src/k8s.io/kubectl/pkg/describe/describe.go` or `pkg/printers/internalversion/printers.go`

### 5. Hallucinated Files
Three files were hallucinated by models (cited but do not exist in any repo in the dataset):
- `extension/observer/k8sobserver/ingress_endpoint.go` (cited by deepseek-v3.2 and step-3.5-flash)
- `discovery/kubernetes/ingress.go` (cited by deepseek-v3.2, minimax-m2.5, step-3.5-flash, and grok-code-fast-1)

---

## Summary

This question tests a model's ability to trace the impact of a breaking type change in a core Kubernetes API across multiple downstream consumers. The actual blast radius is 33 files across 6 repositories (ingress-nginx, cert-manager, external-dns, istio, cilium, kubernetes). The best-performing model (gpt-oss-120b) achieved only 24.2% recall, finding 8 of 33 files. Every model failed to identify the majority of affected files, particularly in test code and less obvious consumer files. The most common false positive was confusing similar-looking `.Spec.Rules` accesses on non-Ingress types (Kong TCPIngress, Cilium policy) or citing files that interact with Ingress objects but never access the `.Spec.Rules` field directly.

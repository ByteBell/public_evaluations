# Dataset Small - Questions Reference

Complete catalog of all 30 cross-repository impact analysis test cases from `sample_questions.json`.

## Summary

- **Total test cases:** 30
- **Categories:** MIXED (Kubernetes + Observability cross-stack), OBS (Observability stack)
- **Repos covered:** 15 (kubernetes, argo-cd, cert-manager, helm, ingress-nginx, external-dns, external-secrets, grafana, prometheus, thanos, mimir, loki, opentelemetry-operator, opentelemetry-collector-contrib, jaeger, tempo)

### Categories

| Prefix | Description | Count |
|--------|-------------|-------|
| MIXED | Kubernetes + Observability cross-stack | 10 |
| OBS | Observability stack | 20 |

### Corrections Summary

All 30 questions were cross-checked against the actual source code in the dataset repositories. **30 out of 30 (100%)** had at least one incorrect file reference before corrections were applied. The original accuracy was approximately **37%** across all listed files.

| Issue Type | Count | Description |
|-----------|-------|-------------|
| Wrong file paths | 23 | Listed files did not exist or did not contain the claimed code pattern |
| Flawed question premise | 7 | The source type/interface was internal or private with no actual cross-repo impact |
| Incorrect repos listed | 15 | Repos were listed that don't actually use the claimed API or pattern |
| Total questions corrected | **30** | Every question required at least one file correction |

See the [Detailed Corrections Log](#detailed-corrections-log) at the end for per-question details.

## All Questions

| # | ID | Source Repo | Source File | Change Type | Affected Repos | Files |
|---|-----|------------|------------|-------------|----------------|-------|
| 1 | MIXED_TC001 | kubernetes | `shared_informer.go` | interface modification | 4 | 15 |
| 2 | MIXED_TC002 | kubernetes | `config.go` | struct field change | 4 | 7 |
| 3 | MIXED_TC003 | kubernetes | `types.go` | struct field modification | 4 | 7 |
| 4 | MIXED_TC004 | kubernetes | `types.go` | struct field modification | 5 | 9 |
| 5 | MIXED_TC005 | kubernetes | `selector.go` | interface modification | 4 | 9 |
| 6 | MIXED_TC006 | kubernetes | `types.go` | struct field modification | 4 | 11 |
| 7 | MIXED_TC007 | kubernetes | `types.go` | struct field modification | 6 | 20 |
| 8 | MIXED_TC008 | kubernetes | `interface.go` | interface modification | 3 | 6 |
| 9 | MIXED_TC009 | kubernetes | `scheme.go` | method signature change | 4 | 7 |
| 10 | MIXED_TC010 | kubernetes | `clientset.go` | interface modification | 5 | 9 |
| 11 | OBS_TC001 | prometheus | `interface.go` | interface modification | 2 | 8 |
| 12 | OBS_TC002 | prometheus | `labels_common.go` | type change | 3 | 11 |
| 13 | OBS_TC003 | prometheus | `histogram.go` | struct field change | 2 | 7 |
| 14 | OBS_TC004 | prometheus | `db.go` | method signature change | 2 | 3 |
| 15 | OBS_TC005 | prometheus | `engine.go` | interface modification | 2 | 6 |
| 16 | OBS_TC006 | prometheus | `interface_append.go` | interface modification | 3 | 7 |
| 17 | OBS_TC007 | prometheus | `config.go` | struct field change | 1 | 1 |
| 18 | OBS_TC008 | prometheus | `matcher.go` | type change | 3 | 14 |
| 19 | OBS_TC009 | prometheus | `discovery.go` | interface modification | 1 | 2 |
| 20 | OBS_TC010 | prometheus | `compact.go` | interface modification | 2 | 4 |
| 21 | OBS_TC011 | opentelemetry-collector | `component.go` | interface modification | 3 | 8 |
| 22 | OBS_TC012 | opentelemetry-collector | `metrics.go` | interface modification | 1 | 2 |
| 23 | OBS_TC013 | opentelemetry-collector | `exporter.go` | struct field change | 2 | 3 |
| 24 | OBS_TC014 | opentelemetry-collector | `receiver.go` | method signature change | 2 | 3 |
| 25 | OBS_TC015 | opentelemetry-collector | `config.go` | interface modification | 3 | 6 |
| 26 | OBS_TC016 | opentelemetry-collector | `identifiable.go` | type change | 2 | 6 |
| 27 | OBS_TC017 | opentelemetry-collector | `error.go` | type change | 1 | 3 |
| 28 | OBS_TC018 | opentelemetry-collector | `host.go` | interface modification | 2 | 4 |
| 29 | OBS_TC019 | thanos | `bucket.go` | interface modification | 1 | 2 |
| 30 | OBS_TC020 | thanos | `compact.go` | interface modification | 1 | 3 |
| 31 | OBS_TC021 | thanos | `querier.go` | method signature change | 1 | 3 |
| 32 | OBS_TC022 | thanos | `planner.go` | interface modification | 1 | 4 |
| 33 | OBS_TC023 | grafana | `types.go` | struct field change | 1 | 3 |
| 34 | OBS_TC024 | grafana | `storage.go` | interface modification | 1 | 4 |
| 35 | OBS_TC025 | grafana | `datasource.go` | method signature change | 1 | 1 |
| 36 | OBS_TC026 | grafana | `prometheus_metrics_middleware.go` | interface modification | 1 | 2 |
| 37 | OBS_TC027 | jaeger | `extension.go` | interface modification | 1 | 4 |
| 38 | OBS_TC028 | jaeger | `exporter.go` | struct field change | 1 | 2 |
| 39 | OBS_TC029 | opentelemetry-collector-contrib | `accumulator.go` | interface modification | 1 | 2 |
| 40 | OBS_TC030 | opentelemetry-collector-contrib | `trace_receiver.go` | struct field change | 3 | 3 |

## Detailed Questions

### 1. MIXED_TC001

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/cache/shared_informer.go`
**Change type:** interface_modification
**Change:** Add `WaitForCacheSync(ctx context.Context) bool` method to SharedInformer interface
**Repos involved:** 4 | **Affected files:** 15

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `appcontroller.go`, `cache.go`, `server.go` | ArgoCD controllers use SharedInformer for watching Application CRDs, Secrets, and cluster resources |
| cert-manager | `issuing_controller.go`, `trigger_controller.go`, `core_filteredsecrets.go`, `factory.go` | Cert-manager controllers use SharedInformer for watching Certificates, CertificateRequests, and Secrets |
| prometheus | `kubernetes.go`, `pod.go`, `service.go`, `node.go`, `endpoints.go`, `endpointslice.go` | Prometheus Kubernetes service discovery uses SharedInformer to watch Pods, Services, Nodes, Endpoints, and EndpointSlice |
| opentelemetry-operator | `promOperator.go`, `collector.go` | OpenTelemetry Operator target allocator uses SharedInformer for watching collectors and Prometheus operator CRDs |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `controller/appcontroller.go`
- `controller/cache/cache.go`
- `server/server.go`
**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/issuing_controller.go`
- `pkg/controller/certificates/trigger/trigger_controller.go`
- `internal/informers/core_filteredsecrets.go`
- `pkg/client/informers/externalversions/factory.go`
**prometheus/prometheus:**
- `discovery/kubernetes/kubernetes.go`
- `discovery/kubernetes/pod.go`
- `discovery/kubernetes/service.go`
- `discovery/kubernetes/node.go`
- `discovery/kubernetes/endpoints.go`
- `discovery/kubernetes/endpointslice.go`
**open-telemetry/opentelemetry-operator:**
- `cmd/otel-allocator/internal/watcher/promOperator.go`
- `cmd/otel-allocator/internal/collector/collector.go`

</details>

### 2. MIXED_TC002

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/rest/config.go`
**Change type:** struct_field_change
**Change:** Change `TLSClientConfig TLSClientConfig` to `TLSClientConfig *TLSClientConfig` (value to pointer)
**Repos involved:** 4 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `types.go` | Directly assigns rest.TLSClientConfig struct literals for multi-cluster TLS configuration |
| ingress-nginx | `main.go` | Creates rest.TLSClientConfig{} and assigns CAFile before setting cfg.TLSClientConfig |
| external-secrets | `auth.go` | Assigns cfg.TLSClientConfig = rest.TLSClientConfig{} for cross-cluster secret access |
| grafana | `config.go`, `zanzana_folder_reconciler.go`, `rbac.go`, `service.go` | Constructs rest.TLSClientConfig{} for operator provisioning, IAM, authorization, and API server setup |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `pkg/apis/application/v1alpha1/types.go`
**kubernetes/ingress-nginx:**
- `cmd/nginx/main.go`
**external-secrets/external-secrets:**
- `providers/v1/kubernetes/auth.go`
**grafana/grafana:**
- `pkg/operators/provisioning/config.go`
- `pkg/operators/iam/zanzana_folder_reconciler.go`
- `pkg/services/authz/rbac.go`
- `pkg/services/apiserver/service.go`

</details>

### 3. MIXED_TC003

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Containers []Container` to `Containers ContainerList` where ContainerList is a new named type
**Repos involved:** 4 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `info.go`, `terminal.go` | Uses len() and range on pod.Spec.Containers for pod info extraction and terminal exec |
| cert-manager | `pod.go` | Constructs Containers: []corev1.Container{} and accesses pod.Spec.Containers[0] for ACME HTTP-01 challenge pods |
| prometheus | `pod.go` | Iterates pod.Spec.Containers to extract container names, ports, and image info for scrape target labels |
| opentelemetry-operator | `sdk.go`, `helper.go`, `pod.go` | Accesses pod.Spec.Containers with len(), range, and index for auto-instrumentation injection and sidecar management |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `controller/cache/info.go`
- `server/application/terminal.go`
**cert-manager/cert-manager:**
- `pkg/issuer/acme/http/pod.go`
**prometheus/prometheus:**
- `discovery/kubernetes/pod.go`
**open-telemetry/opentelemetry-operator:**
- `internal/instrumentation/sdk.go`
- `internal/instrumentation/helper.go`
- `pkg/sidecar/pod.go`

</details>

### 4. MIXED_TC004

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Type ServiceType` to `Type *ServiceType` (value to pointer) in ServiceSpec
**Repos involved:** 5 | **Affected files:** 9

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `ready.go` | Checks Service.Spec.Type for LoadBalancer readiness evaluation |
| argo-cd | `health_service.go` | Checks Service.Spec.Type for health status and load balancer ingress status |
| ingress-nginx | `store.go`, `endpointslices.go`, `controller.go`, `status.go` | Accesses Service.Spec.Type for backend routing, endpoint resolution, and status reporting |
| external-dns | `service.go`, `compatibility.go` | Reads Service.Spec.Type to determine DNS endpoint generation and compatibility handling |
| prometheus | `service.go` | Reads svc.Spec.Type for service-level target discovery and label generation |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/ready.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/health/health_service.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`
- `internal/ingress/controller/endpointslices.go`
- `internal/ingress/controller/controller.go`
- `internal/ingress/status/status.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`
- `source/compatibility.go`
**prometheus/prometheus:**
- `discovery/kubernetes/service.go`

</details>

### 5. MIXED_TC005

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/labels/selector.go`
**Change type:** interface_modification
**Change:** Change `Matches(labels Labels) bool` to `Matches(ctx context.Context, labels Labels) bool` in Selector interface
**Repos involved:** 4 | **Affected files:** 9

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `list.go` | Calls selector.Matches(labels.Set(rls.Labels)) for filtering releases by label selector |
| argo-cd | `application.go`, `selector.go`, `generator_spec_processor.go` | Calls selector.Matches() for application event filtering and generator parameter filtering |
| external-dns | `source.go`, `gateway.go`, `filter.go`, `indexers.go` | Calls selector.Matches() for filtering source resources, gateways, annotations, and informer indexing |
| ingress-nginx | `store.go` | Calls namespaceSelector.Matches(labels.Set(ns.Labels)) for namespace filtering |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/action/list.go`
**argoproj/argo-cd:**
- `server/application/application.go`
- `applicationset/utils/selector.go`
- `applicationset/generators/generator_spec_processor.go`
**kubernetes-sigs/external-dns:**
- `source/source.go`
- `source/gateway.go`
- `source/annotations/filter.go`
- `source/informers/indexers.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`

</details>

### 6. MIXED_TC006

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Data map[string][]byte` to `Data SecretData` (new named type) on corev1.Secret
**Repos involved:** 4 | **Affected files:** 11

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `secrets.go` | Stores release data in Secret.Data map, encoding release metadata as base64 byte values |
| argo-cd | `secrets.go`, `repository_secrets.go`, `cluster.go`, `settings.go` | Stores and reads cluster/repo credentials and settings from Secret.Data |
| cert-manager | `secret.go`, `sources.go`, `vault.go`, `dns.go`, `venaficlient.go` | Reads/writes TLS certificates, keys, Vault credentials, DNS provider credentials, and Venafi credentials from Secret.Data |
| external-secrets | `pushsecret_controller.go` | Reads secret.Data[key] to check key existence and push secret values to external providers |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/storage/driver/secrets.go`
**argoproj/argo-cd:**
- `util/db/secrets.go`
- `util/db/repository_secrets.go`
- `util/db/cluster.go`
- `util/settings/settings.go`
**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/internal/secret.go`
- `pkg/controller/cainjector/sources.go`
- `internal/vault/vault.go`
- `pkg/issuer/acme/dns/dns.go`
- `pkg/issuer/venafi/client/venaficlient.go`
**external-secrets/external-secrets:**
- `pkg/controllers/pushsecret/pushsecret_controller.go`

</details>

### 7. MIXED_TC007

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Labels map[string]string` to `Labels LabelMap` (new named type requiring accessor methods) in ObjectMeta
**Repos involved:** 6 | **Affected files:** 20

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `appcontroller.go`, `settings.go` | Directly accesses ObjectMeta.Labels map for application resource labeling and settings |
| cert-manager | `pod.go`, `service.go`, `ingress.go` | Constructs ObjectMeta with Labels map literals for ACME challenge resources |
| external-secrets | `externalsecret_controller.go`, `webhookconfig.go`, `clusterexternalsecret_types.go` | Directly accesses .Labels[key], assigns Labels = make(map[string]string), defines Labels map field |
| prometheus | `kubernetes.go`, `pod.go`, `node.go`, `service.go` | Reads ObjectMeta.Labels for __meta_kubernetes_*_label_* target label construction |
| loki | `config.go`, `distributor.go`, `compactor.go`, `gateway.go` | Loki Operator constructs resources with ObjectMeta.Labels for all components |
| opentelemetry-operator | `opentelemetrycollector_types.go`, `service.go`, `pod.go`, `mutate.go` | CRD types use Labels, sets pod.Labels, assigns existing.Labels = desired.Labels |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `controller/appcontroller.go`
- `util/settings/settings.go`
**cert-manager/cert-manager:**
- `pkg/issuer/acme/http/pod.go`
- `pkg/issuer/acme/http/service.go`
- `pkg/issuer/acme/http/ingress.go`
**external-secrets/external-secrets:**
- `pkg/controllers/externalsecret/externalsecret_controller.go`
- `pkg/controllers/webhookconfig/webhookconfig.go`
- `apis/externalsecrets/v1/clusterexternalsecret_types.go`
**prometheus/prometheus:**
- `discovery/kubernetes/kubernetes.go`
- `discovery/kubernetes/pod.go`
- `discovery/kubernetes/node.go`
- `discovery/kubernetes/service.go`
**grafana/loki:**
- `operator/internal/manifests/config.go`
- `operator/internal/manifests/distributor.go`
- `operator/internal/manifests/compactor.go`
- `operator/internal/manifests/gateway.go`
**open-telemetry/opentelemetry-operator:**
- `apis/v1beta1/opentelemetrycollector_types.go`
- `internal/manifests/collector/service.go`
- `pkg/sidecar/pod.go`
- `internal/manifests/mutate.go`

</details>

### 8. MIXED_TC008

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/dynamic/interface.go`
**Change type:** interface_modification
**Change:** Change `List` return type on `dynamic.ResourceInterface` from `(*unstructured.UnstructuredList, error)` to `(PaginatedList, error)`
**Repos involved:** 3 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `lookup_func.go` | Template engine uses dynamic client to look up arbitrary K8s resources during chart rendering |
| argo-cd | `sync_context.go`, `cluster.go`, `controller.go` | Calls dynamic.ResourceInterface.List() for sync operations, cache population, and notification controller |
| grafana | `client.go`, `retry_client.go` | Provisioning system uses dynamic client for listing Kubernetes resources with retry logic |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/engine/lookup_func.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/sync/sync_context.go`
- `gitops-engine/pkg/cache/cluster.go`
- `notification_controller/controller/controller.go`
**grafana/grafana:**
- `pkg/registry/apis/provisioning/resources/client.go`
- `pkg/registry/apis/provisioning/resources/retry_client.go`

</details>

### 9. MIXED_TC009

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/scheme.go`
**Change type:** method_signature_change
**Change:** Change `AddKnownTypes` from variadic `Object` arguments to requiring a typed `TypeRegistration` struct
**Repos involved:** 4 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cert-manager | `register.go` | Calls scheme.AddKnownTypes to register Certificate, Issuer, and ClusterIssuer CRD types |
| external-secrets | `register.go` | Registers SecretStore, ExternalSecret, and ClusterExternalSecret CRD types |
| grafana | `zz_generated.defaults.go`, `register.go`, `register.go` | Registers alerting enrichment, provisioning API types |
| opentelemetry-operator | `groupversion_info.go`, `groupversion_info.go` | Registers OpenTelemetryCollector, Instrumentation, and OpAMPBridge CRD types |

<details>
<summary>Full file paths</summary>

**cert-manager/cert-manager:**
- `pkg/apis/certmanager/v1/register.go`
**external-secrets/external-secrets:**
- `apis/externalsecrets/v1/register.go`
**grafana/grafana:**
- `apps/alerting/alertenrichment/pkg/apis/alertenrichment/v1beta1/zz_generated.defaults.go`
- `apps/provisioning/pkg/generated/clientset/versioned/scheme/register.go`
- `apps/provisioning/pkg/apis/provisioning/v0alpha1/register.go`
**open-telemetry/opentelemetry-operator:**
- `apis/v1beta1/groupversion_info.go`
- `apis/v1alpha1/groupversion_info.go`

</details>

### 10. MIXED_TC010

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/kubernetes/clientset.go`
**Change type:** interface_modification
**Change:** Add `HealthCheck(ctx context.Context) error` to the `kubernetes.Interface` (Clientset interface)
**Repos involved:** 5 | **Affected files:** 9

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `action.go` | Calls kubernetes.NewForConfig(conf) for Kubernetes API operations during chart actions |
| argo-cd | `argocd_server.go` | Calls kubernetes.NewForConfigOrDie(config) for API server communication and cluster management |
| cert-manager | `webhook.go`, `authority.go`, `provider.go` | Calls kubernetes.NewForConfig for webhook, TLS authority, and DNS provider operations |
| grafana | `client.go`, `short_url.go` | Calls kubernetes.NewForConfig() for star API and short URL API operations |
| opentelemetry-operator | `main.go`, `main.go` | Calls kubernetes.NewForConfig for operator initialization and target allocator |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/action/action.go`
**argoproj/argo-cd:**
- `cmd/argocd-server/commands/argocd_server.go`
**cert-manager/cert-manager:**
- `internal/webhook/webhook.go`
- `pkg/server/tls/authority/authority.go`
- `pkg/issuer/acme/dns/rfc2136/provider.go`
**grafana/grafana:**
- `pkg/services/star/api/client.go`
- `pkg/api/short_url.go`
**open-telemetry/opentelemetry-operator:**
- `main.go`
- `cmd/otel-allocator/main.go`

</details>

### 11. OBS_TC001

**Source:** `prometheus/prometheus` / `storage/interface.go`
**Change type:** interface_modification
**Change:** Add `SelectSorted(ctx context.Context, hints *SelectHints, matchers ...*labels.Matcher) SeriesSet` method to Querier interface
**Repos involved:** 2 | **Affected files:** 8

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `querier.go`, `queryable.go`, `multitsdb.go` | Thanos query layer implements storage.Querier with Select/LabelValues/LabelNames/Close. Rules queryable and receive multitsdb wrap storage.Querier |
| mimir | `querier.go`, `blocks_store_queryable.go`, `distributor_queryable.go`, `error_translate_queryable.go`, `lazyquery.go` | Mimir implements storage.Querier in multiQuerier, blocksStoreQuerier, distributorQuerier, errorTranslateQuerier, and LazyQuerier |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/query/querier.go`
- `pkg/rules/queryable.go`
- `pkg/receive/multitsdb.go`
**grafana/mimir:**
- `pkg/querier/querier.go`
- `pkg/querier/blocks_store_queryable.go`
- `pkg/querier/distributor_queryable.go`
- `pkg/querier/error_translate_queryable.go`
- `pkg/storage/lazyquery/lazyquery.go`

</details>

### 12. OBS_TC002

**Source:** `prometheus/prometheus` / `model/labels/labels_common.go`
**Change type:** type_change
**Change:** Change `type Labels []Label` to `type Labels struct { data []Label }` with accessor methods
**Repos involved:** 3 | **Affected files:** 11

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `lazy_postings.go`, `label.go`, `compact.go`, `multitsdb.go` | Uses labels.FromMap, constructs labels.Label{}/Labels{}, uses labels.FromStrings for tenant labels |
| mimir | `split_merge_grouper.go`, `job.go`, `bucket_compactor.go` | Uses labels.FromMap for block external labels, label matching, and block upload logging |
| loki | `compat.go`, `compat.go`, `api.go` | Uses labels.FromMap for rule label conversion, constructs labels.Labels{}/Label{} structs |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/store/lazy_postings.go`
- `pkg/store/labelpb/label.go`
- `pkg/compact/compact.go`
- `pkg/receive/multitsdb.go`
**grafana/mimir:**
- `pkg/compactor/split_merge_grouper.go`
- `pkg/compactor/job.go`
- `pkg/compactor/bucket_compactor.go`
**grafana/loki:**
- `pkg/ruler/rulespb/compat.go`
- `pkg/ruler/compat.go`
- `pkg/ruler/base/api.go`

</details>

### 13. OBS_TC003

**Source:** `prometheus/prometheus` / `model/histogram/histogram.go`
**Change type:** struct_field_change
**Change:** Add `CreatedTimestamp int64` field to Histogram struct
**Repos involved:** 2 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `samples.go`, `write_request.go` | Constructs &histogram.Histogram{} and &histogram.FloatHistogram{} struct literals when converting protobuf/Cap'n Proto samples |
| mimir | `compat.go`, `batch.go`, `merge.go`, `prometheus_chunk.go`, `tsdb.go` | Constructs histogram structs for format conversion, batch querying, chunk decoding, and zero histogram sentinel values |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/storepb/prompb/samples.go`
- `pkg/receive/writecapnp/write_request.go`
**grafana/mimir:**
- `pkg/mimirpb/compat.go`
- `pkg/querier/batch/batch.go`
- `pkg/querier/batch/merge.go`
- `pkg/storage/chunk/prometheus_chunk.go`
- `pkg/blockbuilder/tsdb.go`

</details>

### 14. OBS_TC004

**Source:** `prometheus/prometheus` / `tsdb/db.go`
**Change type:** method_signature_change
**Change:** Add `ctx context.Context` as first parameter to `DB.Querier(mint, maxt int64)` method
**Repos involved:** 2 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `multitsdb.go` | Directly calls a.db.Querier(mint, maxt) on a tsdb.DB instance to create queriers for local TSDB reads |
| mimir | `ingester.go`, `user_tsdb.go` | Calls db.Querier() for querying local TSDB data and exposes the underlying TSDB querier |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/receive/multitsdb.go`
**grafana/mimir:**
- `pkg/ingester/ingester.go`
- `pkg/ingester/user_tsdb.go`

</details>

### 15. OBS_TC005

**Source:** `prometheus/prometheus` / `promql/engine.go`
**Change type:** interface_modification
**Change:** Add `ExplainQuery(ctx context.Context, qs string) (*QueryPlan, error)` method to QueryEngine
**Repos involved:** 2 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `remote_engine.go`, `engine.go` | Implements QueryEngine interface methods for distributed query execution and wraps promql.Engine |
| mimir | `querier.go`, `fallback_engine.go`, `querysharding.go`, `spin_off_subqueries.go` | Creates/wraps promql.QueryEngine instances for query execution, fallback, sharding, and subquery handling |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/query/remote_engine.go`
- `pkg/api/query/engine.go`
**grafana/mimir:**
- `pkg/querier/querier.go`
- `pkg/streamingpromql/compat/fallback_engine.go`
- `pkg/frontend/querymiddleware/querysharding.go`
- `pkg/frontend/querymiddleware/spin_off_subqueries.go`

</details>

### 16. OBS_TC006

**Source:** `prometheus/prometheus` / `storage/interface_append.go`
**Change type:** interface_modification
**Change:** Add `AppendCTZeroSample(ref SeriesRef, l labels.Labels, t, ct int64) (SeriesRef, error)` to Appender interface
**Repos involved:** 3 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `writer.go`, `multitsdb.go` | ReceiveAppender embeds storage.Appender. ReadyStorage.Appender() returns storage.Appender instances |
| mimir | `compat.go`, `ingester.go`, `user_tsdb.go` | PusherAppender/NoopAppender satisfy storage.Appender. extendedAppender embeds storage.Appender |
| opentelemetry-collector-contrib | `transaction.go`, `appendable.go` | Prometheus receiver implements full storage.Appender interface for converting scraped metrics to OTLP |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/receive/writer.go`
- `pkg/receive/multitsdb.go`
**grafana/mimir:**
- `pkg/ruler/compat.go`
- `pkg/ingester/ingester.go`
- `pkg/ingester/user_tsdb.go`
**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/prometheusreceiver/internal/transaction.go`
- `receiver/prometheusreceiver/internal/appendable.go`

</details>

### 17. OBS_TC007

**Source:** `prometheus/prometheus` / `config/config.go`
**Change type:** struct_field_change
**Change:** Change `ScrapeInterval model.Duration` to `ScrapeInterval ValidatedDuration` in GlobalConfig
**Repos involved:** 1 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `rule.go` | Constructs a config.GlobalConfig{} struct literal when configuring remote storage for the ruler component |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `cmd/thanos/rule.go`

</details>

### 18. OBS_TC008

**Source:** `prometheus/prometheus` / `model/labels/matcher.go`
**Change type:** type_change
**Change:** Change `Matches(v string) bool` to `Matches(v string) (bool, error)` on Matcher
**Repos involved:** 3 | **Affected files:** 14

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `prometheus.go`, `local.go`, `proxy.go`, `rules.go` | Calls m.Matches() in multiple locations for series filtering, external label matching, and rule label filtering |
| mimir | `bucket.go`, `series_refs.go`, `bucket_index_postings.go`, `matchers.go`, `tenant_federation.go` | Calls m.Matches() for block label filtering, series filtering, postings evaluation, active series matching, and tenant ID filtering |
| loki | `instance.go`, `tailer.go`, `index.go`, `querier.go` | Calls filter.Matches()/matcher.Matches()/m.Matches() for stream label filtering, tail queries, inverted index lookups, and postings-based series filtering |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/store/prometheus.go`
- `pkg/store/local.go`
- `pkg/store/proxy.go`
- `pkg/rules/rules.go`
**grafana/mimir:**
- `pkg/storegateway/bucket.go`
- `pkg/storegateway/series_refs.go`
- `pkg/storegateway/bucket_index_postings.go`
- `pkg/ingester/activeseries/model/matchers.go`
- `pkg/querier/tenantfederation/tenant_federation.go`
**grafana/loki:**
- `pkg/ingester/instance.go`
- `pkg/ingester/tailer.go`
- `pkg/ingester/index/index.go`
- `pkg/storage/stores/shipper/indexshipper/tsdb/querier.go`

</details>

### 19. OBS_TC009

**Source:** `prometheus/prometheus` / `discovery/discovery.go`
**Change type:** interface_modification
**Change:** Add `HealthCheck(ctx context.Context) error` method to Discoverer interface
**Repos involved:** 1 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `endpointset.go`, `http.go` | Creates file.NewDiscovery instances (implementing discovery.Discoverer) and calls Run() for store endpoint and HTTP service discovery |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `cmd/thanos/endpointset.go`
- `pkg/clientconfig/http.go`

</details>

### 20. OBS_TC010

**Source:** `prometheus/prometheus` / `tsdb/compact.go`
**Change type:** interface_modification
**Change:** Add `CompactWithTombstones(ctx context.Context, blocks []BlockMeta, tombstones Tombstones) (ulid.ULID, error)` to Compactor interface
**Repos involved:** 2 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `compact.go` | Defines the Compactor interface with Compact and CompactWithBlockPopulator methods |
| mimir | `compactor.go`, `split_merge_compactor.go`, `bucket_compactor.go` | Defines its own Compactor interface mirroring Prometheus TSDB Compactor. Uses Compactor via factory pattern |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/compact/compact.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
- `pkg/compactor/bucket_compactor.go`

</details>

### 21. OBS_TC011

**Source:** `open-telemetry/opentelemetry-collector` / `component/component.go`
**Change type:** interface_modification
**Change:** Add `Capabilities() ComponentCapabilities` method to Component interface
**Repos involved:** 3 | **Affected files:** 8

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `prometheus.go`, `factory.go`, `trace_receiver.go`, `factory.go` | Every exporter and receiver in otel-contrib implements the Component interface |
| jaeger | `extension.go`, `exporter.go` | Jaeger v2 storage extension and exporter implement Component |
| tempo | `shim.go`, `forwarder.go` | Tempo's receiver shim and forwarder implement component.Host and manage OTel receiver/processor/exporter lifecycle |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/prometheus.go`
- `exporter/prometheusexporter/factory.go`
- `receiver/jaegerreceiver/trace_receiver.go`
- `receiver/jaegerreceiver/factory.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
- `cmd/jaeger/internal/exporters/storageexporter/exporter.go`
**grafana/tempo:**
- `modules/distributor/receiver/shim.go`
- `modules/distributor/forwarder/forwarder.go`

</details>

### 22. OBS_TC012

**Source:** `open-telemetry/opentelemetry-collector` / `consumer/metrics.go`
**Change type:** interface_modification
**Change:** Add `ConsumeMetricsWithContext` method to Metrics consumer interface
**Repos involved:** 1 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `prometheus.go`, `collector.go` | Prometheus exporter implements ConsumeMetrics which feeds metrics to the collector |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/prometheus.go`
- `exporter/prometheusexporter/collector.go`

</details>

### 23. OBS_TC013

**Source:** `open-telemetry/opentelemetry-collector` / `exporter/exporter.go`
**Change type:** struct_field_change
**Change:** Add `RetryConfig RetrySettings` field to exporter.Settings struct
**Repos involved:** 2 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `factory.go`, `prometheus.go` | Prometheus exporter factory creates exporter using Settings |
| jaeger | `factory.go` | Jaeger storage exporter factory receives exporter.Settings in createTracesExporter |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/factory.go`
- `exporter/prometheusexporter/prometheus.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/exporters/storageexporter/factory.go`

</details>

### 24. OBS_TC014

**Source:** `open-telemetry/opentelemetry-collector` / `receiver/receiver.go`
**Change type:** method_signature_change
**Change:** Add `logger *zap.Logger` parameter to CreateTraces factory function signature
**Repos involved:** 2 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `factory.go`, `trace_receiver.go` | Jaeger receiver factory implements CreateTraces and must add the logger parameter |
| jaeger | `trace_writer.go` | Calls factory.CreateTraces(context.Background(), set, cfg) and would break when signature changes |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/factory.go`
- `receiver/jaegerreceiver/trace_receiver.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/integration/trace_writer.go`

</details>

### 25. OBS_TC015

**Source:** `open-telemetry/opentelemetry-collector` / `component/config.go`
**Change type:** interface_modification
**Change:** Replace `Validate() error` with `ValidateWithContext(ctx context.Context) error` on Config interface
**Repos involved:** 3 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `config.go`, `config.go` | Every contrib component config implements Validate() and must migrate |
| jaeger | `config.go`, `config.go` | Both config files implement Validate() on component.Config types |
| tempo | `config.go`, `config.go` | Tempo module configs implement Validate() |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/config.go`
- `receiver/jaegerreceiver/config.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/config.go`
- `cmd/jaeger/internal/extension/jaegerquery/config.go`
**grafana/tempo:**
- `modules/distributor/config.go`
- `modules/generator/config.go`

</details>

### 26. OBS_TC016

**Source:** `open-telemetry/opentelemetry-collector` / `component/identifiable.go`
**Change type:** type_change
**Change:** Change `type ID struct { typeVal Type; nameVal string }` to opaque type with constructors only
**Repos involved:** 2 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `factory.go`, `factory.go` | Every contrib factory constructs component.ID for registration |
| jaeger | `extension.go`, `factory.go`, `factory.go`, `factory.go` | Constructs component.ID via component.NewID() and component.MustNewType(). Accesses component.ID fields |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/factory.go`
- `receiver/jaegerreceiver/factory.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
- `cmd/jaeger/internal/extension/jaegerstorage/factory.go`
- `cmd/jaeger/internal/exporters/storageexporter/factory.go`
- `cmd/jaeger/internal/extension/jaegerquery/factory.go`

</details>

### 27. OBS_TC017

**Source:** `open-telemetry/opentelemetry-collector` / `consumer/consumererror/error.go`
**Change type:** type_change
**Change:** Change consumererror to struct with `FailedData interface{}` field instead of simple error wrapper
**Repos involved:** 1 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `exporter.go`, `zipkin.go`, `trace_receiver.go` | Uses consumererror.NewPermanent() and consumererror.IsPermanent() |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusremotewriteexporter/exporter.go`
- `exporter/zipkinexporter/zipkin.go`
- `receiver/zipkinreceiver/trace_receiver.go`

</details>

### 28. OBS_TC018

**Source:** `open-telemetry/opentelemetry-collector` / `component/host.go`
**Change type:** interface_modification
**Change:** Add `GetExtension(id ID) (Component, bool)` method to Host interface
**Repos involved:** 2 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `trace_receiver.go` | Jaeger receiver accesses Host to look up authentication extensions during initialization |
| jaeger | `extension.go`, `extension.go`, `extension.go` | All three extension files call host.GetExtensions() to look up other extensions |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/trace_receiver.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
- `cmd/jaeger/internal/extension/jaegerquery/extension.go`
- `cmd/jaeger/internal/extension/remotesampling/extension.go`

</details>

### 29. OBS_TC019

**Source:** `thanos-io/thanos` / `pkg/store/bucket.go`
**Change type:** interface_modification
**Change:** Add `SyncWithCallback(ctx context.Context, cb func(meta *metadata.Meta)) error` to BucketStore
**Repos involved:** 1 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `bucket_stores.go`, `bucket.go` | Multi-tenant wrapper of Thanos BucketStore and forked BucketStore struct |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/storegateway/bucket_stores.go`
- `pkg/storegateway/bucket.go`

</details>

### 30. OBS_TC020

**Source:** `thanos-io/thanos` / `pkg/compact/compact.go`
**Change type:** interface_modification
**Change:** Add `CompactWithDeletionMarkers(ctx context.Context, markers []DeletionMark) error` to Syncer
**Repos involved:** 1 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `compactor.go`, `bucket_compactor.go`, `syncer_metrics.go` | Creates/uses metaSyncer, defines metaSyncer struct, and tracks Syncer metrics |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/bucket_compactor.go`
- `pkg/compactor/syncer_metrics.go`

</details>

### 31. OBS_TC021 (Internal Only)

**Source:** `thanos-io/thanos` / `pkg/query/querier.go`
**Change type:** method_signature_change
**Change:** Add `skipChunks bool` parameter to QueryableCreator function signature
**Repos involved:** 1 | **Affected files:** 3
**Note:** QueryableCreator is thanos-internal only. No downstream repos import this type.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `v1.go`, `grpc.go`, `query.go` | Internal files that use QueryableCreator type and call NewQueryableCreator |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/api/query/v1.go`
- `pkg/api/query/grpc.go`
- `cmd/thanos/query.go`

</details>

### 32. OBS_TC022

**Source:** `thanos-io/thanos` / `pkg/compact/planner.go`
**Change type:** interface_modification
**Change:** Add `PlanWithFilter` method to Planner interface
**Repos involved:** 1 | **Affected files:** 4
**Note:** Mimir forked the Thanos Planner interface (not a Go module import).

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `compactor.go`, `split_merge_compactor.go`, `bucket_compactor.go`, `split_merge_planner.go` | Defines forked Planner interface and implementations |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
- `pkg/compactor/bucket_compactor.go`
- `pkg/compactor/split_merge_planner.go`

</details>

### 33. OBS_TC023 (Internal Only)

**Source:** `grafana/grafana` / `pkg/apis/datasource/v0alpha1/types.go`
**Change type:** struct_field_change
**Change:** Add `AuthConfig AuthenticationConfig` field to DataSourceConnection struct
**Repos involved:** 1 | **Affected files:** 3
**Note:** DataSourceConnection is grafana-internal only. No downstream repos reference this type.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| grafana | `connections.go`, `register.go`, `zz_generated.deepcopy.go` | Internal Grafana files that construct or use DataSourceConnection |

<details>
<summary>Full file paths</summary>

**grafana/grafana:**
- `pkg/registry/apis/query/connections.go`
- `pkg/registry/apis/query/register.go`
- `pkg/apis/query/v0alpha1/zz_generated.deepcopy.go`

</details>

### 34. OBS_TC024 (Internal Only)

**Source:** `grafana/grafana` / `pkg/registry/apps/alerting/rules/alertrule/storage.go`
**Change type:** interface_modification
**Change:** Add `ListByDatasource(ctx context.Context, dsUID string) ([]AlertRule, error)` to alert rule storage
**Repos involved:** 1 | **Affected files:** 4
**Note:** AlertRule storage is grafana-internal only. No downstream repos reference this interface.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| grafana | `alert_rule.go`, `database.go`, `api_ruler.go`, `alert_rules.go` | Grafana files that implement and use the AlertRule storage interface |

<details>
<summary>Full file paths</summary>

**grafana/grafana:**
- `pkg/services/ngalert/store/alert_rule.go`
- `pkg/services/ngalert/store/database.go`
- `pkg/services/ngalert/api/api_ruler.go`
- `pkg/services/ngalert/provisioning/alert_rules.go`

</details>

### 35. OBS_TC025 (Internal Only)

**Source:** `grafana/grafana` / `pkg/tsdb/loki/standalone/datasource.go`
**Change type:** method_signature_change
**Change:** Add `stream bool` parameter to QueryData method
**Repos involved:** 1 | **Affected files:** 1
**Note:** This is a grafana-internal plugin with no cross-repo impact. Loki does not implement or depend on Grafana's QueryData method.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| grafana | `datasource.go` | Source file itself; no external impact |

<details>
<summary>Full file paths</summary>

**grafana/grafana:**
- `pkg/tsdb/loki/standalone/datasource.go`

</details>

### 36. OBS_TC026 (Internal Only)

**Source:** `grafana/grafana` / `pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go`
**Change type:** interface_modification
**Change:** Replace `prometheus.Registerer` parameter with `MetricsCollector` interface in middleware constructor
**Repos involved:** 1 | **Affected files:** 2
**Note:** This is a grafana-internal HTTP client middleware. No downstream repos import from grafana's httpclient package.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| grafana | `prometheus_metrics_middleware.go`, `http_client_provider.go` | Internal middleware files |

<details>
<summary>Full file paths</summary>

**grafana/grafana:**
- `pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go`
- `pkg/infra/httpclient/httpclientprovider/http_client_provider.go`

</details>

### 37. OBS_TC027 (Internal Only)

**Source:** `jaegertracing/jaeger` / `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
**Change type:** interface_modification
**Change:** Add `GetArchiveStorage(ctx context.Context) (tracestorage.Reader, tracestorage.Writer, error)` to StorageExtension
**Repos involved:** 1 | **Affected files:** 4
**Note:** StorageExtension is jaeger-internal. No external repos import this interface.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| jaeger | `exporter.go`, `server.go`, `server.go`, `extension.go` | Jaeger components that use jaegerstorage.GetTraceStoreFactory or depend on the Extension interface |

<details>
<summary>Full file paths</summary>

**jaegertracing/jaeger:**
- `cmd/jaeger/internal/exporters/storageexporter/exporter.go`
- `cmd/jaeger/internal/extension/jaegerquery/server.go`
- `cmd/jaeger/internal/extension/remotestorage/server.go`
- `cmd/jaeger/internal/extension/remotesampling/extension.go`

</details>

### 38. OBS_TC028 (Internal Only)

**Source:** `jaegertracing/jaeger` / `cmd/jaeger/internal/exporters/storageexporter/exporter.go`
**Change type:** struct_field_change
**Change:** Add `BatchConfig BatchSettings` field to storageExporter struct
**Repos involved:** 1 | **Affected files:** 2
**Note:** storageExporter is a private (unexported) struct. No external repos can access this type.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| jaeger | `exporter.go`, `factory.go` | Only files within the storageexporter package construct or reference the private struct |

<details>
<summary>Full file paths</summary>

**jaegertracing/jaeger:**
- `cmd/jaeger/internal/exporters/storageexporter/exporter.go`
- `cmd/jaeger/internal/exporters/storageexporter/factory.go`

</details>

### 39. OBS_TC029 (Internal Only)

**Source:** `open-telemetry/opentelemetry-collector-contrib` / `exporter/prometheusexporter/accumulator.go`
**Change type:** interface_modification
**Change:** Change return type of `Accumulate(metrics pmetric.Metrics)` from `int` to `[]AccumulatedMetric`
**Repos involved:** 1 | **Affected files:** 2
**Note:** The accumulator interface is private (unexported), so no external repos can implement it.

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `collector.go`, `accumulator.go` | collector.go calls accumulator.Accumulate() directly. accumulator.go defines the interface |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/collector.go`
- `exporter/prometheusexporter/accumulator.go`

</details>

### 40. OBS_TC030

**Source:** `open-telemetry/opentelemetry-collector-contrib` / `receiver/jaegerreceiver/trace_receiver.go`
**Change type:** struct_field_change
**Change:** Add `SamplingConfig SamplingStrategy` field to jReceiver struct
**Repos involved:** 3 | **Affected files:** 3
**Note:** jReceiver is a private struct but the factory behavior change affects callers via NewFactory().

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `trace_receiver.go` | Source file: jReceiver is defined and constructed here |
| jaeger | `components.go` | Uses jaegerreceiver.NewFactory() to create the receiver |
| tempo | `shim.go` | Imports jaegerreceiver and uses NewFactory(), casts to *jaegerreceiver.Config |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/trace_receiver.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/components.go`
**grafana/tempo:**
- `modules/distributor/receiver/shim.go`

</details>

---

## Detailed Corrections Log

This section documents what was wrong with the original file references and how they were corrected. All corrections were verified by grep-searching the actual source code in the dataset repositories.

### MIXED_TC001
**Files corrected:** 1
- `server/application/application.go` was replaced with `server/server.go` - the server.go file is where `NewSharedInformerFactoryWithOptions` and `WaitForCacheSync` are actually called, not in the application handler.

### MIXED_TC002
**Files corrected:** 8 (7 removed, 5 added)
- Removed 7 files from cert-manager, prometheus, and otel-operator repos that were listed but do **not** use `rest.TLSClientConfig{}` struct literals. These repos only access the Config object, not constructing TLSClientConfig as a struct literal.
- Added `external-secrets/providers/v1/kubernetes/auth.go` and 4 grafana files that actually construct `rest.TLSClientConfig{}` struct literals.

### MIXED_TC003
**Files corrected:** 3
- Replaced 3 wrong opentelemetry-operator files (`podmutator.go`, `opentelemetrycollector_types.go`, `common.go`) with `sdk.go`, `helper.go`, and `pod.go` which actually use `len()`, `range`, and `append()` on `pod.Spec.Containers`.

### MIXED_TC004
**Files corrected:** 5 (2 removed, 3 added)
- Removed `endpoints.go` and `endpointslice.go` from prometheus (they don't access `.Spec.Type`).
- Added ingress-nginx `controller.go` and `status.go`, and external-dns `compatibility.go` which actually compare `svc.Spec.Type`.

### MIXED_TC005
**Files corrected:** 13 (8 removed, 9 added)
- Major overhaul. Removed 8 files that did not call `.Matches()` (only used selectors in other ways). Replaced with verified `.Matches()` callers including `generator_spec_processor.go`, `gateway.go`, `filter.go`, `indexers.go`, and `store.go`.

### MIXED_TC006
**Files corrected:** 4
- Replaced 4 wrong files (otel-operator volume.go files, grafana jaeger/client.go) with files that actually access `secret.Data[key]` as a map: `vault.go`, `dns.go`, `venaficlient.go`, `pushsecret_controller.go`.

### MIXED_TC007
**Files corrected:** 3
- Replaced 3 CRD type definition files (which just declare struct types) with files that actually access `.Labels[key]` as a map: `externalsecret_controller.go`, `webhookconfig.go`, `collector/service.go`.

### MIXED_TC008
**Files corrected:** 1
- `folders.go` was replaced with `retry_client.go` - retry_client.go actually wraps `dynamic.ResourceInterface` and calls `r.client.List(ctx, opts)`.

### MIXED_TC009
**Files corrected:** 1
- `factory.go` (from cert-manager startup API check) was replaced with `certmanager/v1/register.go` which actually calls `scheme.AddKnownTypes()`.

### MIXED_TC010
**Files corrected:** 8
- Replaced 8 wrong files with verified `kubernetes.NewForConfig()` callers. The original files referenced general config usage, not actual Clientset construction.

### OBS_TC001
**Files corrected:** 9 (4 removed, 8 added)
- Replaced `bucket.go`, `iter.go`, `compactor.go`, `bucketindex.go` (none of which implement `storage.Querier`) with actual Querier implementations: `querier.go`, `queryable.go`, `multitsdb.go`, and 5 mimir querier files.

### OBS_TC002
**Files corrected:** all
- Replaced all listed files with actual `labels.FromMap`/`labels.FromStrings` callers. Removed otel-contrib (doesn't use Prometheus labels package).

### OBS_TC003
**Files corrected:** all 4
- Replaced all with verified `histogram.Histogram{}` struct literal constructors: `prompb/samples.go`, `writecapnp`, `mimirpb/compat.go`, etc.

### OBS_TC004
**Files corrected:** all
- Replaced with actual `db.Querier()` callers: `multitsdb.go`, `ingester.go`, `user_tsdb.go`.

### OBS_TC005
**Files corrected:** all
- Replaced with QueryEngine users. Removed grafana (doesn't use `promql.Engine` directly).

### OBS_TC006
**Files corrected:** all
- Replaced with actual `storage.Appender` implementations: `writer.go`, `multitsdb.go`, `compat.go`, `transaction.go`, `appendable.go`.

### OBS_TC007
**Files corrected:** 3 repos removed
- Only `thanos/cmd/thanos/rule.go` actually constructs `config.GlobalConfig{}`. Removed mimir and grafana entries (they don't construct this struct literal).

### OBS_TC008
**Files corrected:** all
- Replaced with 14 verified `Matcher.Matches()` callers across thanos/mimir/loki.

### OBS_TC009
**Files corrected:** 1
- Replaced `endpointset.go` (wrong path) with `cmd/thanos/endpointset.go` and added `clientconfig/http.go`.

### OBS_TC010
**Files corrected:** 1
- Removed `planner.go` (implements Planner, not Compactor).

### OBS_TC011
**Files corrected:** 2
- Replaced tempo `main.go` with `shim.go` and `forwarder.go` (actual component.Host implementors).

### OBS_TC012
**Files corrected:** 1
- Removed jaeger entry entirely (no ConsumeMetrics usage in jaeger).

### OBS_TC013
**Files corrected:** 1
- Replaced jaeger `exporter.go` with `factory.go` (where exporter.Settings is actually received).

### OBS_TC014
**Files corrected:** 1
- Replaced jaeger `command.go` with `trace_writer.go` (which actually calls factory.CreateTraces).

### OBS_TC015
**Files corrected:** 3
- Replaced `extension.go` files with `config.go` files (where Validate() is implemented). Replaced tempo `main.go` with `distributor/config.go` and `generator/config.go`.

### OBS_TC016
**Files corrected:** 2
- Replaced `command.go` references with actual factory files that construct component.ID.

### OBS_TC017
**Files corrected:** ALL (completely wrong)
- All originally listed files were wrong. Replaced with `prometheusremotewriteexporter/exporter.go`, `zipkinexporter/zipkin.go`, and `zipkinreceiver/trace_receiver.go`.

### OBS_TC018
**Files corrected:** 2
- Replaced `config.go` references with `extension.go` files (where host.GetExtensions() is called).

### OBS_TC019
**Files corrected:** all (removed loki, replaced with mimir storegateway files)
- Removed loki entries (non-existent file paths). Replaced with correct mimir storegateway files.

### OBS_TC020
**Files corrected:** 2
- Replaced `split_merge_compactor.go` and `job.go` with `bucket_compactor.go` and `syncer_metrics.go`.

### OBS_TC021
**Premise corrected:** QueryableCreator is thanos-internal only
- Original claimed cross-repo impact on grafana and mimir. Corrected to show only thanos-internal files. No downstream repos import this type.

### OBS_TC022
**Files corrected:** 1
- Replaced `split_merge_job.go` with `bucket_compactor.go` and added `split_merge_planner.go`.

### OBS_TC023
**Premise corrected:** DataSourceConnection is grafana-internal only
- Original claimed impact on loki, tempo, mimir. Corrected to show only grafana-internal files.

### OBS_TC024
**Premise corrected:** AlertRule storage is grafana-internal only
- Original claimed impact on mimir and loki rulers. Corrected to show only grafana-internal files.

### OBS_TC025
**Premise corrected:** Grafana QueryData is grafana-internal only
- Original claimed Loki depends on this method. Corrected: Loki does not implement or depend on Grafana's QueryData.

### OBS_TC026
**Premise corrected:** prometheus_metrics_middleware is grafana-internal only
- Original claimed impact on prometheus, thanos, mimir. Corrected: no downstream repos import from grafana's httpclient package.

### OBS_TC027
**Premise corrected:** StorageExtension is jaeger-internal only
- Original claimed impact on otel-contrib and tempo. Corrected: StorageExtension is only used within jaeger's internal packages.

### OBS_TC028
**Premise corrected:** storageExporter is private struct
- Original claimed cross-repo impact. Corrected: storageExporter is unexported (lowercase) and only accessible within the storageexporter package.

### OBS_TC029
**Scope corrected:** accumulator interface is private
- Original claimed impact on jaeger and grafana. Corrected: only otel-contrib `collector.go` and `accumulator.go` are affected.

### OBS_TC030
**Files corrected:** 3
- Corrected to `trace_receiver.go` (source), `components.go` (jaeger), and `shim.go` (tempo).

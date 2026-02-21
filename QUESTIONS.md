# Questions Reference

Complete catalog of all 100 cross-repository impact analysis test cases.

## Summary

- **Total test cases:** 100
- **Distribution:** 23 two-repo, 40 three-repo, 37 four-plus-repo
- **Repos covered:** 25

### Categories

| Prefix | Description | Count |
|--------|-------------|-------|
| CRW | Cross-repo workflow | 41 |
| OBS | Observability stack | 30 |
| KM | Kubernetes mechanics | 14 |
| MIXED | Kubernetes + Observability cross-stack | 10 |
| SA | Shared API / client-go | 3 |
| NK | Networking / Kustomize | 2 |

## All Questions

| # | ID | Source Repo | Source File | Change Type | Affected Repos | Files |
|---|-----|------------|------------|-------------|----------------|-------|
| 1 | MIXED_TC001 | kubernetes | `shared_informer.go` | interface modification | 5 | 15 |
| 2 | MIXED_TC002 | kubernetes | `config.go` | struct field change | 6 | 9 |
| 3 | MIXED_TC003 | kubernetes | `types.go` | struct field modification | 5 | 7 |
| 4 | MIXED_TC004 | kubernetes | `types.go` | struct field modification | 6 | 8 |
| 5 | MIXED_TC005 | kubernetes | `selector.go` | interface modification | 6 | 12 |
| 6 | MIXED_TC006 | kubernetes | `types.go` | struct field modification | 6 | 11 |
| 7 | MIXED_TC007 | kubernetes | `types.go` | struct field modification | 7 | 19 |
| 8 | MIXED_TC008 | kubernetes | `interface.go` | interface modification | 4 | 6 |
| 9 | MIXED_TC009 | kubernetes | `scheme.go` | method signature change | 5 | 7 |
| 10 | MIXED_TC010 | kubernetes | `clientset.go` | interface modification | 6 | 9 |
| 11 | SA_TC011 | kustomize | `rnode.go` | method signature change | 2 | 1 |
| 12 | SA_TC012 | helm | `chartfile.go` | function signature change | 2 | 1 |
| 13 | SA_TC013 | kustomize | `types.go` | interface modification | 2 | 1 |
| 14 | NK_TC012 | kustomize | `types.go` | struct field rename | 2 | 1 |
| 15 | NK_TC015 | helm | `chart.go` | struct modification | 2 | 1 |
| 16 | KM_TC001 | kubernetes | `interfaces.go` | interface modification | 3 | 3 |
| 17 | KM_TC002 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 18 | KM_TC003 | kubernetes | `types.go` | struct field modification | 5 | 7 |
| 19 | KM_TC004 | kubernetes | `clientset.go` | interface modification | 4 | 3 |
| 20 | KM_TC006 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 21 | KM_TC007 | kubernetes | `types.go` | struct field modification | 4 | 6 |
| 22 | KM_TC008 | kubernetes | `types.go` | struct field modification | 2 | 2 |
| 23 | KM_TC009 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 24 | KM_TC010 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 25 | KM_TC011 | kubernetes | `event.go` | interface modification | 3 | 3 |
| 26 | KM_TC012 | kubernetes | `types.go` | struct field modification | 3 | 3 |
| 27 | KM_TC013 | kubernetes | `namespacedname.go` | struct modification | 4 | 3 |
| 28 | KM_TC014 | kubernetes | `request.go` | method signature change | 3 | 2 |
| 29 | KM_TC015 | kubernetes | `types.go` | struct field modification | 4 | 4 |
| 30 | CRW_TC001 | kubernetes | `types.go` | struct field modification | 2 | 1 |
| 31 | CRW_TC002 | kubernetes | `event.go` | interface modification | 2 | 1 |
| 32 | CRW_TC003 | kubernetes | `portforward.go` | function signature change | 2 | 1 |
| 33 | CRW_TC004 | kubernetes | `errors.go` | function signature change | 2 | 1 |
| 34 | CRW_TC005 | kubernetes | `selector.go` | method signature change | 2 | 1 |
| 35 | CRW_TC006 | kubernetes | `clientset.go` | function signature change | 2 | 1 |
| 36 | CRW_TC007 | kubernetes | `watch.go` | interface modification | 2 | 1 |
| 37 | CRW_TC008 | kubernetes | `util.go` | function signature change | 2 | 1 |
| 38 | CRW_TC009 | kubernetes | `unstructured.go` | method signature change | 2 | 1 |
| 39 | CRW_TC010 | kubernetes | `config.go` | struct field modification | 2 | 1 |
| 40 | CRW_TC011 | kubernetes | `interface.go` | interface modification | 2 | 1 |
| 41 | CRW_TC012 | kubernetes | `types.go` | struct field modification | 2 | 1 |
| 42 | CRW_TC013 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 43 | CRW_TC014 | kubernetes | `scheme.go` | function signature change | 3 | 2 |
| 44 | CRW_TC015 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 45 | CRW_TC016 | kubernetes | `event.go` | interface modification | 3 | 2 |
| 46 | CRW_TC017 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 47 | CRW_TC018 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 48 | CRW_TC019 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 49 | CRW_TC020 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 50 | CRW_TC021 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 51 | CRW_TC022 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 52 | CRW_TC023 | kubernetes | `group_version.go` | method signature change | 3 | 2 |
| 53 | CRW_TC024 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 54 | CRW_TC025 | kubernetes | `types.go` | struct field modification | 3 | 2 |
| 55 | CRW_TC026 | kubernetes | `selector.go` | method signature change | 3 | 2 |
| 56 | CRW_TC027 | kubernetes | `codec_factory.go` | function signature change | 3 | 2 |
| 57 | CRW_TC028 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 58 | CRW_TC029 | kubernetes | `unstructured.go` | struct field modification | 4 | 3 |
| 59 | CRW_TC030 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 60 | CRW_TC031 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 61 | CRW_TC032 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 62 | CRW_TC033 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 63 | CRW_TC034 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 64 | CRW_TC035 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 65 | CRW_TC036 | kubernetes | `config.go` | struct field modification | 4 | 3 |
| 66 | CRW_TC037 | kubernetes | `selector.go` | method signature change | 4 | 3 |
| 67 | CRW_TC038 | kubernetes | `scheme.go` | method signature change | 4 | 3 |
| 68 | CRW_TC039 | kubernetes | `event.go` | interface modification | 4 | 3 |
| 69 | CRW_TC040 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 70 | CRW_TC041 | kubernetes | `types.go` | struct field modification | 4 | 3 |
| 71 | OBS_TC001 | prometheus | `interface.go` | interface modification | 3 | 5 |
| 72 | OBS_TC002 | prometheus | `labels_common.go` | type change | 5 | 9 |
| 73 | OBS_TC003 | prometheus | `histogram.go` | struct field change | 3 | 4 |
| 74 | OBS_TC004 | prometheus | `db.go` | method signature change | 3 | 4 |
| 75 | OBS_TC005 | prometheus | `engine.go` | interface modification | 4 | 4 |
| 76 | OBS_TC006 | prometheus | `interface_append.go` | interface modification | 4 | 6 |
| 77 | OBS_TC007 | prometheus | `config.go` | struct field change | 4 | 4 |
| 78 | OBS_TC008 | prometheus | `matcher.go` | type change | 4 | 6 |
| 79 | OBS_TC009 | prometheus | `discovery.go` | interface modification | 2 | 1 |
| 80 | OBS_TC010 | prometheus | `compact.go` | interface modification | 3 | 5 |
| 81 | OBS_TC011 | opentelemetry-collector | `component.go` | interface modification | 4 | 7 |
| 82 | OBS_TC012 | opentelemetry-collector | `metrics.go` | interface modification | 3 | 3 |
| 83 | OBS_TC013 | opentelemetry-collector | `exporter.go` | struct field change | 3 | 3 |
| 84 | OBS_TC014 | opentelemetry-collector | `receiver.go` | method signature change | 3 | 3 |
| 85 | OBS_TC015 | opentelemetry-collector | `config.go` | interface modification | 4 | 5 |
| 86 | OBS_TC016 | opentelemetry-collector | `identifiable.go` | type change | 3 | 4 |
| 87 | OBS_TC017 | opentelemetry-collector | `error.go` | type change | 3 | 3 |
| 88 | OBS_TC018 | opentelemetry-collector | `host.go` | interface modification | 3 | 3 |
| 89 | OBS_TC019 | thanos | `bucket.go` | interface modification | 3 | 4 |
| 90 | OBS_TC020 | thanos | `compact.go` | interface modification | 2 | 3 |
| 91 | OBS_TC021 | thanos | `querier.go` | method signature change | 3 | 2 |
| 92 | OBS_TC022 | thanos | `planner.go` | interface modification | 2 | 3 |
| 93 | OBS_TC023 | grafana | `types.go` | struct field change | 3 | 2 |
| 94 | OBS_TC024 | grafana | `storage.go` | interface modification | 3 | 4 |
| 95 | OBS_TC025 | grafana | `datasource.go` | method signature change | 2 | 2 |
| 96 | OBS_TC026 | grafana | `prometheus_metrics_middleware.go` | interface modification | 3 | 2 |
| 97 | OBS_TC027 | jaeger | `extension.go` | interface modification | 3 | 4 |
| 98 | OBS_TC028 | jaeger | `exporter.go` | struct field change | 2 | 2 |
| 99 | OBS_TC029 | opentelemetry-collector-contrib | `accumulator.go` | interface modification | 3 | 4 |
| 100 | OBS_TC030 | opentelemetry-collector-contrib | `trace_receiver.go` | struct field change | 3 | 4 |

## Detailed Questions

### 1. MIXED_TC001

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/cache/shared_informer.go`
**Change type:** interface_modification
**Change:** Add `WaitForCacheSync(ctx context.Context) bool` method to SharedInformer interface
**Repos involved:** 5 | **Affected files:** 15

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `appcontroller.go`, `cache.go`, `application.go` | ArgoCD controllers use SharedInformer for watching Application CRDs, Secrets, and cluster resources |
| cert-manager | `issuing_controller.go`, `trigger_controller.go`, `core_filteredsecrets.go`, `factory.go` | Cert-manager controllers use SharedInformer for watching Certificates, CertificateRequests, and Secrets |
| prometheus | `kubernetes.go`, `pod.go`, `service.go`, `node.go`, `endpoints.go`, `endpointslice.go` | Prometheus Kubernetes service discovery uses SharedInformer to watch Pods, Services, Nodes, Endpoints, and EndpointSlice |
| opentelemetry-operator | `promOperator.go`, `collector.go` | OpenTelemetry Operator target allocator uses SharedInformer for watching collectors and Prometheus operator CRDs |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `controller/appcontroller.go`
- `controller/cache/cache.go`
- `server/application/application.go`
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
**Repos involved:** 6 | **Affected files:** 9

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `types.go` | ArgoCD directly assigns rest.TLSClientConfig struct literals for multi-cluster TLS configuration |
| ingress-nginx | `main.go` | Ingress-nginx creates rest.TLSClientConfig{} and assigns CAFile before setting cfg.TLSClientConfig |
| cert-manager | `controller.go`, `controller.go`, `factory.go` | Cert-manager controllers construct rest.Config with TLSClientConfig for API server communication |
| prometheus | `kubernetes.go` | Prometheus Kubernetes discovery creates rest.Config for connecting to the Kubernetes API server for target discovery |
| opentelemetry-operator | `config.go`, `config.go`, `main.go` | OpenTelemetry Operator uses rest.Config for target allocator, OpAMP bridge, and platform autodetection |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `pkg/apis/application/v1alpha1/types.go`
**kubernetes/ingress-nginx:**
- `cmd/nginx/main.go`
**cert-manager/cert-manager:**
- `cmd/cainjector/app/controller.go`
- `cmd/controller/app/controller.go`
- `cmd/startupapicheck/pkg/factory/factory.go`
**prometheus/prometheus:**
- `discovery/kubernetes/kubernetes.go`
**open-telemetry/opentelemetry-operator:**
- `cmd/otel-allocator/internal/config/config.go`
- `cmd/operator-opamp-bridge/internal/config/config.go`
- `internal/autodetect/main.go`

</details>

### 3. MIXED_TC003

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Containers []Container` to `Containers ContainerList` where ContainerList is a new named type
**Repos involved:** 5 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `info.go`, `terminal.go` | ArgoCD accesses pod.Spec.Containers using len() and range for pod info extraction and terminal exec |
| cert-manager | `pod.go` | Cert-manager constructs Containers: []corev1.Container{} and accesses pod.Spec.Containers[0] for ACME HTTP-01 challenge  |
| prometheus | `pod.go` | Prometheus Kubernetes discovery iterates pod.Spec.Containers to extract container names, ports, and image info for scrap |
| opentelemetry-operator | `podmutator.go`, `opentelemetrycollector_types.go`, `common.go` | OpenTelemetry Operator mutates pod containers for auto-instrumentation injection and defines collector container specs i |

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
- `internal/instrumentation/podmutator.go`
- `apis/v1beta1/opentelemetrycollector_types.go`
- `apis/v1beta1/common.go`

</details>

### 4. MIXED_TC004

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Type ServiceType` to `Type *ServiceType` (value to pointer) in ServiceSpec
**Repos involved:** 6 | **Affected files:** 8

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `ready.go` | Helm checks Service.Spec.Type for LoadBalancer readiness evaluation |
| argo-cd | `health_service.go` | ArgoCD checks Service.Spec.Type for health status and load balancer ingress status |
| ingress-nginx | `store.go`, `endpointslices.go` | Ingress-nginx accesses Service.Spec.Type for backend routing and endpoint resolution |
| external-dns | `service.go` | External-DNS reads Service.Spec.Type to determine DNS endpoint generation for LoadBalancer/NodePort services |
| prometheus | `service.go`, `endpoints.go`, `endpointslice.go` | Prometheus Kubernetes discovery reads Service objects and their types for service-level target discovery and endpoint as |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/ready.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/health/health_service.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`
- `internal/ingress/controller/endpointslices.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`
**prometheus/prometheus:**
- `discovery/kubernetes/service.go`
- `discovery/kubernetes/endpoints.go`
- `discovery/kubernetes/endpointslice.go`

</details>

### 5. MIXED_TC005

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/labels/selector.go`
**Change type:** interface_modification
**Change:** Change `Matches(labels Labels) bool` to `Matches(ctx context.Context, labels Labels) bool` in Selector interface
**Repos involved:** 6 | **Affected files:** 12

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `secrets.go`, `cfgmaps.go`, `list.go` | Helm uses labels.Selector for filtering Secrets/ConfigMaps in storage drivers and listing releases |
| argo-cd | `appcontroller.go`, `application.go`, `selector.go` | ArgoCD uses labels.Selector for filtering Applications and ApplicationSets |
| external-dns | `source.go`, `service.go`, `ingress.go` | External-DNS uses labels.Selector for filtering source resources across all source types |
| prometheus | `kubernetes.go` | Prometheus Kubernetes discovery uses labels.Selector for filtering discoverable resources by namespace and label selecto |
| opentelemetry-operator | `cluster.go`, `opentelemetrycollector_controller.go` | OpenTelemetry Operator uses labels.Selector for collector pod selection and cluster resource gathering |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/storage/driver/secrets.go`
- `pkg/storage/driver/cfgmaps.go`
- `pkg/action/list.go`
**argoproj/argo-cd:**
- `controller/appcontroller.go`
- `server/application/application.go`
- `applicationset/utils/selector.go`
**kubernetes-sigs/external-dns:**
- `source/source.go`
- `source/service.go`
- `source/ingress.go`
**prometheus/prometheus:**
- `discovery/kubernetes/kubernetes.go`
**open-telemetry/opentelemetry-operator:**
- `cmd/gather/cluster/cluster.go`
- `internal/controllers/opentelemetrycollector_controller.go`

</details>

### 6. MIXED_TC006

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Data map[string][]byte` to `Data SecretData` where SecretData requires different accessor methods
**Repos involved:** 6 | **Affected files:** 11

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `secrets.go` | Helm stores release data in Secret.Data map, encoding release metadata as base64 byte values |
| argo-cd | `secrets.go`, `repository_secrets.go`, `cluster.go`, `settings.go` | ArgoCD stores cluster credentials, repository credentials, and settings in Secret.Data fields |
| cert-manager | `secret.go`, `sources.go` | Cert-manager reads/writes TLS certificates and keys to Secret.Data fields |
| opentelemetry-operator | `exporter.go`, `volume.go`, `volume.go` | OpenTelemetry Operator reads Secret.Data for collector configuration, instrumentation exporter secrets, and target alloc |
| grafana | `client.go` | Grafana reads Secret.Data for Jaeger datasource client credentials configuration |

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
**open-telemetry/opentelemetry-operator:**
- `internal/instrumentation/exporter.go`
- `internal/manifests/targetallocator/volume.go`
- `internal/manifests/collector/volume.go`
**grafana/grafana:**
- `pkg/tsdb/jaeger/client.go`

</details>

### 7. MIXED_TC007

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Labels map[string]string` to `Labels LabelMap` in ObjectMeta where LabelMap requires accessor methods
**Repos involved:** 7 | **Affected files:** 19

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `appcontroller.go`, `settings.go` | ArgoCD directly accesses ObjectMeta.Labels map for application and settings resource labeling |
| cert-manager | `pod.go`, `service.go`, `ingress.go` | Cert-manager constructs ObjectMeta with Labels map literals for ACME challenge resources |
| external-secrets | `secretstore_types.go`, `clusterexternalsecret_types.go` | External-secrets CRD types embed ObjectMeta and use Labels for store and secret selection |
| prometheus | `kubernetes.go`, `pod.go`, `node.go`, `service.go` | Prometheus Kubernetes discovery reads ObjectMeta.Labels to construct __meta_kubernetes_*_label_* target labels for all d |
| loki | `config.go`, `distributor.go`, `compactor.go`, `gateway.go` | Loki Operator constructs Kubernetes resources with ObjectMeta.Labels for all Loki components (distributor, compactor, ga |
| opentelemetry-operator | `opentelemetrycollector_types.go`, `instrumentation_types.go`, `opampbridge_types.go`, `mutate.go` | OpenTelemetry Operator CRD types embed ObjectMeta and use Labels for collector, instrumentation, and OpAMP bridge resour |

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
- `apis/externalsecrets/v1/secretstore_types.go`
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
- `apis/v1alpha1/instrumentation_types.go`
- `apis/v1alpha1/opampbridge_types.go`
- `internal/manifests/mutate.go`

</details>

### 8. MIXED_TC008

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/dynamic/interface.go`
**Change type:** interface_modification
**Change:** Change `List(ctx context.Context, opts metav1.ListOptions) (*unstructured.UnstructuredList, error)` to return `(PaginatedList, error)`
**Repos involved:** 4 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `lookup_func.go` | Helm template engine uses dynamic client to look up arbitrary K8s resources during chart rendering |
| argo-cd | `sync_context.go`, `cluster.go`, `controller.go` | ArgoCD gitops-engine calls dynamic.ResourceInterface.List() for cache population, sync operations, and notification cont |
| grafana | `client.go`, `folders.go` | Grafana provisioning system uses dynamic client for listing and managing provisioned Kubernetes resources and folders |

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
- `pkg/registry/apis/provisioning/resources/folders.go`

</details>

### 9. MIXED_TC009

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/scheme.go`
**Change type:** method_signature_change
**Change:** Change `func (s *Scheme) AddKnownTypes(gv schema.GroupVersion, types ...Object)` to require `TypeRegistration` struct
**Repos involved:** 5 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cert-manager | `factory.go` | Cert-manager registers certificate and issuer types with runtime.Scheme for informer factories |
| external-secrets | `register.go` | External-secrets registers SecretStore, ExternalSecret, and ClusterExternalSecret CRD types with runtime.Scheme |
| grafana | `zz_generated.defaults.go`, `register.go`, `register.go` | Grafana registers alerting enrichment, provisioning, and datasource API types with runtime.Scheme |
| opentelemetry-operator | `groupversion_info.go`, `groupversion_info.go` | OpenTelemetry Operator registers OpenTelemetryCollector, Instrumentation, and OpAMPBridge CRD types with runtime.Scheme |

<details>
<summary>Full file paths</summary>

**cert-manager/cert-manager:**
- `pkg/client/informers/externalversions/factory.go`
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
**Change:** Add `HealthCheck(ctx context.Context) error` method to kubernetes.Interface
**Repos involved:** 6 | **Affected files:** 9

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `helm.go` | Helm creates kubernetes.Clientset via kubernetes.NewForConfig for API server communication in all chart operations |
| argo-cd | `argocd_server.go` | ArgoCD server creates kubernetes.Clientset for API server communication and cluster management |
| cert-manager | `controller.go`, `controller.go` | Cert-manager controllers create kubernetes.Clientset for certificate operations and CA injection |
| grafana | `register.go`, `register.go` | Grafana generates and uses typed clientsets for provisioning and service API access |
| opentelemetry-operator | `config.go`, `config.go`, `metrics.go` | OpenTelemetry Operator creates kubernetes.Clientset for allocator config, OpAMP bridge, and operator metrics |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `cmd/helm/helm.go`
**argoproj/argo-cd:**
- `cmd/argocd-server/commands/argocd_server.go`
**cert-manager/cert-manager:**
- `cmd/cainjector/app/controller.go`
- `cmd/controller/app/controller.go`
**grafana/grafana:**
- `apps/provisioning/pkg/generated/clientset/versioned/scheme/register.go`
- `pkg/generated/clientset/versioned/scheme/register.go`
**open-telemetry/opentelemetry-operator:**
- `cmd/otel-allocator/internal/config/config.go`
- `cmd/operator-opamp-bridge/internal/config/config.go`
- `internal/operator-metrics/metrics.go`

</details>

### 11. SA_TC011

**Source:** `kubernetes-sigs/kustomize` / `kyaml/yaml/rnode.go`
**Change type:** method_signature_change
**Change:** Change `func (rn *RNode) PipeE(functions ...Filter) error` to `func (rn *RNode) PipeE(pipeline Pipeline) error`
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `action.go` | Helm calls manifest.PipeE(kyaml.SetAnnotation(...)) at line 167 and manifest.PipeE(kyaml.ClearAnnotation(...)) at line 1 |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/action/action.go`

</details>

### 12. SA_TC012

**Source:** `helm/helm` / `pkg/chart/v2/util/chartfile.go`
**Change type:** function_signature_change
**Change:** Change `func LoadChartfile(filename string) (*chart.Metadata, error)` to return `(*chart.ChartFile, error)` and change `func SaveChartfile(filename string, cf *chart.Metadata) error` to accept `*chart.ChartFile`
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| ingress-nginx | `helm.go` | Ingress-nginx calls chartutil.LoadChartfile() at lines 46, 54, and 107 and accesses chart.Version, chart.AppVersion, and |

<details>
<summary>Full file paths</summary>

**kubernetes/ingress-nginx:**
- `magefiles/steps/helm.go`

</details>

### 13. SA_TC013

**Source:** `kubernetes-sigs/kustomize` / `kyaml/yaml/types.go`
**Change type:** interface_modification
**Change:** Change `Filter(object *RNode) (*RNode, error)` to `Filter(ctx context.Context, object *RNode) (*RNode, error)` in the Filter interface
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `action.go` | Helm passes kyaml.SetAnnotation() and kyaml.ClearAnnotation() Filter implementations to manifest.PipeE() at lines 167 an |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/action/action.go`

</details>

### 14. NK_TC012

**Source:** `kubernetes-sigs/kustomize` / `kyaml/yaml/types.go`
**Change type:** struct_field_rename
**Change:** Rename `Annotations map[string]string` to `MetadataAnnotations map[string]string` in ObjectMeta within ResourceMeta
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `action.go` | Helm splitAndDeannotate() calls manifest.GetMeta() and accesses meta.Annotations directly for removing internal annotati |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/action/action.go`

</details>

### 15. NK_TC015

**Source:** `helm/helm` / `pkg/chart/v2/chart.go`
**Change type:** struct_modification
**Change:** Rename `Version string` to `ChartVersion string` and `AppVersion string` to `ApplicationVersion string` in chart.Metadata
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| ingress-nginx | `helm.go` | Ingress-nginx accesses chart.Version and chart.AppVersion after calling chartutil.LoadChartfile() in updateVersion() and |

<details>
<summary>Full file paths</summary>

**kubernetes/ingress-nginx:**
- `magefiles/steps/helm.go`

</details>

### 16. KM_TC001

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/interfaces.go`
**Change type:** interface_modification
**Change:** Add `DeepCopyContext(ctx context.Context) Object` method to the Object interface
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `client.go` | Helm kube client works with runtime.Object for resource creation and updates |
| argo-cd | `ctl.go`, `sync_context.go` | ArgoCD gitops-engine manipulates runtime.Object for applying and syncing Kubernetes resources |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/client.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/utils/kube/ctl.go`
- `gitops-engine/pkg/sync/sync_context.go`

</details>

### 17. KM_TC002

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/apps/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Replicas *int32` to `Replicas *int64` in DeploymentSpec
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `ready.go` | Helm checks Deployment readiness by accessing deployment.Spec.Replicas for comparing desired vs available replicas |
| argo-cd | `health_deployment.go` | ArgoCD health checker accesses deployment.Spec.Replicas to determine Deployment health status |
| autoscaler | `controller_fetcher.go` | VPA controller fetcher reads Deployment.Spec.Replicas for scaling target identification |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/ready.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/health/health_deployment.go`
**kubernetes/autoscaler:**
- `vertical-pod-autoscaler/pkg/target/controller_fetcher/controller_fetcher.go`

</details>

### 18. KM_TC003

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Labels map[string]string` to `Labels LabelMap` where LabelMap has Get/Set methods instead of direct map access
**Repos involved:** 5 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `list.go`, `secrets.go` | Helm accesses resource.Labels map directly for release filtering in list.go and for labeling storage Secrets in secrets. |
| argo-cd | `appcontroller.go`, `settings.go` | ArgoCD reads and writes ObjectMeta.Labels on Application CRDs and ConfigMaps for filtering and identification |
| external-dns | `service.go`, `ingress.go` | External-DNS reads resource.Labels for annotation-based DNS endpoint configuration |
| cert-manager | `pod.go` | Cert-manager sets Labels map on ACME challenge pods using direct map assignment |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/action/list.go`
- `pkg/storage/driver/secrets.go`
**argoproj/argo-cd:**
- `controller/appcontroller.go`
- `util/settings/settings.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`
- `source/ingress.go`
**cert-manager/cert-manager:**
- `pkg/issuer/acme/http/pod.go`

</details>

### 19. KM_TC004

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/kubernetes/clientset.go`
**Change type:** interface_modification
**Change:** Add `WithContext(ctx context.Context) Interface` method to kubernetes.Interface
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `client.go` | Helm kube client wraps kubernetes.Interface for all Kubernetes API operations |
| ingress-nginx | `store.go` | Ingress-nginx store creates and uses kubernetes.Clientset for watching resources |
| cert-manager | `issuing_controller.go` | Cert-manager issuing controller uses kubernetes.Interface for Secret CRUD operations |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/client.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`
**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/issuing_controller.go`

</details>

### 20. KM_TC006

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Data map[string]string` to `Data ConfigData` where ConfigData has Get/Set methods
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `settings.go` | ArgoCD reads argocd-cm ConfigMap.Data map extensively for application settings, OIDC config, and resource customizations |
| ingress-nginx | `store.go` | Ingress-nginx reads ConfigMap.Data for nginx configuration parameters |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `util/settings/settings.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`

</details>

### 21. KM_TC007

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Name string` to `Name ResourceName` in ObjectMeta where ResourceName requires .String() for string conversion
**Repos involved:** 4 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `secrets.go`, `ready.go` | Helm accesses resource.Name as a string for Secret naming in storage driver and resource identification in readiness che |
| argo-cd | `appcontroller.go`, `cluster.go` | ArgoCD accesses ObjectMeta.Name for Application and cluster Secret identification |
| external-dns | `service.go`, `ingress.go` | External-DNS reads resource.Name for DNS endpoint source identification |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/storage/driver/secrets.go`
- `pkg/kube/ready.go`
**argoproj/argo-cd:**
- `controller/appcontroller.go`
- `util/db/cluster.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`
- `source/ingress.go`

</details>

### 22. KM_TC008

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/clientcmd/api/types.go`
**Change type:** struct_field_modification
**Change:** Change `Clusters map[string]*Cluster` to `Clusters ClusterMap` with Get/Set accessor methods
**Repos involved:** 2 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `cluster.go`, `cluster.go` | ArgoCD reads and constructs kubeconfig Config.Clusters map for multi-cluster management, accessing clusters by name with |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `util/db/cluster.go`
- `cmd/util/cluster.go`

</details>

### 23. KM_TC009

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/batch/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Template corev1.PodTemplateSpec` to `Template *corev1.PodTemplateSpec` in JobSpec
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `ready.go` | Helm checks Job readiness by accessing job.Spec fields for completion status |
| argo-cd | `health_job.go` | ArgoCD health checker accesses Job spec for determining Job health status |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/ready.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/health/health_job.go`

</details>

### 24. KM_TC010

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Conditions []NodeCondition` to `Conditions NodeConditionList` in NodeStatus
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| autoscaler | `listers.go` | Cluster autoscaler reads node.Status.Conditions for determining node readiness and scheduling decisions |
| karpenter | `controller.go` | Karpenter reads node conditions for node lifecycle management and drift detection |

<details>
<summary>Full file paths</summary>

**kubernetes/autoscaler:**
- `cluster-autoscaler/utils/kubernetes/listers.go`
**kubernetes-sigs/karpenter:**
- `pkg/controllers/nodeclass/controller.go`

</details>

### 25. KM_TC011

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/record/event.go`
**Change type:** interface_modification
**Change:** Add `EventWithFields(object runtime.Object, fields map[string]string, eventtype, reason, messageFmt string, args ...interface{})` to EventRecorder interface
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cert-manager | `issuing_controller.go`, `trigger_controller.go` | Cert-manager controllers use EventRecorder to emit certificate lifecycle events |
| ingress-nginx | `store.go` | Ingress-nginx uses EventRecorder for emitting configuration change events |

<details>
<summary>Full file paths</summary>

**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/issuing_controller.go`
- `pkg/controller/certificates/trigger/trigger_controller.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`

</details>

### 26. KM_TC012

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/networking/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Service *IngressServiceBackend` to `Service IngressServiceBackend` in IngressBackend
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| ingress-nginx | `store.go`, `endpointslices.go` | Ingress-nginx accesses backend.Service with nil checks for routing configuration and endpoint resolution |
| external-dns | `ingress.go` | External-DNS reads IngressBackend.Service for extracting service-based DNS endpoints from Ingress rules |

<details>
<summary>Full file paths</summary>

**kubernetes/ingress-nginx:**
- `internal/ingress/controller/store/store.go`
- `internal/ingress/controller/endpointslices.go`
**kubernetes-sigs/external-dns:**
- `source/ingress.go`

</details>

### 27. KM_TC013

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/types/namespacedname.go`
**Change type:** struct_modification
**Change:** Add `Cluster string` field to NamespacedName struct
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| argo-cd | `appcontroller.go` | ArgoCD creates NamespacedName{Namespace, Name} literals for identifying Applications |
| cert-manager | `issuing_controller.go` | Cert-manager uses NamespacedName for identifying Certificate resources in reconciliation |
| crossplane | `reconciler.go` | Crossplane uses NamespacedName for identifying composite resources in reconciliation |

<details>
<summary>Full file paths</summary>

**argoproj/argo-cd:**
- `controller/appcontroller.go`
**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/issuing_controller.go`
**crossplane/crossplane:**
- `internal/controller/apiextensions/composite/reconciler.go`

</details>

### 28. KM_TC014

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/rest/request.go`
**Change type:** method_signature_change
**Change:** Change `func (r *Request) Do(ctx context.Context) Result` to `func (r *Request) Do(ctx context.Context) (*Result, error)`
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| helm | `client.go` | Helm kube client chains .Do(ctx).Into() for Kubernetes API calls |
| argo-cd | `ctl.go` | ArgoCD gitops-engine uses rest.Request.Do() for applying and patching resources |

<details>
<summary>Full file paths</summary>

**helm/helm:**
- `pkg/kube/client.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/utils/kube/ctl.go`

</details>

### 29. KM_TC015

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Port int32` to `Port PortNumber` in ServicePort where PortNumber is a named type with range validation
**Repos involved:** 4 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| ingress-nginx | `endpointslices.go`, `store.go` | Ingress-nginx reads ServicePort.Port for backend endpoint resolution and nginx configuration |
| external-dns | `service.go` | External-DNS reads ServicePort for constructing SRV DNS records from Kubernetes Services |
| cert-manager | `service.go` | Cert-manager sets ServicePort.Port when creating Services for ACME HTTP-01 challenge solving |

<details>
<summary>Full file paths</summary>

**kubernetes/ingress-nginx:**
- `internal/ingress/controller/endpointslices.go`
- `internal/ingress/controller/store/store.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`
**cert-manager/cert-manager:**
- `pkg/issuer/acme/http/service.go`

</details>

### 30. CRW_TC001

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Requests ResourceList` to `ResourceRequests ResourceList` in ResourceRequirements
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `resource_ctors.go` | Cilium resource constructors use corev1 resource types for Pod, Service, Namespace watchers |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/resource_ctors.go`

</details>

### 31. CRW_TC002

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/record/event.go`
**Change type:** interface_modification
**Change:** Add `EventfWithAnnotations(object runtime.Object, annotations map[string]string, eventtype, reason, messageFmt string, args ...interface{})` to EventRecorder interface
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `dropeventemitter.go` | Cilium creates record.EventBroadcaster and record.EventRecorder at lines 42-43 and 52-75 |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/hubble/dropeventemitter/dropeventemitter.go`

</details>

### 32. CRW_TC003

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/portforward/portforward.go`
**Change type:** function_signature_change
**Change:** Add `ctx context.Context` as first parameter to `NewOnAddresses()`
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `portforward.go` | Cilium calls portforward.NewOnAddresses(dialer, p.Addresses, p.Ports, ...) at line 87 |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/portforward/portforward.go`

</details>

### 33. CRW_TC004

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/api/errors/errors.go`
**Change type:** function_signature_change
**Change:** Change `func IsNotFound(err error) bool` to `func IsNotFound(err error) (bool, string)`
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `externalsecret_controller.go` | External-secrets calls apierrors.IsNotFound() for secret existence checks in reconciler |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/externalsecret/externalsecret_controller.go`

</details>

### 34. CRW_TC005

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/labels/selector.go`
**Change type:** method_signature_change
**Change:** Add `error` return to `Matches(labels.Labels) bool` method on Selector interface
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `clusterpushsecret_controller.go` | External-secrets imports k8s.io/apimachinery/pkg/labels and uses label selection at line 32 |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/clusterpushsecret/clusterpushsecret_controller.go`

</details>

### 35. CRW_TC006

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/kubernetes/clientset.go`
**Change type:** function_signature_change
**Change:** Change `NewForConfig(c *rest.Config) (*Clientset, error)` to require a context: `NewForConfig(ctx context.Context, c *rest.Config) (*Clientset, error)`
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `provider.go` | External-secrets calls kubernetes.NewForConfig(restCfg) for vault provider client creation |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `providers/v1/vault/provider.go`

</details>

### 36. CRW_TC007

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/watch/watch.go`
**Change type:** interface_modification
**Change:** Add `Context() context.Context` method to watch.Interface
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| flux2 | `get.go` | Flux2 imports k8s.io/apimachinery/pkg/watch and k8s.io/client-go/tools/watch at lines 29-30 |

<details>
<summary>Full file paths</summary>

**fluxcd/flux2:**
- `cmd/flux/get.go`

</details>

### 37. CRW_TC008

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/util/retry/util.go`
**Change type:** function_signature_change
**Change:** Change `RetryOnConflict(backoff wait.Backoff, fn func() error) error` to require a context parameter
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| flux2 | `reconcile.go` | Flux2 imports k8s.io/client-go/util/retry at line 31 for reconciliation retry logic |

<details>
<summary>Full file paths</summary>

**fluxcd/flux2:**
- `cmd/flux/reconcile.go`

</details>

### 38. CRW_TC009

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/unstructured/unstructured.go`
**Change type:** method_signature_change
**Change:** Change `func (u *Unstructured) SetName(name string)` to `func (u *Unstructured) SetName(name string) error`
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| gatekeeper | `system.go` | Gatekeeper imports unstructured and uses Unstructured objects at line 17 for expansion system |

<details>
<summary>Full file paths</summary>

**open-policy-agent/gatekeeper:**
- `pkg/expansion/system.go`

</details>

### 39. CRW_TC010

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/rest/config.go`
**Change type:** struct_field_modification
**Change:** Rename `Host string` to `APIServerURL string` in rest.Config struct
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `client_factory.go` | Istio creates rest.Config via clientcmd.BuildConfigFromFlags and clientcmd.ClientConfig |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pkg/kube/client_factory.go`

</details>

### 40. CRW_TC011

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/dynamic/interface.go`
**Change type:** interface_modification
**Change:** Add `ListAll(ctx context.Context, gvr schema.GroupVersionResource) (*unstructured.UnstructuredList, error)` to dynamic.Interface
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `client.go` | Istio calls dynamic.NewForConfig() in kube client.go for dynamic resource operations |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pkg/kube/client.go`

</details>

### 41. CRW_TC012

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/admissionregistration/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Webhooks []MutatingWebhook` to `WebhookHandlers []MutatingWebhook` in MutatingWebhookConfiguration
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `webhookpatch.go` | Istio uses kclient.Client[*v1.MutatingWebhookConfiguration] and patches CA bundles |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pkg/webhooks/webhookpatch.go`

</details>

### 42. CRW_TC013

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Labels map[string]string` to `MetadataLabels map[string]string` in ObjectMeta
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `utils.go` | Cilium uses metav1.LabelSelector, labels.NewSelector() and labels.NewRequirement() |
| istio | `namespacecontroller.go` | Istio uses metav1.ObjectMeta for namespace and configmap filtering at lines 18-21 |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/utils/utils.go`
**istio/istio:**
- `pilot/pkg/serviceregistry/kube/controller/namespacecontroller.go`

</details>

### 43. CRW_TC014

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/scheme.go`
**Change type:** function_signature_change
**Change:** Change `func NewScheme() *Scheme` to require a name: `func NewScheme(name string) *Scheme`
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `crds_controller.go` | External-secrets uses runtime.Scheme for CRD handling in CRDs controller |
| gatekeeper | `main.go` | Gatekeeper calls runtime.NewScheme() in main.go for scheme initialization |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/crds/crds_controller.go`
**open-policy-agent/gatekeeper:**
- `main.go`

</details>

### 44. CRW_TC015

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/apps/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Spec DeploymentSpec` to `DeploymentConfiguration DeploymentSpec` in Deployment
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| flux2 | `check.go` | Flux2 lists Flux component Deployments with label selectors in check command |
| helm | `ready.go` | Helm checks Deployment readiness by accessing deployment.Spec for completion status |

<details>
<summary>Full file paths</summary>

**fluxcd/flux2:**
- `cmd/flux/check.go`
**helm/helm:**
- `pkg/kube/ready.go`

</details>

### 45. CRW_TC016

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/record/event.go`
**Change type:** interface_modification
**Change:** Change `NewBroadcasterWithCorrelatorOptions(options CorrelatorOptions) EventBroadcaster` to require context
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `dropeventemitter.go` | Cilium calls record.NewBroadcasterWithCorrelatorOptions at line 52 |
| external-secrets | `externalsecret_controller.go` | External-secrets uses tools/record for event recording in reconciler |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/hubble/dropeventemitter/dropeventemitter.go`
**external-secrets/external-secrets:**
- `pkg/controllers/externalsecret/externalsecret_controller.go`

</details>

### 46. CRW_TC017

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Spec CustomResourceDefinitionSpec` to `CRDSpec CustomResourceDefinitionSpec`
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| gatekeeper | `manager.go` | Gatekeeper uses apiextensionsv1.CustomResourceDefinition in upgrade manager |
| crossplane | `establisher.go` | Crossplane handles CRD establishment for package revisions |

<details>
<summary>Full file paths</summary>

**open-policy-agent/gatekeeper:**
- `pkg/upgrade/manager.go`
**crossplane/crossplane:**
- `internal/controller/pkg/revision/establisher.go`

</details>

### 47. CRW_TC018

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Data map[string][]byte` to `SecretData map[string][]byte` in Secret
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `casecret.go` | Istio uses v1.Secret with corev1.CoreV1Interface for CA secret management |
| cert-manager | `secret.go` | Cert-manager creates and manages TLS secrets in issuing controller |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `security/pkg/k8s/controller/casecret.go`
**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/internal/secret.go`

</details>

### 48. CRW_TC019

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Type string` to `ConditionType string` in Condition
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| flux2 | `reconcile.go` | Flux2 uses metav1.Condition at line 69-78 for reconciliation status checking |
| argo-cd | `health_test.go` | ArgoCD uses metav1.Condition for health check status evaluation |

<details>
<summary>Full file paths</summary>

**fluxcd/flux2:**
- `cmd/flux/reconcile.go`
**argoproj/argo-cd:**
- `controller/health_test.go`

</details>

### 49. CRW_TC020

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/networking/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Spec IngressSpec` to `IngressConfiguration IngressSpec` in Ingress
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `controller.go` | Istio processes knetworking.Ingress resources in ingress controller |
| ingress-nginx | `controller.go` | Ingress-nginx accesses Ingress spec for routing configuration |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pilot/pkg/config/kube/ingress/controller.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/controller.go`

</details>

### 50. CRW_TC021

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Spec NodeSpec` to `NodeConfiguration NodeSpec` in Node
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `resource_ctors.go` | Cilium creates Node resource watchers using slim_corev1.Node |
| karpenter | `controller.go` | Karpenter manages Node lifecycle in termination controller |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/resource_ctors.go`
**kubernetes-sigs/karpenter:**
- `pkg/controllers/nodeclaim/garbagecollection/controller.go`

</details>

### 51. CRW_TC022

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/admissionregistration/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Webhooks []ValidatingWebhook` to `ValidationRules []ValidatingWebhook`
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| gatekeeper | `webhook.go` | Gatekeeper references ValidatingWebhookConfiguration and MutatingWebhookConfiguration |
| istio | `controller.go` | Istio uses kubeApiAdmission.ValidatingWebhookConfiguration with kclient patterns |

<details>
<summary>Full file paths</summary>

**open-policy-agent/gatekeeper:**
- `pkg/webhook/webhook.go`
**istio/istio:**
- `pkg/webhooks/validation/controller/controller.go`

</details>

### 52. CRW_TC023

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/schema/group_version.go`
**Change type:** method_signature_change
**Change:** Change `func (gvr GroupVersionResource) String() string` to return `(string, error)`
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `informer_manager.go` | External-secrets uses schema.GroupVersionKind and unstructured.Unstructured in informer manager |
| crossplane | `reconciler.go` | Crossplane uses schema.GroupVersionKind for composite resource reconciliation |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/externalsecret/informer_manager.go`
**crossplane/crossplane:**
- `internal/controller/apiextensions/composite/reconciler.go`

</details>

### 53. CRW_TC024

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Spec NamespaceSpec` to `NamespaceConfiguration NamespaceSpec` in Namespace
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| flux2 | `uninstall.go` | Flux2 lists and deletes corev1.Namespace resources during uninstall |
| external-dns | `service.go` | External-DNS uses Namespace filtering for service discovery |

<details>
<summary>Full file paths</summary>

**fluxcd/flux2:**
- `pkg/uninstall/uninstall.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`

</details>

### 54. CRW_TC025

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Status PodStatus` to `PodCurrentStatus PodStatus` in Pod
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `pod.go` | Cilium implements Pod watcher with slim_corev1.Pod handling |
| autoscaler | `fetcher.go` | Autoscaler fetches Pod status for VPA recommendations |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/watchers/pod.go`
**kubernetes/autoscaler:**
- `vertical-pod-autoscaler/pkg/target/fetcher.go`

</details>

### 55. CRW_TC026

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/labels/selector.go`
**Change type:** method_signature_change
**Change:** Add `ctx context.Context` as first parameter to `NewRequirement()`
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `filter.go` | Istio uses labels.Selector for namespace filtering |
| external-dns | `source.go` | External-DNS uses labels.NewSelector() and labels.NewRequirement() for source filtering |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pkg/kube/namespace/filter.go`
**kubernetes-sigs/external-dns:**
- `source/source.go`

</details>

### 56. CRW_TC027

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/serializer/codec_factory.go`
**Change type:** function_signature_change
**Change:** Change `NewCodecFactory(scheme *runtime.Scheme, mutators ...CodecFactoryOptionsMutator) CodecFactory` to require a name string
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| gatekeeper | `main.go` | Gatekeeper calls apis.AddToScheme(runtimeScheme) for runtime.Scheme registration in main |
| cert-manager | `scheme.go` | Cert-manager registers types via AddToScheme in its central scheme.go |

<details>
<summary>Full file paths</summary>

**open-policy-agent/gatekeeper:**
- `main.go`
**cert-manager/cert-manager:**
- `pkg/api/scheme.go`

</details>

### 57. CRW_TC028

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Ports []ServicePort` to `ServicePorts []ServicePort` in ServiceSpec
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `resource_ctors.go` | Cilium creates Service resource watchers via slim_corev1.Service |
| istio | `controller.go` | Istio processes Service resources via kclient for service registry |
| ingress-nginx | `endpointslices.go` | Ingress-nginx resolves Service endpoints for backend routing |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/resource_ctors.go`
**istio/istio:**
- `pilot/pkg/serviceregistry/kube/controller/controller.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/endpointslices.go`

</details>

### 58. CRW_TC029

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/unstructured/unstructured.go`
**Change type:** struct_field_modification
**Change:** Change `Object map[string]interface{}` to `Object map[string]any` in Unstructured (requiring Go 1.18+)
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `informer_manager.go` | External-secrets uses unstructured.Unstructured in informer manager for dynamic resources |
| gatekeeper | `client.go` | Gatekeeper uses *unstructured.Unstructured for AddConstraint at line 22 |
| crossplane | `reconciler.go` | Crossplane works with unstructured objects for composite resource management |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/externalsecret/informer_manager.go`
**open-policy-agent/gatekeeper:**
- `pkg/gator/client.go`
**crossplane/crossplane:**
- `internal/controller/apiextensions/composite/reconciler.go`

</details>

### 59. CRW_TC030

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/apps/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Replicas *int32` to `DesiredReplicas *int32` in DeploymentSpec
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| flux2 | `check.go` | Flux2 checks Deployment status with label selectors for component readiness |
| helm | `ready.go` | Helm checks Deployment readiness by examining Spec.Replicas vs Status.ReadyReplicas |
| argo-cd | `health_deployment.go` | ArgoCD health checker reads Deployment spec/status for determining health |

<details>
<summary>Full file paths</summary>

**fluxcd/flux2:**
- `cmd/flux/check.go`
**helm/helm:**
- `pkg/kube/ready.go`
**argoproj/argo-cd:**
- `gitops-engine/pkg/health/health_deployment.go`

</details>

### 60. CRW_TC031

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Addresses []EndpointAddress` to `EndpointAddresses []EndpointAddress` in EndpointSubset
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `resource_ctors.go` | Cilium creates Endpoints resource watchers for service discovery |
| external-dns | `service.go` | External-DNS resolves service endpoints for DNS record creation |
| ingress-nginx | `controller.go` | Ingress-nginx resolves service endpoints for backend routing configuration |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/resource_ctors.go`
**kubernetes-sigs/external-dns:**
- `source/service.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/controller.go`

</details>

### 61. CRW_TC032

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/networking/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Rules []IngressRule` to `IngressRules []IngressRule` in IngressSpec
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `controller.go` | Istio processes Ingress resources and converts rules to Istio configuration |
| cert-manager | `ingress.go` | Cert-manager creates Ingress resources for ACME HTTP-01 challenge solving |
| ingress-nginx | `controller.go` | Ingress-nginx processes IngressSpec.Rules for routing configuration |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pilot/pkg/config/kube/ingress/controller.go`
**cert-manager/cert-manager:**
- `pkg/issuer/acme/http/ingress.go`
**kubernetes/ingress-nginx:**
- `internal/ingress/controller/controller.go`

</details>

### 62. CRW_TC033

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/admissionregistration/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `ClientConfig WebhookClientConfig` to `WebhookConfig WebhookClientConfig` in ValidatingWebhook
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| gatekeeper | `webhook.go` | Gatekeeper manages ValidatingWebhookConfiguration with VwhName at line 60 |
| istio | `controller.go` | Istio creates and patches ValidatingWebhookConfiguration for istiod validation |
| crossplane | `webhook_configurations.go` | Crossplane initializes webhook configurations during startup |

<details>
<summary>Full file paths</summary>

**open-policy-agent/gatekeeper:**
- `pkg/webhook/webhook.go`
**istio/istio:**
- `pkg/webhooks/validation/controller/controller.go`
**crossplane/crossplane:**
- `internal/initializer/webhook_configurations.go`

</details>

### 63. CRW_TC034

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Tolerations []Toleration` to `PodTolerations []Toleration` in PodSpec
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `pod.go` | Cilium's Pod watcher processes Pod spec fields including tolerations |
| istio | `types.go` | Istio operator spec defines Tolerations []*corev1.Toleration at line 175 for component scheduling |
| argo-cd | `corev1_known_types.go` | ArgoCD normalizes known corev1 types including Toleration for resource diffing |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/watchers/pod.go`
**istio/istio:**
- `operator/pkg/apis/types.go`
**argoproj/argo-cd:**
- `util/argo/normalizers/corev1_known_types.go`

</details>

### 64. CRW_TC035

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Change `Type SecretType` to `SecretKind SecretType` in Secret
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `pushsecret_controller.go` | External-secrets pushes Secret resources to external stores in push secret controller |
| flux2 | `sourcesecret.go` | Flux2 uses corev1.SecretTypeDockerConfigJson for source secret generation |
| cert-manager | `secret.go` | Cert-manager creates TLS secrets with specific Secret types |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/pushsecret/pushsecret_controller.go`
**fluxcd/flux2:**
- `pkg/manifestgen/sourcesecret/sourcesecret.go`
**cert-manager/cert-manager:**
- `pkg/controller/certificates/issuing/internal/secret.go`

</details>

### 65. CRW_TC036

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/rest/config.go`
**Change type:** struct_field_modification
**Change:** Rename `QPS float32` to `RequestsPerSecond float32` in rest.Config
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `client.go` | Istio configures rest.Config for kube client creation |
| helm | `client.go` | Helm uses rest.Config for Kubernetes API communication |
| argo-cd | `types.go` | ArgoCD configures rest.Config for cluster management |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pkg/kube/client.go`
**helm/helm:**
- `pkg/kube/client.go`
**argoproj/argo-cd:**
- `pkg/apis/application/v1alpha1/types.go`

</details>

### 66. CRW_TC037

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/labels/selector.go`
**Change type:** method_signature_change
**Change:** Change `func Parse(selector string) (Selector, error)` to require validation option
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `utils.go` | Cilium uses labels.NewSelector() and labels.NewRequirement() for policy filtering |
| istio | `controller.go` | Istio uses klabels (k8s.io/apimachinery/pkg/labels) for service discovery filtering |
| external-dns | `source.go` | External-DNS uses labels selectors for endpoint source filtering |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/utils/utils.go`
**istio/istio:**
- `pilot/pkg/serviceregistry/kube/controller/controller.go`
**kubernetes-sigs/external-dns:**
- `source/source.go`

</details>

### 67. CRW_TC038

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/apimachinery/pkg/runtime/scheme.go`
**Change type:** method_signature_change
**Change:** Add `error` return value to `AddToScheme(s *Scheme) error` functions
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| gatekeeper | `main.go` | Gatekeeper calls apis.AddToScheme(runtimeScheme) in main.go init |
| flux2 | `utils.go` | Flux2 calls corev1.AddToScheme(), appsv1.AddToScheme() for scheme registration |
| helm | `client.go` | Helm calls AddToScheme for runtime.Scheme registration in kube client |

<details>
<summary>Full file paths</summary>

**open-policy-agent/gatekeeper:**
- `main.go`
**fluxcd/flux2:**
- `internal/utils/utils.go`
**helm/helm:**
- `pkg/kube/client.go`

</details>

### 68. CRW_TC039

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/client-go/tools/record/event.go`
**Change type:** interface_modification
**Change:** Change `Event(object runtime.Object, eventtype, reason, message string)` to require a context parameter
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| external-secrets | `clusterpushsecret_controller.go` | External-secrets uses record.EventRecorder for cluster push secret events |
| crossplane | `reconciler.go` | Crossplane records events during composite resource reconciliation |
| cert-manager | `setup.go` | Cert-manager uses Recorder.Event() at lines 52-77 for issuer events |

<details>
<summary>Full file paths</summary>

**external-secrets/external-secrets:**
- `pkg/controllers/clusterpushsecret/clusterpushsecret_controller.go`
**crossplane/crossplane:**
- `internal/controller/apiextensions/composite/reconciler.go`
**cert-manager/cert-manager:**
- `pkg/issuer/ca/setup.go`

</details>

### 69. CRW_TC040

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Data map[string]string` to `ConfigData map[string]string` in ConfigMap
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| cilium | `resource_ctors.go` | Cilium watches ConfigMap resources for cluster configuration |
| gatekeeper | `manager.go` | Gatekeeper uses ConfigMap for audit configuration via client-go patterns |
| flux2 | `sourcesecret.go` | Flux2 generates ConfigMap manifests for source configuration |

<details>
<summary>Full file paths</summary>

**cilium/cilium:**
- `pkg/k8s/resource_ctors.go`
**open-policy-agent/gatekeeper:**
- `pkg/audit/manager.go`
**fluxcd/flux2:**
- `pkg/manifestgen/sourcesecret/sourcesecret.go`

</details>

### 70. CRW_TC041

**Source:** `kubernetes/kubernetes` / `staging/src/k8s.io/api/core/v1/types.go`
**Change type:** struct_field_modification
**Change:** Rename `Containers []Container` to `AppContainers []Container` in PodSpec
**Repos involved:** 4 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| istio | `pod.go` | Istio accesses pod.Spec.Containers for service mesh sidecar injection |
| autoscaler | `cluster_feeder.go` | Autoscaler reads container resource requests for VPA recommendations |
| helm | `client.go` | Helm accesses pod.Spec.Containers at line 1262 for resource readiness checking |

<details>
<summary>Full file paths</summary>

**istio/istio:**
- `pilot/pkg/serviceregistry/kube/controller/pod.go`
**kubernetes/autoscaler:**
- `vertical-pod-autoscaler/pkg/recommender/input/cluster_feeder.go`
**helm/helm:**
- `pkg/kube/client.go`

</details>

### 71. OBS_TC001

**Source:** `prometheus/prometheus` / `storage/interface.go`
**Change type:** interface_modification
**Change:** Add `SelectSorted(ctx context.Context, hints *SelectHints, matchers ...*labels.Matcher) SeriesSet` method to Querier interface
**Repos involved:** 3 | **Affected files:** 5

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `querier.go`, `iter.go` | Thanos BucketStore and query layer implement the Prometheus Querier interface to serve time-series data over gRPC StoreA |
| mimir | `compactor.go`, `bucketindex.go` | Mimir's compactor and TSDB bucket index layer use Prometheus storage.Querier for block-level queries during compaction |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/query/querier.go`
- `pkg/query/iter.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/storage/tsdb/bucketindex/bucketindex.go`

</details>

### 72. OBS_TC002

**Source:** `prometheus/prometheus` / `model/labels/labels_common.go`
**Change type:** type_change
**Change:** Change `type Labels []Label` to `type Labels struct { data []Label }` with accessor methods
**Repos involved:** 5 | **Affected files:** 9

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `lazy_postings.go`, `querier.go` | Thanos store and query packages directly construct and iterate prometheus labels.Labels for series matching and deduplic |
| mimir | `compactor.go`, `split_merge_compactor.go` | Mimir compactor uses labels.Labels for block-level label filtering and split-merge operations |
| loki | `ruler.go`, `store.go` | Loki ruler uses prometheus labels.Labels for recording rule evaluation and label manipulation |
| opentelemetry-collector-contrib | `accumulator.go`, `collector.go` | OTel Prometheus exporter converts OpenTelemetry metrics to Prometheus format using labels.Labels |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/store/lazy_postings.go`
- `pkg/query/querier.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
**grafana/loki:**
- `pkg/ruler/ruler.go`
- `pkg/ruler/rulestore/store.go`
**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/accumulator.go`
- `exporter/prometheusexporter/collector.go`

</details>

### 73. OBS_TC003

**Source:** `prometheus/prometheus` / `model/histogram/histogram.go`
**Change type:** struct_field_change
**Change:** Add `CreatedTimestamp int64` field to Histogram struct
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `compact.go` | Thanos store and compactor handle native histograms from Prometheus TSDB blocks, constructing and reading Histogram stru |
| mimir | `compactor.go`, `bucket_compactor.go` | Mimir compactor processes native histogram data during block compaction, constructing Histogram instances |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/compact/compact.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/bucket_compactor.go`

</details>

### 74. OBS_TC004

**Source:** `prometheus/prometheus` / `tsdb/db.go`
**Change type:** method_signature_change
**Change:** Add `ctx context.Context` as first parameter to `DB.Querier(mint, maxt int64)` method
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `querier.go` | Thanos calls DB.Querier to read local TSDB data through the sidecar component |
| mimir | `compactor.go`, `bucketindex.go` | Mimir ingester and compactor call DB.Querier for local TSDB reads and compaction queries |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/query/querier.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/storage/tsdb/bucketindex/bucketindex.go`

</details>

### 75. OBS_TC005

**Source:** `prometheus/prometheus` / `promql/engine.go`
**Change type:** interface_modification
**Change:** Add `ExplainQuery(ctx context.Context, qs string) (*QueryPlan, error)` method to QueryEngine
**Repos involved:** 4 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `querier.go`, `remote_engine.go` | Thanos query layer wraps the Prometheus PromQL engine for distributed query evaluation and must implement any new engine |
| mimir | `compactor.go` | Mimir query-frontend uses Prometheus PromQL engine for query splitting and must satisfy the engine interface |
| grafana | `prometheus_metrics_middleware.go` | Grafana's Prometheus datasource wraps the PromQL engine for query execution and metrics collection |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/query/querier.go`
- `pkg/query/remote_engine.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
**grafana/grafana:**
- `pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go`

</details>

### 76. OBS_TC006

**Source:** `prometheus/prometheus` / `storage/interface_append.go`
**Change type:** interface_modification
**Change:** Add `AppendCTZeroSample(ref SeriesRef, l labels.Labels, t, ct int64) (SeriesRef, error)` to Appender interface
**Repos involved:** 4 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `compact.go` | Thanos receive component implements storage.Appender for ingesting remote-write data from Prometheus instances |
| mimir | `compactor.go`, `bucket_compactor.go` | Mimir distributor implements storage.Appender for ingesting samples from Prometheus remote-write |
| opentelemetry-collector-contrib | `prometheus.go`, `accumulator.go` | OTel Prometheus exporter uses storage.Appender to write converted OTLP metrics into Prometheus format |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/compact/compact.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/bucket_compactor.go`
**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/prometheus.go`
- `exporter/prometheusexporter/accumulator.go`

</details>

### 77. OBS_TC007

**Source:** `prometheus/prometheus` / `config/config.go`
**Change type:** struct_field_change
**Change:** Change `ScrapeInterval model.Duration` to `ScrapeInterval ValidatedDuration` in GlobalConfig
**Repos involved:** 4 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `querier.go`, `compact.go` | Thanos ruler and query components read GlobalConfig.ScrapeInterval for step alignment in range queries |
| mimir | `compactor.go` | Mimir ruler embeds Prometheus GlobalConfig for rule evaluation interval configuration |
| grafana | `prometheus_flavor.go` | Grafana reads Prometheus GlobalConfig to detect scrape configuration for usage statistics |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/query/querier.go`
- `pkg/compact/compact.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
**grafana/grafana:**
- `pkg/infra/usagestats/statscollector/prometheus_flavor.go`

</details>

### 78. OBS_TC008

**Source:** `prometheus/prometheus` / `model/labels/matcher.go`
**Change type:** type_change
**Change:** Change `Matches(v string) bool` to `Matches(v string) (bool, error)` on Matcher
**Repos involved:** 4 | **Affected files:** 6

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `bucket.go`, `filter_cache.go` | Thanos store uses labels.Matcher.Matches for filtering series during store queries |
| mimir | `compactor.go`, `split_merge_compactor.go` | Mimir uses Matcher for label-based series filtering during compaction and query evaluation |
| loki | `ruler.go`, `ruler.go` | Loki ruler evaluates recording rules using Prometheus label matchers for log-to-metric conversion |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/store/bucket.go`
- `pkg/store/cache/filter_cache.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
**grafana/loki:**
- `pkg/ruler/ruler.go`
- `pkg/ruler/base/ruler.go`

</details>

### 79. OBS_TC009

**Source:** `prometheus/prometheus` / `discovery/discovery.go`
**Change type:** interface_modification
**Change:** Add `HealthCheck(ctx context.Context) error` method to Discoverer interface
**Repos involved:** 2 | **Affected files:** 1

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `endpointset.go` | Thanos uses Prometheus discovery for finding store endpoints and query targets dynamically |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/query/endpointset.go`

</details>

### 80. OBS_TC010

**Source:** `prometheus/prometheus` / `tsdb/compact.go`
**Change type:** interface_modification
**Change:** Add `CompactWithTombstones(ctx context.Context, blocks []BlockMeta, tombstones Tombstones) (ulid.ULID, error)` to Compactor interface
**Repos involved:** 3 | **Affected files:** 5

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| thanos | `compact.go`, `planner.go` | Thanos compactor implements the Prometheus Compactor interface for cross-replica block compaction and downsampling |
| mimir | `compactor.go`, `split_merge_compactor.go`, `bucket_compactor.go` | Mimir's split-merge and bucket compactors implement the Prometheus Compactor interface for horizontally-scalable compact |

<details>
<summary>Full file paths</summary>

**thanos-io/thanos:**
- `pkg/compact/compact.go`
- `pkg/compact/planner.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
- `pkg/compactor/bucket_compactor.go`

</details>

### 81. OBS_TC011

**Source:** `open-telemetry/opentelemetry-collector` / `component/component.go`
**Change type:** interface_modification
**Change:** Add `Capabilities() ComponentCapabilities` method to Component interface
**Repos involved:** 4 | **Affected files:** 7

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `prometheus.go`, `factory.go`, `trace_receiver.go`, `factory.go` | Every exporter and receiver in otel-contrib implements the Component interface and must add the new Capabilities method |
| jaeger | `extension.go`, `exporter.go` | Jaeger v2 is built on OTel Collector and its storage extension and exporter implement Component |
| tempo | `main.go` | Tempo embeds OTel Collector receiver components for trace ingestion |

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
- `cmd/tempo/main.go`

</details>

### 82. OBS_TC012

**Source:** `open-telemetry/opentelemetry-collector` / `consumer/metrics.go`
**Change type:** interface_modification
**Change:** Add `ConsumeMetricsWithContext` method to Metrics consumer interface
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `prometheus.go`, `collector.go` | Prometheus exporter implements Metrics consumer to convert and expose OTel metrics |
| jaeger | `command.go` | Jaeger's span-metrics connector uses the Metrics consumer interface for derived metrics |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/prometheus.go`
- `exporter/prometheusexporter/collector.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/command.go`

</details>

### 83. OBS_TC013

**Source:** `open-telemetry/opentelemetry-collector` / `exporter/exporter.go`
**Change type:** struct_field_change
**Change:** Add `RetryConfig RetrySettings` field to exporter.Settings struct
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `factory.go`, `prometheus.go` | Prometheus exporter factory creates exporter using Settings and must include the new RetryConfig field |
| jaeger | `exporter.go` | Jaeger storage exporter constructs exporter.Settings when initializing the trace storage pipeline |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/factory.go`
- `exporter/prometheusexporter/prometheus.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/exporters/storageexporter/exporter.go`

</details>

### 84. OBS_TC014

**Source:** `open-telemetry/opentelemetry-collector` / `receiver/receiver.go`
**Change type:** method_signature_change
**Change:** Add `logger *zap.Logger` parameter to CreateTraces factory function signature
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `factory.go`, `trace_receiver.go` | Jaeger receiver factory implements CreateTraces and must add the logger parameter |
| jaeger | `command.go` | Jaeger v2 configures receiver factories and calls CreateTraces during pipeline initialization |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/factory.go`
- `receiver/jaegerreceiver/trace_receiver.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/command.go`

</details>

### 85. OBS_TC015

**Source:** `open-telemetry/opentelemetry-collector` / `component/config.go`
**Change type:** interface_modification
**Change:** Replace `Validate() error` with `ValidateWithContext(ctx context.Context) error` on Config interface
**Repos involved:** 4 | **Affected files:** 5

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `config.go`, `config.go` | Every contrib component config implements Validate() and must migrate to ValidateWithContext() |
| jaeger | `extension.go`, `config.go` | Jaeger extension configs implement component.Config.Validate() for storage and query configuration |
| tempo | `main.go` | Tempo uses OTel Collector config validation for its embedded receiver components |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/config.go`
- `receiver/jaegerreceiver/config.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
- `cmd/jaeger/internal/extension/jaegerquery/config.go`
**grafana/tempo:**
- `cmd/tempo/main.go`

</details>

### 86. OBS_TC016

**Source:** `open-telemetry/opentelemetry-collector` / `component/identifiable.go`
**Change type:** type_change
**Change:** Change `type ID struct { typeVal Type; nameVal string }` to opaque type with constructors only
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `factory.go`, `factory.go` | Every contrib factory constructs component.ID for registration and must use new constructor functions |
| jaeger | `extension.go`, `command.go` | Jaeger constructs component.ID for its storage and query extensions during pipeline setup |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/factory.go`
- `receiver/jaegerreceiver/factory.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
- `cmd/jaeger/internal/command.go`

</details>

### 87. OBS_TC017

**Source:** `open-telemetry/opentelemetry-collector` / `consumer/consumererror/error.go`
**Change type:** type_change
**Change:** Change consumererror to struct with `FailedData interface{}` field instead of simple error wrapper
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `prometheus.go`, `accumulator.go` | Prometheus exporter handles consumer errors during metric conversion and must adapt to new error structure |
| jaeger | `exporter.go` | Jaeger storage exporter handles consumer errors for trace write failures |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/prometheus.go`
- `exporter/prometheusexporter/accumulator.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/exporters/storageexporter/exporter.go`

</details>

### 88. OBS_TC018

**Source:** `open-telemetry/opentelemetry-collector` / `component/host.go`
**Change type:** interface_modification
**Change:** Add `GetExtension(id ID) (Component, bool)` method to Host interface
**Repos involved:** 3 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `trace_receiver.go` | Jaeger receiver accesses Host to look up authentication extensions during initialization |
| jaeger | `extension.go`, `config.go` | Jaeger storage and query extensions use Host.GetFactory to find storage backends and must adapt to GetExtension |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/trace_receiver.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
- `cmd/jaeger/internal/extension/jaegerquery/config.go`

</details>

### 89. OBS_TC019

**Source:** `thanos-io/thanos` / `pkg/store/bucket.go`
**Change type:** interface_modification
**Change:** Add `SyncWithCallback(ctx context.Context, cb func(meta *metadata.Meta)) error` to BucketStore
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `bucket_compactor.go`, `bucketindex.go` | Mimir's bucket compactor wraps Thanos BucketStore for distributed block management |
| loki | `s3.go`, `gcs.go` | Loki uses Thanos objstore bucket abstraction for log chunk storage backends |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/compactor/bucket_compactor.go`
- `pkg/storage/tsdb/bucketindex/bucketindex.go`
**grafana/loki:**
- `pkg/storage/bucket/s3/s3.go`
- `pkg/storage/bucket/gcs/gcs.go`

</details>

### 90. OBS_TC020

**Source:** `thanos-io/thanos` / `pkg/compact/compact.go`
**Change type:** interface_modification
**Change:** Add `CompactWithDeletionMarkers(ctx context.Context, markers []DeletionMark) error` to Syncer
**Repos involved:** 2 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `compactor.go`, `split_merge_compactor.go`, `job.go` | Mimir's compactor uses Thanos Syncer for coordinating multi-tenant compaction with deletion markers |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
- `pkg/compactor/job.go`

</details>

### 91. OBS_TC021

**Source:** `thanos-io/thanos` / `pkg/query/querier.go`
**Change type:** method_signature_change
**Change:** Add `skipChunks bool` parameter to QueryableCreator function signature
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| grafana | `prometheus_metrics_middleware.go` | Grafana's Prometheus datasource proxies to Thanos query endpoints and constructs query parameters |
| mimir | `compactor.go` | Mimir query-frontend wraps Thanos QueryableCreator for query fanout across ingesters and store-gateways |

<details>
<summary>Full file paths</summary>

**grafana/grafana:**
- `pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go`
**grafana/mimir:**
- `pkg/compactor/compactor.go`

</details>

### 92. OBS_TC022

**Source:** `thanos-io/thanos` / `pkg/compact/planner.go`
**Change type:** interface_modification
**Change:** Add `PlanWithFilter` method to Planner interface
**Repos involved:** 2 | **Affected files:** 3

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `compactor.go`, `split_merge_compactor.go`, `split_merge_job.go` | Mimir implements Thanos Planner interface for tenant-aware block planning with split-merge strategy |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/compactor/compactor.go`
- `pkg/compactor/split_merge_compactor.go`
- `pkg/compactor/split_merge_job.go`

</details>

### 93. OBS_TC023

**Source:** `grafana/grafana` / `pkg/apis/datasource/v0alpha1/types.go`
**Change type:** struct_field_change
**Change:** Add `AuthConfig AuthenticationConfig` field to DataSourceConnection struct
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| loki | `ruler.go` | Loki's Grafana integration constructs DataSourceConnection for ruler-to-Grafana callbacks |
| tempo | `main.go` | Tempo query service uses Grafana datasource connection types for trace search API integration |

<details>
<summary>Full file paths</summary>

**grafana/loki:**
- `pkg/ruler/ruler.go`
**grafana/tempo:**
- `cmd/tempo-query/main.go`

</details>

### 94. OBS_TC024

**Source:** `grafana/grafana` / `pkg/registry/apps/alerting/rules/alertrule/storage.go`
**Change type:** interface_modification
**Change:** Add `ListByDatasource(ctx context.Context, dsUID string) ([]AlertRule, error)` to alert rule storage
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| mimir | `alertmanager.go`, `config.go` | Mimir alertmanager integrates with Grafana alerting for ruler rule management |
| loki | `ruler.go`, `config.go` | Loki ruler integrates with Grafana alerting for log-based alert rules |

<details>
<summary>Full file paths</summary>

**grafana/mimir:**
- `pkg/alertmanager/alertmanager.go`
- `pkg/alertmanager/config.go`
**grafana/loki:**
- `pkg/ruler/ruler.go`
- `pkg/ruler/config.go`

</details>

### 95. OBS_TC025

**Source:** `grafana/grafana` / `pkg/tsdb/loki/standalone/datasource.go`
**Change type:** method_signature_change
**Change:** Add `stream bool` parameter to QueryData method
**Repos involved:** 2 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| loki | `ruler.go`, `evaluator_remote.go` | Loki's remote evaluator implements the datasource query interface for ruler queries from Grafana |

<details>
<summary>Full file paths</summary>

**grafana/loki:**
- `pkg/ruler/ruler.go`
- `pkg/ruler/evaluator_remote.go`

</details>

### 96. OBS_TC026

**Source:** `grafana/grafana` / `pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go`
**Change type:** interface_modification
**Change:** Replace `prometheus.Registerer` parameter with `MetricsCollector` interface in middleware constructor
**Repos involved:** 3 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| prometheus | `config.go` | Prometheus config initialization uses the HTTP client provider middleware for scrape target connections |
| thanos | `endpointset.go` | Thanos endpoint discovery uses HTTP client middleware for store endpoint health checking |

<details>
<summary>Full file paths</summary>

**prometheus/prometheus:**
- `config/config.go`
**thanos-io/thanos:**
- `pkg/query/endpointset.go`

</details>

### 97. OBS_TC027

**Source:** `jaegertracing/jaeger` / `cmd/jaeger/internal/extension/jaegerstorage/extension.go`
**Change type:** interface_modification
**Change:** Add `GetArchiveStorage(ctx context.Context) (tracestorage.Reader, tracestorage.Writer, error)` to StorageExtension
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `trace_receiver.go`, `factory.go` | Jaeger receiver in otel-contrib looks up Jaeger storage extensions for trace persistence |
| tempo | `storage.pb.go`, `main.go` | Tempo's Jaeger query compatibility layer implements Jaeger storage interfaces for trace search |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/trace_receiver.go`
- `receiver/jaegerreceiver/factory.go`
**grafana/tempo:**
- `cmd/tempo-query/jaeger/storage_v1/storage.pb.go`
- `cmd/tempo-query/main.go`

</details>

### 98. OBS_TC028

**Source:** `jaegertracing/jaeger` / `cmd/jaeger/internal/exporters/storageexporter/exporter.go`
**Change type:** struct_field_change
**Change:** Add `BatchConfig BatchSettings` field to storageExporter struct
**Repos involved:** 2 | **Affected files:** 2

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `trace_receiver.go`, `config.go` | Jaeger receiver in otel-contrib integrates with the storage exporter for end-to-end trace pipeline |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `receiver/jaegerreceiver/trace_receiver.go`
- `receiver/jaegerreceiver/config.go`

</details>

### 99. OBS_TC029

**Source:** `open-telemetry/opentelemetry-collector-contrib` / `exporter/prometheusexporter/accumulator.go`
**Change type:** interface_modification
**Change:** Change return type of `Accumulate(metrics pmetric.Metrics)` from `int` to `[]AccumulatedMetric`
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| opentelemetry-collector-contrib | `collector.go`, `prometheus.go` | Prometheus collector calls Accumulate and must handle the new AccumulatedMetric return type |
| jaeger | `command.go` | Jaeger uses Prometheus exporter for span metrics pipeline and reads accumulated metric data |
| grafana | `prometheus_flavor.go` | Grafana ingests OTLP metrics via Prometheus exporter compatibility and reads accumulated metrics |

<details>
<summary>Full file paths</summary>

**open-telemetry/opentelemetry-collector-contrib:**
- `exporter/prometheusexporter/collector.go`
- `exporter/prometheusexporter/prometheus.go`
**jaegertracing/jaeger:**
- `cmd/jaeger/internal/command.go`
**grafana/grafana:**
- `pkg/infra/usagestats/statscollector/prometheus_flavor.go`

</details>

### 100. OBS_TC030

**Source:** `open-telemetry/opentelemetry-collector-contrib` / `receiver/jaegerreceiver/trace_receiver.go`
**Change type:** struct_field_change
**Change:** Add `SamplingConfig SamplingStrategy` field to jReceiver struct
**Repos involved:** 3 | **Affected files:** 4

| Affected Repo | Files | Reason |
|--------------|-------|--------|
| jaeger | `command.go`, `config.go` | Jaeger v2 uses the Jaeger receiver as its primary trace ingestion path and configures it during pipeline setup |
| tempo | `main.go`, `main.go` | Tempo uses the Jaeger receiver for backward-compatible Jaeger protocol trace ingestion |

<details>
<summary>Full file paths</summary>

**jaegertracing/jaeger:**
- `cmd/jaeger/internal/command.go`
- `cmd/jaeger/internal/extension/jaegerquery/config.go`
**grafana/tempo:**
- `cmd/tempo/main.go`
- `cmd/tempo-query/main.go`

</details>

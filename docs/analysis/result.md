br_inf Analysis — grafana-operator Top 10
Rank	File	BR1 (Direct)	BR-inf	Role
1	api/v1beta1/grafana_types.go	~30	CRITICAL	Root Grafana CRD schema — everything imports this
2	controllers/controller_shared.go	~11	CRITICAL	GetScopedMatchingInstances() — used by every resource controller
3	controllers/client/grafana_client.go	~15	VERY HIGH	Grafana API client hub — all cross-cluster API calls route through this
4	controllers/grafana_controller.go	~12	VERY HIGH	Main reconciler — orchestrates all 10+ sub-reconcilers
5	api/v1beta1/common.go	~13	VERY HIGH	CommonResource interface + GrafanaCommonSpec — embedded in all 12 CRD types
6	controllers/resources/resources.go	~12	HIGH	Kubernetes object factory (Deployments, Services, ConfigMaps)
7	controllers/client/auth.go	~5 (+transitive)	HIGH	Credential/secret resolution — all API auth flows
8	api/v1beta1/plugins.go	~8	MED-HIGH	Plugin config types — imported by grafana_types.go and provisioner
9	api/v1beta1/content.go	~9	MED-HIGH	GrafanaContentSpec — used by all dashboard/library-panel fetchers
10	controllers/patch.go	~6	MEDIUM	JSON patch execution — affects all post-deploy resource modification flows

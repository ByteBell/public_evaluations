#!/usr/bin/env python3
"""Replace CRW_TC042-TC071 with 30 new observability cross-repo questions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CROSS_REPO = ROOT / "cross_repo_whole.json"

with open(CROSS_REPO) as f:
    data = json.load(f)

# Remove CRW_TC042 through CRW_TC071
remove_ids = {f"CRW_TC{i:03d}" for i in range(42, 72)}
kept = [tc for tc in data["test_cases"] if tc["id"] not in remove_ids]
removed_count = len(data["test_cases"]) - len(kept)
print(f"Removed {removed_count} CRW questions (expected 30)")

# 30 new observability questions
obs_questions = [
    # === Prometheus as source (10) ===
    {
        "id": "OBS_TC001",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "storage/interface.go",
            "change_type": "interface_modification",
            "description": "Add a new method SelectSorted(ctx context.Context, hints *SelectHints, matchers ...*labels.Matcher) SeriesSet to the Querier interface in prometheus/storage. Querier is the core read interface used by Thanos StoreAPI and Mimir query-frontend to evaluate PromQL queries against time-series data. Any type implementing Querier must now satisfy this additional method.",
            "specific_change": "Add `SelectSorted(ctx context.Context, hints *SelectHints, matchers ...*labels.Matcher) SeriesSet` method to Querier interface"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/store/bucket.go",
                    "pkg/query/querier.go",
                    "pkg/query/iter.go"
                ],
                "reason": "Thanos BucketStore and query layer implement the Prometheus Querier interface to serve time-series data over gRPC StoreAPI"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/storage/tsdb/bucketindex/bucketindex.go"
                ],
                "reason": "Mimir's compactor and TSDB bucket index layer use Prometheus storage.Querier for block-level queries during compaction"
            }
        ]
    },
    {
        "id": "OBS_TC002",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "model/labels/labels_common.go",
            "change_type": "type_change",
            "description": "Change the Labels type from a sorted slice of Label structs to a new named struct with private fields and accessor methods. Labels is the fundamental type used across the entire observability stack to represent metric label sets. Any code that directly iterates, indexes, or constructs Labels as a slice will break.",
            "specific_change": "Change `type Labels []Label` to `type Labels struct { data []Label }` with accessor methods"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/store/bucket.go",
                    "pkg/store/lazy_postings.go",
                    "pkg/query/querier.go"
                ],
                "reason": "Thanos store and query packages directly construct and iterate prometheus labels.Labels for series matching and deduplication"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/split_merge_compactor.go"
                ],
                "reason": "Mimir compactor uses labels.Labels for block-level label filtering and split-merge operations"
            },
            {
                "repo": "grafana/loki",
                "files": [
                    "pkg/ruler/ruler.go",
                    "pkg/ruler/rulestore/store.go"
                ],
                "reason": "Loki ruler uses prometheus labels.Labels for recording rule evaluation and label manipulation"
            },
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/accumulator.go",
                    "exporter/prometheusexporter/collector.go"
                ],
                "reason": "OTel Prometheus exporter converts OpenTelemetry metrics to Prometheus format using labels.Labels"
            }
        ]
    },
    {
        "id": "OBS_TC003",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "model/histogram/histogram.go",
            "change_type": "struct_field_change",
            "description": "Add a new required field CreatedTimestamp int64 to the Histogram struct in prometheus/model/histogram. Histogram is the native histogram representation used by Prometheus TSDB and consumed by Thanos and Mimir for storage and query. Any code that constructs Histogram literals will break due to the new required field.",
            "specific_change": "Add `CreatedTimestamp int64` field to Histogram struct"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/store/bucket.go",
                    "pkg/compact/compact.go"
                ],
                "reason": "Thanos store and compactor handle native histograms from Prometheus TSDB blocks, constructing and reading Histogram structs"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/bucket_compactor.go"
                ],
                "reason": "Mimir compactor processes native histogram data during block compaction, constructing Histogram instances"
            }
        ]
    },
    {
        "id": "OBS_TC004",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "tsdb/db.go",
            "change_type": "method_signature_change",
            "description": "Change the DB.Querier method signature from Querier(mint, maxt int64) (storage.Querier, error) to Querier(ctx context.Context, mint, maxt int64) (storage.Querier, error) by adding a context parameter. DB is the main TSDB entry point used by Thanos sidecar and Mimir ingester for local time-series storage. All callers must pass a context.",
            "specific_change": "Add `ctx context.Context` as first parameter to `DB.Querier(mint, maxt int64)` method"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/store/bucket.go",
                    "pkg/query/querier.go"
                ],
                "reason": "Thanos calls DB.Querier to read local TSDB data through the sidecar component"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/storage/tsdb/bucketindex/bucketindex.go"
                ],
                "reason": "Mimir ingester and compactor call DB.Querier for local TSDB reads and compaction queries"
            }
        ]
    },
    {
        "id": "OBS_TC005",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "promql/engine.go",
            "change_type": "interface_modification",
            "description": "Add a new method ExplainQuery(ctx context.Context, qs string) (*QueryPlan, error) to the QueryEngine interface in promql. QueryEngine is used by Thanos query frontend for distributed PromQL evaluation and by Grafana for direct Prometheus queries. All implementations must add this method.",
            "specific_change": "Add `ExplainQuery(ctx context.Context, qs string) (*QueryPlan, error)` method to QueryEngine"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/query/querier.go",
                    "pkg/query/remote_engine.go"
                ],
                "reason": "Thanos query layer wraps the Prometheus PromQL engine for distributed query evaluation and must implement any new engine interface methods"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go"
                ],
                "reason": "Mimir query-frontend uses Prometheus PromQL engine for query splitting and must satisfy the engine interface"
            },
            {
                "repo": "grafana/grafana",
                "files": [
                    "pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go"
                ],
                "reason": "Grafana's Prometheus datasource wraps the PromQL engine for query execution and metrics collection"
            }
        ]
    },
    {
        "id": "OBS_TC006",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "storage/interface_append.go",
            "change_type": "interface_modification",
            "description": "Add a new method AppendCTZeroSample(ref SeriesRef, l labels.Labels, t, ct int64) (SeriesRef, error) to the Appender interface in prometheus/storage. Appender is used by all components that write time-series data including remote write receivers, OTLP-to-Prometheus converters, and Mimir distributors. All implementations must add this method.",
            "specific_change": "Add `AppendCTZeroSample(ref SeriesRef, l labels.Labels, t, ct int64) (SeriesRef, error)` to Appender interface"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/store/bucket.go",
                    "pkg/compact/compact.go"
                ],
                "reason": "Thanos receive component implements storage.Appender for ingesting remote-write data from Prometheus instances"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/bucket_compactor.go"
                ],
                "reason": "Mimir distributor implements storage.Appender for ingesting samples from Prometheus remote-write"
            },
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/prometheus.go",
                    "exporter/prometheusexporter/accumulator.go"
                ],
                "reason": "OTel Prometheus exporter uses storage.Appender to write converted OTLP metrics into Prometheus format"
            }
        ]
    },
    {
        "id": "OBS_TC007",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "config/config.go",
            "change_type": "struct_field_change",
            "description": "Change the ScrapeInterval field in GlobalConfig from model.Duration to a new typed Duration with validation constraints. GlobalConfig is embedded by Thanos, Mimir, and Grafana for configuring Prometheus-compatible scrape and evaluation intervals. Any code that assigns model.Duration values to ScrapeInterval will break.",
            "specific_change": "Change `ScrapeInterval model.Duration` to `ScrapeInterval ValidatedDuration` in GlobalConfig"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/query/querier.go",
                    "pkg/compact/compact.go"
                ],
                "reason": "Thanos ruler and query components read GlobalConfig.ScrapeInterval for step alignment in range queries"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go"
                ],
                "reason": "Mimir ruler embeds Prometheus GlobalConfig for rule evaluation interval configuration"
            },
            {
                "repo": "grafana/grafana",
                "files": [
                    "pkg/infra/usagestats/statscollector/prometheus_flavor.go"
                ],
                "reason": "Grafana reads Prometheus GlobalConfig to detect scrape configuration for usage statistics"
            }
        ]
    },
    {
        "id": "OBS_TC008",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "model/labels/matcher.go",
            "change_type": "type_change",
            "description": "Change the Matcher struct to use a compiled regex cache instead of re-compiling on each match. Change the Matches(v string) bool method signature to Matches(v string) (bool, error) to surface regex compilation errors. Matcher is used across the entire observability stack for label filtering in queries and alerting rules.",
            "specific_change": "Change `Matches(v string) bool` to `Matches(v string) (bool, error)` on Matcher"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/store/bucket.go",
                    "pkg/store/cache/filter_cache.go"
                ],
                "reason": "Thanos store uses labels.Matcher.Matches for filtering series during store queries"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/split_merge_compactor.go"
                ],
                "reason": "Mimir uses Matcher for label-based series filtering during compaction and query evaluation"
            },
            {
                "repo": "grafana/loki",
                "files": [
                    "pkg/ruler/ruler.go",
                    "pkg/ruler/base/ruler.go"
                ],
                "reason": "Loki ruler evaluates recording rules using Prometheus label matchers for log-to-metric conversion"
            }
        ]
    },
    {
        "id": "OBS_TC009",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "discovery/discovery.go",
            "change_type": "interface_modification",
            "description": "Add a new method HealthCheck(ctx context.Context) error to the Discoverer interface in prometheus/discovery. Discoverer is used by Thanos and Prometheus to find scrape targets dynamically. Any custom service discovery implementation must now implement HealthCheck.",
            "specific_change": "Add `HealthCheck(ctx context.Context) error` method to Discoverer interface"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/query/endpointset.go"
                ],
                "reason": "Thanos uses Prometheus discovery for finding store endpoints and query targets dynamically"
            }
        ]
    },
    {
        "id": "OBS_TC010",
        "source_change": {
            "repo": "prometheus/prometheus",
            "file": "tsdb/compact.go",
            "change_type": "interface_modification",
            "description": "Add a new method CompactWithTombstones(ctx context.Context, blocks []BlockMeta, tombstones Tombstones) (ulid.ULID, error) to the Compactor interface in prometheus/tsdb. Compactor is used by Thanos and Mimir for multi-block compaction. All implementations must support tombstone-aware compaction.",
            "specific_change": "Add `CompactWithTombstones(ctx context.Context, blocks []BlockMeta, tombstones Tombstones) (ulid.ULID, error)` to Compactor interface"
        },
        "expected_affected_files": [
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/compact/compact.go",
                    "pkg/compact/planner.go"
                ],
                "reason": "Thanos compactor implements the Prometheus Compactor interface for cross-replica block compaction and downsampling"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/split_merge_compactor.go",
                    "pkg/compactor/bucket_compactor.go"
                ],
                "reason": "Mimir's split-merge and bucket compactors implement the Prometheus Compactor interface for horizontally-scalable compaction"
            }
        ]
    },
    # === OpenTelemetry Collector as source (8) ===
    {
        "id": "OBS_TC011",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "component/component.go",
            "change_type": "interface_modification",
            "description": "Add a new method Capabilities() ComponentCapabilities to the Component interface in go.opentelemetry.io/collector/component. Component is the base interface for all OTel Collector plugins (receivers, exporters, processors, connectors). Jaeger v2 and Tempo both embed the collector as their core pipeline. Every plugin across otel-contrib must implement this method.",
            "specific_change": "Add `Capabilities() ComponentCapabilities` method to Component interface"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/prometheus.go",
                    "exporter/prometheusexporter/factory.go",
                    "receiver/jaegerreceiver/trace_receiver.go",
                    "receiver/jaegerreceiver/factory.go"
                ],
                "reason": "Every exporter and receiver in otel-contrib implements the Component interface and must add the new Capabilities method"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/extension/jaegerstorage/extension.go",
                    "cmd/jaeger/internal/exporters/storageexporter/exporter.go"
                ],
                "reason": "Jaeger v2 is built on OTel Collector and its storage extension and exporter implement Component"
            },
            {
                "repo": "grafana/tempo",
                "files": [
                    "cmd/tempo/main.go"
                ],
                "reason": "Tempo embeds OTel Collector receiver components for trace ingestion"
            }
        ]
    },
    {
        "id": "OBS_TC012",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "consumer/metrics.go",
            "change_type": "interface_modification",
            "description": "Add a new method ConsumeMetricsWithContext(ctx context.Context, md pmetric.Metrics, opts ...ConsumeOption) error to the Metrics consumer interface. This interface is implemented by all metric processors and exporters in the OTel Collector pipeline. Jaeger uses it for span metrics.",
            "specific_change": "Add `ConsumeMetricsWithContext` method to Metrics consumer interface"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/prometheus.go",
                    "exporter/prometheusexporter/collector.go"
                ],
                "reason": "Prometheus exporter implements Metrics consumer to convert and expose OTel metrics"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/command.go"
                ],
                "reason": "Jaeger's span-metrics connector uses the Metrics consumer interface for derived metrics"
            }
        ]
    },
    {
        "id": "OBS_TC013",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "exporter/exporter.go",
            "change_type": "struct_field_change",
            "description": "Add a required field RetryConfig RetrySettings to the exporter.Settings struct. Every exporter factory in otel-contrib and Jaeger receives Settings when creating exporter instances. All callers constructing Settings literals will break.",
            "specific_change": "Add `RetryConfig RetrySettings` field to exporter.Settings struct"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/factory.go",
                    "exporter/prometheusexporter/prometheus.go"
                ],
                "reason": "Prometheus exporter factory creates exporter using Settings and must include the new RetryConfig field"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/exporters/storageexporter/exporter.go"
                ],
                "reason": "Jaeger storage exporter constructs exporter.Settings when initializing the trace storage pipeline"
            }
        ]
    },
    {
        "id": "OBS_TC014",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "receiver/receiver.go",
            "change_type": "method_signature_change",
            "description": "Change the CreateTraces receiver factory function signature to include a new logger parameter: CreateTraces(ctx context.Context, set Settings, cfg component.Config, logger *zap.Logger, next consumer.Traces) (Traces, error). All receiver factories must update their signatures.",
            "specific_change": "Add `logger *zap.Logger` parameter to CreateTraces factory function signature"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "receiver/jaegerreceiver/factory.go",
                    "receiver/jaegerreceiver/trace_receiver.go"
                ],
                "reason": "Jaeger receiver factory implements CreateTraces and must add the logger parameter"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/command.go"
                ],
                "reason": "Jaeger v2 configures receiver factories and calls CreateTraces during pipeline initialization"
            }
        ]
    },
    {
        "id": "OBS_TC015",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "component/config.go",
            "change_type": "interface_modification",
            "description": "Add a new method ValidateWithContext(ctx context.Context) error to the Config interface, replacing the existing Validate() error method. Every component config across the OTel ecosystem must implement context-aware validation.",
            "specific_change": "Replace `Validate() error` with `ValidateWithContext(ctx context.Context) error` on Config interface"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/config.go",
                    "receiver/jaegerreceiver/config.go"
                ],
                "reason": "Every contrib component config implements Validate() and must migrate to ValidateWithContext()"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/extension/jaegerstorage/extension.go",
                    "cmd/jaeger/internal/extension/jaegerquery/config.go"
                ],
                "reason": "Jaeger extension configs implement component.Config.Validate() for storage and query configuration"
            },
            {
                "repo": "grafana/tempo",
                "files": [
                    "cmd/tempo/main.go"
                ],
                "reason": "Tempo uses OTel Collector config validation for its embedded receiver components"
            }
        ]
    },
    {
        "id": "OBS_TC016",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "component/identifiable.go",
            "change_type": "type_change",
            "description": "Change the component.ID type from a struct with Type and Name string fields to a new opaque type with only accessor methods. ID is used everywhere in the OTel Collector for identifying pipeline components. Any code that constructs ID literals or accesses fields directly will break.",
            "specific_change": "Change `type ID struct { typeVal Type; nameVal string }` to opaque type with constructors only"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/factory.go",
                    "receiver/jaegerreceiver/factory.go"
                ],
                "reason": "Every contrib factory constructs component.ID for registration and must use new constructor functions"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/extension/jaegerstorage/extension.go",
                    "cmd/jaeger/internal/command.go"
                ],
                "reason": "Jaeger constructs component.ID for its storage and query extensions during pipeline setup"
            }
        ]
    },
    {
        "id": "OBS_TC017",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "consumer/consumererror/error.go",
            "change_type": "type_change",
            "description": "Change the consumererror type from wrapping a simple error to a structured ErrorData type that includes the failed data (metrics/traces/logs) for retry. Any code that type-asserts or unwraps consumer errors will break.",
            "specific_change": "Change consumererror to struct with `FailedData interface{}` field instead of simple error wrapper"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/prometheus.go",
                    "exporter/prometheusexporter/accumulator.go"
                ],
                "reason": "Prometheus exporter handles consumer errors during metric conversion and must adapt to new error structure"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/exporters/storageexporter/exporter.go"
                ],
                "reason": "Jaeger storage exporter handles consumer errors for trace write failures"
            }
        ]
    },
    {
        "id": "OBS_TC018",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector",
            "file": "component/host.go",
            "change_type": "interface_modification",
            "description": "Add a new method GetExtension(id ID) (Component, bool) to the Host interface. Host provides access to the collector's shared resources. Jaeger and contrib extensions use Host to look up other extensions (e.g., storage, auth). All Host implementations must add this method.",
            "specific_change": "Add `GetExtension(id ID) (Component, bool)` method to Host interface"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "receiver/jaegerreceiver/trace_receiver.go"
                ],
                "reason": "Jaeger receiver accesses Host to look up authentication extensions during initialization"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/extension/jaegerstorage/extension.go",
                    "cmd/jaeger/internal/extension/jaegerquery/config.go"
                ],
                "reason": "Jaeger storage and query extensions use Host.GetFactory to find storage backends and must adapt to GetExtension"
            }
        ]
    },
    # === Thanos as source (4) ===
    {
        "id": "OBS_TC019",
        "source_change": {
            "repo": "thanos-io/thanos",
            "file": "pkg/store/bucket.go",
            "change_type": "interface_modification",
            "description": "Add a new method SyncWithCallback(ctx context.Context, cb func(meta *metadata.Meta)) error to the BucketStore. BucketStore is the primary object-storage-backed store used by Mimir and Loki for reading historical time-series blocks. Any wrapper or mock must implement this method.",
            "specific_change": "Add `SyncWithCallback(ctx context.Context, cb func(meta *metadata.Meta)) error` to BucketStore"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/bucket_compactor.go",
                    "pkg/storage/tsdb/bucketindex/bucketindex.go"
                ],
                "reason": "Mimir's bucket compactor wraps Thanos BucketStore for distributed block management"
            },
            {
                "repo": "grafana/loki",
                "files": [
                    "pkg/storage/bucket/s3/s3.go",
                    "pkg/storage/bucket/gcs/gcs.go"
                ],
                "reason": "Loki uses Thanos objstore bucket abstraction for log chunk storage backends"
            }
        ]
    },
    {
        "id": "OBS_TC020",
        "source_change": {
            "repo": "thanos-io/thanos",
            "file": "pkg/compact/compact.go",
            "change_type": "interface_modification",
            "description": "Add a new method CompactWithDeletionMarkers(ctx context.Context, markers []DeletionMark) error to the Syncer in thanos/pkg/compact. Mimir's compactor embeds Thanos Syncer for multi-tenant block lifecycle management. This new method enables deletion-mark-aware compaction.",
            "specific_change": "Add `CompactWithDeletionMarkers(ctx context.Context, markers []DeletionMark) error` to Syncer"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/split_merge_compactor.go",
                    "pkg/compactor/job.go"
                ],
                "reason": "Mimir's compactor uses Thanos Syncer for coordinating multi-tenant compaction with deletion markers"
            }
        ]
    },
    {
        "id": "OBS_TC021",
        "source_change": {
            "repo": "thanos-io/thanos",
            "file": "pkg/query/querier.go",
            "change_type": "method_signature_change",
            "description": "Change the QueryableCreator function signature to accept an additional deduplication parameter: QueryableCreator(deduplicate bool, replicaLabels []string, storeMatchers [][]*labels.Matcher, maxResolution int64, partialResponse bool, skipChunks bool) storage.Queryable. This affects Grafana and Mimir which wrap Thanos query for federated queries.",
            "specific_change": "Add `skipChunks bool` parameter to QueryableCreator function signature"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/grafana",
                "files": [
                    "pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go"
                ],
                "reason": "Grafana's Prometheus datasource proxies to Thanos query endpoints and constructs query parameters"
            },
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go"
                ],
                "reason": "Mimir query-frontend wraps Thanos QueryableCreator for query fanout across ingesters and store-gateways"
            }
        ]
    },
    {
        "id": "OBS_TC022",
        "source_change": {
            "repo": "thanos-io/thanos",
            "file": "pkg/compact/planner.go",
            "change_type": "interface_modification",
            "description": "Add a new method PlanWithFilter(ctx context.Context, metasByMinTime []*metadata.Meta, filter func(*metadata.Meta) bool) ([]*metadata.Meta, error) to the Planner interface. Planner is used by Mimir for deciding which TSDB blocks to compact together.",
            "specific_change": "Add `PlanWithFilter` method to Planner interface"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/compactor/compactor.go",
                    "pkg/compactor/split_merge_compactor.go",
                    "pkg/compactor/split_merge_job.go"
                ],
                "reason": "Mimir implements Thanos Planner interface for tenant-aware block planning with split-merge strategy"
            }
        ]
    },
    # === Grafana as source (4) ===
    {
        "id": "OBS_TC023",
        "source_change": {
            "repo": "grafana/grafana",
            "file": "pkg/apis/datasource/v0alpha1/types.go",
            "change_type": "struct_field_change",
            "description": "Add a new required field AuthConfig AuthenticationConfig to the DataSourceConnection struct in Grafana's datasource API types. DataSourceConnection defines how Grafana connects to backends like Prometheus, Loki, Mimir, and Tempo. All datasource plugins constructing this struct will break.",
            "specific_change": "Add `AuthConfig AuthenticationConfig` field to DataSourceConnection struct"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/loki",
                "files": [
                    "pkg/ruler/ruler.go"
                ],
                "reason": "Loki's Grafana integration constructs DataSourceConnection for ruler-to-Grafana callbacks"
            },
            {
                "repo": "grafana/tempo",
                "files": [
                    "cmd/tempo-query/main.go"
                ],
                "reason": "Tempo query service uses Grafana datasource connection types for trace search API integration"
            }
        ]
    },
    {
        "id": "OBS_TC024",
        "source_change": {
            "repo": "grafana/grafana",
            "file": "pkg/registry/apps/alerting/rules/alertrule/storage.go",
            "change_type": "interface_modification",
            "description": "Add a new method ListByDatasource(ctx context.Context, dsUID string) ([]AlertRule, error) to the AlertRule storage interface. This interface is used by Mimir and Loki rulers for federated alert rule management through Grafana.",
            "specific_change": "Add `ListByDatasource(ctx context.Context, dsUID string) ([]AlertRule, error)` to alert rule storage"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/mimir",
                "files": [
                    "pkg/alertmanager/alertmanager.go",
                    "pkg/alertmanager/config.go"
                ],
                "reason": "Mimir alertmanager integrates with Grafana alerting for ruler rule management"
            },
            {
                "repo": "grafana/loki",
                "files": [
                    "pkg/ruler/ruler.go",
                    "pkg/ruler/config.go"
                ],
                "reason": "Loki ruler integrates with Grafana alerting for log-based alert rules"
            }
        ]
    },
    {
        "id": "OBS_TC025",
        "source_change": {
            "repo": "grafana/grafana",
            "file": "pkg/tsdb/loki/standalone/datasource.go",
            "change_type": "method_signature_change",
            "description": "Change the QueryData method signature in the Loki standalone datasource to accept a new streaming parameter: QueryData(ctx context.Context, req *backend.QueryDataRequest, stream bool) (*backend.QueryDataResponse, error). This affects Loki's query API compatibility.",
            "specific_change": "Add `stream bool` parameter to QueryData method"
        },
        "expected_affected_files": [
            {
                "repo": "grafana/loki",
                "files": [
                    "pkg/ruler/ruler.go",
                    "pkg/ruler/evaluator_remote.go"
                ],
                "reason": "Loki's remote evaluator implements the datasource query interface for ruler queries from Grafana"
            }
        ]
    },
    {
        "id": "OBS_TC026",
        "source_change": {
            "repo": "grafana/grafana",
            "file": "pkg/infra/httpclient/httpclientprovider/prometheus_metrics_middleware.go",
            "change_type": "interface_modification",
            "description": "Change the metrics middleware to use a new MetricsCollector interface instead of directly using prometheus.Registerer. Any component that registers HTTP client metrics through this middleware must implement MetricsCollector.",
            "specific_change": "Replace `prometheus.Registerer` parameter with `MetricsCollector` interface in middleware constructor"
        },
        "expected_affected_files": [
            {
                "repo": "prometheus/prometheus",
                "files": [
                    "config/config.go"
                ],
                "reason": "Prometheus config initialization uses the HTTP client provider middleware for scrape target connections"
            },
            {
                "repo": "thanos-io/thanos",
                "files": [
                    "pkg/query/endpointset.go"
                ],
                "reason": "Thanos endpoint discovery uses HTTP client middleware for store endpoint health checking"
            }
        ]
    },
    # === Jaeger as source (2) ===
    {
        "id": "OBS_TC027",
        "source_change": {
            "repo": "jaegertracing/jaeger",
            "file": "cmd/jaeger/internal/extension/jaegerstorage/extension.go",
            "change_type": "interface_modification",
            "description": "Add a new method GetArchiveStorage(ctx context.Context) (tracestorage.Reader, tracestorage.Writer, error) to the StorageExtension interface. This interface is used by OTel Collector contrib's Jaeger components and Tempo for Jaeger-compatible trace storage backends.",
            "specific_change": "Add `GetArchiveStorage(ctx context.Context) (tracestorage.Reader, tracestorage.Writer, error)` to StorageExtension"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "receiver/jaegerreceiver/trace_receiver.go",
                    "receiver/jaegerreceiver/factory.go"
                ],
                "reason": "Jaeger receiver in otel-contrib looks up Jaeger storage extensions for trace persistence"
            },
            {
                "repo": "grafana/tempo",
                "files": [
                    "cmd/tempo-query/jaeger/storage_v1/storage.pb.go",
                    "cmd/tempo-query/main.go"
                ],
                "reason": "Tempo's Jaeger query compatibility layer implements Jaeger storage interfaces for trace search"
            }
        ]
    },
    {
        "id": "OBS_TC028",
        "source_change": {
            "repo": "jaegertracing/jaeger",
            "file": "cmd/jaeger/internal/exporters/storageexporter/exporter.go",
            "change_type": "struct_field_change",
            "description": "Add a new required field BatchConfig BatchSettings to the storageExporter struct. This exporter is the bridge between OTel Collector pipeline and Jaeger storage backends. OTel contrib components that wrap or test this exporter will break.",
            "specific_change": "Add `BatchConfig BatchSettings` field to storageExporter struct"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "receiver/jaegerreceiver/trace_receiver.go",
                    "receiver/jaegerreceiver/config.go"
                ],
                "reason": "Jaeger receiver in otel-contrib integrates with the storage exporter for end-to-end trace pipeline"
            }
        ]
    },
    # === Cross-stack (2) ===
    {
        "id": "OBS_TC029",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector-contrib",
            "file": "exporter/prometheusexporter/accumulator.go",
            "change_type": "interface_modification",
            "description": "Change the metric accumulator to use a new AccumulatedMetric type instead of raw pmetric.Metric. The accumulator bridges OTel metrics to Prometheus exposition format and is used indirectly by Jaeger (for span metrics) and Grafana (for OTLP ingestion). Any code that reads accumulated metrics will break.",
            "specific_change": "Change return type of `Accumulate(metrics pmetric.Metrics)` from `int` to `[]AccumulatedMetric`"
        },
        "expected_affected_files": [
            {
                "repo": "open-telemetry/opentelemetry-collector-contrib",
                "files": [
                    "exporter/prometheusexporter/collector.go",
                    "exporter/prometheusexporter/prometheus.go"
                ],
                "reason": "Prometheus collector calls Accumulate and must handle the new AccumulatedMetric return type"
            },
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/command.go"
                ],
                "reason": "Jaeger uses Prometheus exporter for span metrics pipeline and reads accumulated metric data"
            },
            {
                "repo": "grafana/grafana",
                "files": [
                    "pkg/infra/usagestats/statscollector/prometheus_flavor.go"
                ],
                "reason": "Grafana ingests OTLP metrics via Prometheus exporter compatibility and reads accumulated metrics"
            }
        ]
    },
    {
        "id": "OBS_TC030",
        "source_change": {
            "repo": "open-telemetry/opentelemetry-collector-contrib",
            "file": "receiver/jaegerreceiver/trace_receiver.go",
            "change_type": "struct_field_change",
            "description": "Add a new required field SamplingConfig SamplingStrategy to the jReceiver struct. The Jaeger receiver is used by both Jaeger v2 (as its primary ingest path) and Tempo (for Jaeger protocol compatibility). Any code constructing or wrapping jReceiver will break.",
            "specific_change": "Add `SamplingConfig SamplingStrategy` field to jReceiver struct"
        },
        "expected_affected_files": [
            {
                "repo": "jaegertracing/jaeger",
                "files": [
                    "cmd/jaeger/internal/command.go",
                    "cmd/jaeger/internal/extension/jaegerquery/config.go"
                ],
                "reason": "Jaeger v2 uses the Jaeger receiver as its primary trace ingestion path and configures it during pipeline setup"
            },
            {
                "repo": "grafana/tempo",
                "files": [
                    "cmd/tempo/main.go",
                    "cmd/tempo-query/main.go"
                ],
                "reason": "Tempo uses the Jaeger receiver for backward-compatible Jaeger protocol trace ingestion"
            }
        ]
    },
]

# Insert new questions and rebuild test_cases
kept.extend(obs_questions)
data["test_cases"] = kept

# Update metadata
data["metadata"]["repo_set"].update({
    "A16": "prometheus/prometheus",
    "A17": "thanos-io/thanos",
    "A18": "grafana/grafana",
    "A19": "grafana/loki",
    "A20": "grafana/mimir",
    "A21": "grafana/tempo",
    "A22": "open-telemetry/opentelemetry-collector",
    "A23": "open-telemetry/opentelemetry-collector-contrib",
    "A24": "jaegertracing/jaeger",
    "A25": "open-telemetry/opentelemetry-operator",
})
data["metadata"]["description"] = (
    "100 cross-repository file-level impact test cases across 25 Kubernetes and observability repos"
)

# Recount distribution
tc_list = data["test_cases"]
dist = {"2_repo": 0, "3_repo": 0, "4_plus_repo": 0}
for tc in tc_list:
    repos = {tc["source_change"]["repo"]}
    for af in tc.get("expected_affected_files", []):
        repos.add(af["repo"])
    n = len(repos)
    if n == 2:
        dist["2_repo"] += 1
    elif n == 3:
        dist["3_repo"] += 1
    else:
        dist["4_plus_repo"] += 1
data["metadata"]["distribution"] = dist

# Write back
with open(CROSS_REPO, "w") as f:
    json.dump(data, f, indent=2, default=str)

print(f"Total test cases: {len(data['test_cases'])}")
print(f"Distribution: {dist}")
print(f"Repos in set: {len(data['metadata']['repo_set'])}")

# Verify OBS questions present
obs_ids = [tc["id"] for tc in data["test_cases"] if tc["id"].startswith("OBS_")]
print(f"OBS questions: {len(obs_ids)}")
print(f"OBS IDs: {obs_ids}")

# Verify removed CRW questions absent
remaining_crw = [tc["id"] for tc in data["test_cases"] if tc["id"].startswith("CRW_")]
print(f"Remaining CRW questions: {len(remaining_crw)}")

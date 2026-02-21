#!/usr/bin/env python3
"""Download all repositories for the Kubecluster dataset."""
import subprocess
import sys
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset" / "Kubecluster"

REPOS = {
    "argo-cd": "https://github.com/argoproj/argo-cd",
    "autoscaler": "https://github.com/kubernetes/autoscaler",
    "cert-manager": "https://github.com/cert-manager/cert-manager",
    "cilium": "https://github.com/cilium/cilium",
    "crossplane": "https://github.com/crossplane/crossplane",
    "external-dns": "https://github.com/kubernetes-sigs/external-dns",
    "external-secrets": "https://github.com/external-secrets/external-secrets",
    "flux2": "https://github.com/fluxcd/flux2",
    "gatekeeper": "https://github.com/open-policy-agent/gatekeeper",
    "grafana": "https://github.com/grafana/grafana",
    "helm": "https://github.com/helm/helm",
    "ingress-nginx": "https://github.com/kubernetes/ingress-nginx",
    "istio": "https://github.com/istio/istio",
    "jaeger": "https://github.com/jaegertracing/jaeger",
    "karpenter": "https://github.com/aws/karpenter-provider-aws",
    "kubernetes": "https://github.com/kubernetes/kubernetes",
    "kustomize": "https://github.com/kubernetes-sigs/kustomize",
    "loki": "https://github.com/grafana/loki",
    "mimir": "https://github.com/grafana/mimir",
    "opentelemetry-collector": "https://github.com/open-telemetry/opentelemetry-collector",
    "opentelemetry-collector-contrib": "https://github.com/open-telemetry/opentelemetry-collector-contrib",
    "opentelemetry-operator": "https://github.com/open-telemetry/opentelemetry-operator",
    "prometheus": "https://github.com/prometheus/prometheus",
    "tempo": "https://github.com/grafana/tempo",
    "thanos": "https://github.com/thanos-io/thanos",
}


def main():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    failed = []
    for name, url in sorted(REPOS.items()):
        dest = DATASET_DIR / name
        if dest.exists():
            print(f"[skip] {name} already exists")
            continue

        print(f"[clone] {name} <- {url}")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(dest)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[error] {name}: {result.stderr.strip()}", file=sys.stderr)
            failed.append(name)
        else:
            print(f"[done] {name}")

    print()
    if failed:
        print(f"Failed to clone: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All repositories cloned successfully.")


if __name__ == "__main__":
    main()

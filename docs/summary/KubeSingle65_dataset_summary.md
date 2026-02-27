# KubeSingle65 Dataset Summary

**Generated:** 2026-02-27

This document provides a comprehensive overview of the `KubeSingle65` dataset located at `results/KubeSingle65/meta.json`. The dataset was assembled following the guidelines defined in `docs/plans/new_becnhmark_plan.md` and draws exclusively on real Kubernetes pull requests.

---

## 1. Dataset Overview

- **Benchmark name:** `KubeSingle50` (mis‑nomer; contains 65 questions)
- **Repository under test:** `kubernetes/kubernetes`
- **Total questions:** 65
- **Creation date:** 2026‑02‑27

Each question corresponds to a single code change or observation extracted from a PR; metadata fields include:

1. `id` – unique identifier (`KSR_TC001` … `KSR_TC065`)
2. `type` – difficulty category (Black, Red, Orange, Yellow, Grey)
3. `pr` – originating pull request number
4. `module` – the symbol, file, or descriptive label affected
5. `source_file` – path to the file within the repo

The `note` field documents how questions were grouped into batches for construction:

> Batch 1 (TC001-TC006) from PR #137171. Batch 2 (TC007-TC012) from PR #137120. Batch 3 (TC013-TC017) from PR #137084. Batch 4 (TC018-TC029) from PR #136953 (Revert dv native in the validation-gen framework). Batch 5 (TC030-TC042) from PRs #136896 and #136793. Batch 6 (TC043-TC048) from PR #136619 (DRA allocator promote experimental->incubating->stable). Batch 7 (TC049-TC051) from PR #136613. Batch 8 (TC052) from PR #136793. Batch 9 (TC053-TC057) from PR #136574. Batch 10 (TC058-TC061) from PR #136284. Batch 11 (TC062-TC063) from PR #135675. Batch 12 (TC064-TC065) from PR #131068.


## 2. Distribution by Difficulty

| Category | Number |
|----------|:------:|
| Black    | 19     |
| Red      | 19     |
| Orange   | 12     |
| Yellow   | 8      |
| Grey     | 7      |



## 3. Breakdown by Pull Request

1. **PR 137171** – Introduced `nodedeclaredfeatures` package changes (6 questions:
   features, feature gate types, node configuration, match result). Difficulties span Black/Red/Orange.
2. **PR 137120** – Updates to `validation-gen` linter and `rbac/v1.Role` (6 Qs; Black/Red/Yellow).
3. **PR 137084** – Protobuf generator tweaks and build‑tagged stubs (5 Qs; Black/Red/Orange/Yellow/Grey).
4. **PR 136953** – Revert of `dv native` in validation‑gen; sizable cascade (12 Qs mostly Black/Red).
5. **PRs 136896 & 136793** – Mixed validation logic, REST config, and API spec changes (13 Qs).
6. **PR 136619** – Dynamic‑resource‑allocation (DRA) allocator promotion (6 Qs).
7. **PR 136613** – Scheduler preemption API (3 Qs).
8. **PR 136793** (again) – single Yellow item on `PodGroup`.
9. **PR 136574** – utility function logging additions and restmapper expanders (5 Qs).
10. **PR 136284** – another validation‑gen change (4 Qs).
11. **PR 135675** – peerproxy components (2 Qs).
12. **PR 131068** – sample‑controller API and controller code (2 Qs).


## 4. Content Highlights

- **Core API structures:** `ServiceSpec`, `StatefulSetSpec`, `PodFailurePolicyRule`, `Role`, `PodGroup`, controller sync handler.
- **Code‑generator / validation‑gen:** Recurring theme – many modules and symbols from `code-generator/cmd/validation-gen` appear.
- **Build‑tagged/conditional code:** several questions revolve around proto message stubs and build tags.
- **Infrastructure/utilities:** wsstream, utilnet, restmapper, preemption, dynamic resource allocator.
- **Deletions and removals:** entire files (e.g. `native.go`), tests, constants, private methods.


## 5. Strengths

- **Real‑world provenance** ensures relevance and verifiability.
- **Detailed metadata** allows for filtering, slicing, and tooling.
- **Cross‑package variety** provides broad coverage of Kubernetes components.
- **Batch documentation** makes replication or extension simple.


## 7. Usage Tips

- For evaluation, shuffle the dataset and sample per category to enforce balanced tests.
- Use the `source_file` paths to automatically fetch diff context when presenting questions to models.
- Cross‑reference PR numbers with GitHub to retrieve commit messages or review comments for richer context.

---

This summary captures every question and decision recorded in the meta file and provides critique and guidance for future dataset development. For further analysis, the accompanying Python utilities in `src/` (e.g. `evaluate.py`, `mcp_context_generation.py`) may be adapted to process `KubeSingle65`.

> ⚠️ *Note:* the benchmark name in `meta.json` remains `KubeSingle50` due to historical reasons; update it if consistency is desired.

---

*End of document.*
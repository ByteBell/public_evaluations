Now let me get the actual list of the 11 public repositories in SWE-bench Pro:Now I have everything. Here's the complete breakdown:

---

## SWE-bench Pro — Full Details

### What It Is

SWE-Bench Pro is a substantially more challenging benchmark created by Scale AI, containing 1,865 problems sourced from 41 actively maintained repositories spanning business applications, B2B services, and developer tools. Solutions average 107.4 lines of code across 4.1 files, making these significantly harder than standard SWE-bench tasks.

While most top models score over 70% on SWE-bench Verified, the best-performing models score only around 23% on SWE-bench Pro.

---

### Three Subsets

| Subset | Instances | Repos | Access |
|---|---|---|---|
| **Public** | 731 | 11 GPL repos | Fully open on HuggingFace |
| **Commercial (Private)** | 276 | 18 startup repos | Results only, code private |
| **Held-out** | 858 | 12 GPL repos | Fully private (overfitting check) |

---

### Download the Dataset (JSON)

The dataset is on HuggingFace at `ScaleAI/SWE-bench_Pro`:

```python
from datasets import load_dataset

# Load the full public dataset
dataset = load_dataset('ScaleAI/SWE-bench_Pro', split='test')

# Export to JSON
dataset.to_json('swe_bench_pro.json')
```

Or download directly from: **https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro**

---

### The 11 Public Repositories You Must Index

The 11 public repositories in SWE-bench Pro are:

| # | Repository | Language | Domain |
|---|---|---|---|
| 1 | **NodeBB/NodeBB** | JavaScript | Forum software |
| 2 | **ansible/ansible** | Python | DevOps/automation |
| 3 | **element-hq/element-web** | TypeScript/JS | Matrix chat client |
| 4 | **flipt-io/flipt** | Go | Feature flag platform |
| 5 | **future-architect/vuls** | Go | Vulnerability scanner |
| 6 | **gravitational/teleport** | Go | Infrastructure access |
| 7 | **internetarchive/openlibrary** | Python/JS | Online library platform |
| 8 | **navidrome/navidrome** | Go | Music streaming server |
| 9 | **protonmail/webclients** | TypeScript | ProtonMail web clients |
| 10 | **qutebrowser/qutebrowser** | Python | Keyboard-driven browser |
| 11 | **tutao/tutanota** | TypeScript | Encrypted email client |

All are licensed under **GPL or other copyleft licenses** by design.

---

### Dataset Schema (Per Instance)

The structure follows SWE-Bench Verified with extra fields:

```json
{
  "instance_id": "string",
  "repo": "owner/repo",
  "base_commit": "commit_hash",
  "problem_statement": "Issue description (human-augmented)",
  "patch": "Gold solution patch",
  "test_patch": "Test patch",
  "FAIL_TO_PASS": "[list of tests]",
  "PASS_TO_PASS": "[list of tests]",
  "dockerhub_tag": "tag for pre-built Docker image",
  // Additional Pro-specific fields:
  "requirements": "Human-written requirements",
  "interface": "Expected class/function names"
}
```

---

### Docker Images for Evaluation

Pre-built Docker images for each instance are on Docker Hub at `jefzda/sweap-images`:

```python
for row in dataset:
    instance_id = row['instance_id']
    docker_tag = row['dockerhub_tag']
    full_image = f"jefzda/sweap-images:{docker_tag}"
```

---

### Evaluation Code

**GitHub repo**: https://github.com/scaleapi/SWE-bench_Pro-os

To evaluate patches:

```bash
# Gather patches into JSON
python helper_code/gather_patches.py \
  --directory swe_bench_pro_results/sample1 \
  --prefix sample1 \
  --output sample1_patches.json

# Run evaluation
python swe_bench_pro_eval.py \
  --raw_sample_path=swe_bench_pro_full.csv \
  --patch_path=sample1_patches.json \
  --output_dir=output \
  --scripts_dir=run_scripts \
  --num_workers=100
```

---

### Key Links

| Resource | URL |
|---|---|
| HuggingFace Dataset | https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro |
| Evaluation Code | https://github.com/scaleapi/SWE-bench_Pro-os |
| Public Leaderboard | https://scale.com/leaderboard/swe_bench_pro_public |
| Paper | https://arxiv.org/abs/2509.16941 |
| Trajectory Explorer | https://docent.transluce.org/dashboard/032fb63d-4992-4bfc-911d-3b7dafcb931f |
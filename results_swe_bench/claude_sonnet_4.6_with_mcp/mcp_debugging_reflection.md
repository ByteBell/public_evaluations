# MCP-Assisted Debugging Reflection: astropy FITS Card Quote Bug

## What I Was Trying to Do

Diagnose and patch a bug in `astropy/io/fits/card.py` at commit `80c3854a5f4f4a6ab86c03d9db7854767fcd83c1`. The issue: double single-quotes (`''`) in long FITS card string values were sometimes silently truncated to a single quote (`'`) after a roundtrip through `Card.fromstring(str(card))`.

---

## Where I Got Stuck (and Why)

### 1. My mental model of `_words_group` was wrong

I kept tracing through `_words_group` expecting it to split cleanly on the escaped string. On paper, the split for `n=65` looked fine — `["x"*65 + "''"`, `"''"]`. Both pieces seemed to carry the right FITS-escaped quote pairs. My logic said: "join them, wrap in outer quotes, unescape → correct." But the bug is real, which means my trace was wrong somewhere.

The confusion came from `_words_group` operating on the **escaped** string (after `replace("'", "''")`), but the FITS card format has rules about where a string can legally be split. The function doesn't know about FITS string semantics — it just splits on spaces or at fixed widths. So it can split `''''` (two escaped quotes) right down the middle into `''` + `''`, and each piece ends up wrapped in its own card's outer quotes. That creates an off-by-one in how many quotes land in each subcard.

### 2. The `_strg_comment_RE` regex is deceptively complex

```python
_strg = r"\'(?P<strg>([ -~]+?|\'\'|) *?)\'(?=$|/| )"
```

The lookahead `(?=$|/| )` requires the closing quote to be followed by end-of-string, `/`, or a space. This is correct FITS syntax — but when a CONTINUE card ends with `''''` (4 quotes), the regex has to "count inward" to find the right closing quote. I kept expecting it to fail, then tracing it succeeding, then second-guessing myself.

The inner pattern `([ -~]+?|\'\'|)` allows `'` as part of `[ -~]+?`, meaning the regex can match a single `'` or a `''` pair — whichever backtracks correctly. Non-greedy matching here is subtle: which `'` becomes the closing quote depends on what follows it, and with 4+ consecutive quotes that cascade of lookahead checks confused me.

### 3. Distinguishing `str(card)` vs `card.image` vs `Card.fromstring`

The bug report uses `str(card1)` — which just calls `__str__` → `self.image`. And `Card.fromstring(str(card1))` reconstructs from the multi-card image string. I initially wasn't sure if `fromstring` resets `_verified` and forces a fresh `_split` call, or if cached state from the first card bled through. Looking at `fromstring` (line 571: `card._verified = False`) confirmed it's a fresh parse. So the bug is purely in the round-trip encode/decode, not in state leakage.

---

## How MCP Helped

### `cypher` — Commit Discovery

The first thing I had to do was confirm the target commit `80c3854a5f4f4a6ab86c03d9db7854767fcd83c1` was actually indexed. The cypher query:

```cypher
MATCH (k:Knowledge {knowledge_id: '...'})
MATCH (k)-[:HAS_FILE]->(fn:FileNode)-[:HAS_VERSION]->(fv:FileVersion)
WITH collect(DISTINCT fv.commit_hash) AS commits
RETURN size(commits) AS total_indexed_commits, commits
```

Returned all 23 indexed commits instantly. The target hash was right there in the list. Without this I'd have been guessing blindly at whether the file versions I was reading matched the right code.

**Token estimate: ~2,000 tokens**

### `retrieve_file` (metadata) — Rapid File Orientation

Calling `metadata` on both `astropy/io/fits/card.py` and `astropy/io/fits/tests/test_header.py` in one shot gave me:
- `sectionMap` — a precise line-range index of every logical section in card.py. I could jump straight to `L828-866: _split logic` without reading 800 lines of setup.
- `functions[]` — confirmed `_split`, `_format_long_image`, `_itersubcards`, `_parse_value` all existed and where to look.
- `summary` — a paragraph describing that `_split reconstructs the value/comment across subcards by iterating subcards` — this pinpointed the reconstruction logic as the suspect area immediately.

**What confused me**: the `sectionMap` had some duplicate/shifted entries like `L1-30: _split end logic` which seemed to refer to continuation of the section across what the indexer treated as a "chunk boundary." I initially thought card.py was only 30 lines long, which was clearly wrong. Once I read the actual file content the confusion cleared.

**Token estimate: ~8,000 tokens**

### `retrieve_file` (content, line ranges) — Deep Code Reading

Reading `L820-950` gave me `_split` in full. Reading `L950-1100` gave me `_format_long_image` and `_format_image`. Reading `L705-830` gave me `_parse_value` with the key line:

```python
value = re.sub("''", "'", m.group("strg"))
```

This confirmed how FITS-escaped `''` gets decoded back to a single `'`. Without seeing this line I might have suspected the unescaping was wrong; now I knew it was correct and the problem was upstream in how the FITS string was encoded and split.

Reading `L1-170` for the regex definitions was critical — the `_strg` regex is defined at line 67 and the full `_value_FSC_RE` block from lines 82-127 required careful reading.

**Token estimate: ~6,000 tokens (across 4 content reads)**

### `retrieve_file` (content + search) — `_words_group` lookup

Using `search: "_words_group"` in `util.py` found the function in one call without knowing its line number. This is exactly the kind of "I know the symbol, not the location" case the search mode is designed for. Reading lines 737-777 gave me the full implementation.

This is where the **algorithm confusion** lived. `_words_group` uses a `blank_loc` array and an `offset` variable that changes meaning mid-loop (first it's an end-position estimate, then it's the start of the next chunk). Tracing through with `s = "x"*65 + "''''"` (no spaces) required careful attention: `blank_loc = [69]` (the appended sentinel space), and the first iteration gives `offset = min(67, 69) = 67`, splitting `"x"*65 + "''''"` into `"x"*65 + "''"` and `"''"`.

**The key insight** that MCP helped surface by letting me read `_words_group` directly: the function has no awareness of FITS quoting semantics. It splits the **already-escaped** string at character positions. This means a `''` pair (representing one `'` in the value) can be split across two CONTINUE cards. The reconstruction in `_split()` then joins the halves — but does it correctly strip the continuation `&` and rejoin the escaped content before wrapping in outer quotes? That's where the actual bug lives.

**Token estimate: ~2,500 tokens**

### `retrieve_file` (test file content) — Test Pinpointing

Reading lines 585-600 showed the exact test `test_long_string_value_with_quotes`:

```python
def test_long_string_value_with_quotes(self):
    testval = "x" * 100 + "''"
    c = fits.Card("TEST", testval)
    c = fits.Card.fromstring(c.image)
    assert c.value == testval
```

This told me the patch needs to handle at least three sub-cases: trailing `''`, embedded `''xxx`, and embedded `'' xxx` (with space). The test is clean and minimal — no mocking, no fixtures — which made it easy to reason about without running code.

**Token estimate: ~500 tokens**

---

## What Confused Me About MCP

### 1. Commit scoping returned nothing when passed to `metadata`

When I tried `retrieve_file(operation="metadata", commitHash="80c3854...")`, it returned `totalFound: 0`. But without `commitHash` it returned both files fine. This was confusing — the commit is indexed (confirmed by the cypher query), but the metadata operation apparently only serves the "current" (latest) version. The distinction between `FileNode` (current) and `FileVersion` (per-commit snapshot) in the flat folder model means metadata always reflects the latest state, and you need cypher + content reads for commit-scoped history.

### 2. `sectionMap` line references vs actual file line numbers

The `sectionMap` for `card.py` contained entries like `L1-30: _split end logic producing keyword and value/comment`. But `_split` actually starts at line 829. The indexer was describing "chunk 2" of the file's semantic sections, resetting line numbers to 1 at each chunk boundary rather than using absolute file line numbers. This made me briefly think I was looking at a different file or a short file. Once I started using `retrieve_file(content, fromLine=829)` I trusted absolute line numbers over the section map offsets.

### 3. Metadata `lineCount: 0`

Both `card.py` and `test_header.py` returned `lineCount: 0` in the metadata response. This meant I couldn't quickly estimate how much of the file I needed to read or how many pages of content calls to budget for. I had to infer file size from context (the section map went up to L1333, test file to L3308).

### 4. Token overhead is real

Each `retrieve_file(content)` call for a 150-line block costs ~1,500-2,000 estimated tokens. For a bug like this that requires reading 5-6 separate regions of a 1,333-line file, plus the test file, the cumulative input token cost adds up fast. MCP helped by making each call targeted — but I still needed 6+ content reads because the bug spans `_format_long_image` (encoding), `_words_group` (splitting), `_split` (decoding), and `_parse_value` (unescaping). No single read covered it all.

---

## Summary

MCP's `metadata` operation with `sectionMap` was the single biggest accelerator — it let me navigate a 1,333-line file by section name rather than line number. The `search` mode in content reads (symbol lookup without knowing line numbers) was the second most useful feature. The `cypher` tool was essential for commit verification.

The main confusion points were: commit-scoped metadata not working as expected, `sectionMap` line numbers being chunk-relative rather than absolute, and `lineCount: 0` giving no file-size signal. None of these were blockers, but they each cost a round of re-orientation.

---

*Task: astropy/astropy#14598 — FITS Card double single-quote inconsistency*
*Knowledge base: `eb768039-0fd9-4051-bf82-44ce31015d78` (astropy)*
*Commit: `80c3854a5f4f4a6ab86c03d9db7854767fcd83c1`*

---

---

# MCP SWE-Bench Evaluation Report — 22 Tasks

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-03-30
**Judge:** Claude Code (claude-sonnet-4-6)

> **Note — Stuck Question:** `astropy__astropy-14598` was the question the team got stuck on during this evaluation run. The debugging reflection above documents the confusion points encountered while diagnosing the two-bug root cause (double-decode in `_split` + premature regex close in `_strg`). Despite getting stuck, the MCP ultimately produced a correct and well-traced answer, scoring 9/10.

---

## Scoring Rubric

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification | 3 pts | Did the MCP correctly diagnose WHY the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the code change match or is functionally equivalent to ground truth? |
| Test awareness | 2 pts | Did it account for failing tests / propose test changes? |

---

## Results

| # | Instance ID | Difficulty | RC | Files | Patch | Tests | **Total** | Notes |
|---|-------------|------------|----|-------|-------|-------|-----------|-------|
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | Exact 1-char fix (`= 1` → `= right`); test cases match failing parametrized IDs |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | Used "expected" correctly; `as_scalar_or_list_str` applied correctly; message matches ground truth |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | Exact 6-line removal; `test_structured_masked_column` and parametrized `test_ndarray_mixin` match |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 2 | 2 | **9/10** | All 6 correct files identified; `EarthLocationAttribute`, `EARTH_CENTER`, new transform file all correct; minor deduction — ERFA refraction constants unverifiable without execution |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | 2 | **9/10** | Added `_set_col_formats()` — functionally correct; missing `self.data.cols = cols` assignment present in ground truth |
| 6 | `astropy__astropy-13579` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | Exact fix: `world_coords[iworld]` replacing `1.0`; `test_coupled_world_slicing` with full WCS header matches |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | `except (TypeError, ValueError, AttributeError)` — exact match; DuckQuantity1–4 and `TestUfuncReturnsNotImplemented` comprehensive |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | Descriptor re-invocation in `__getattr__` 'Fail' section correct; no infinite recursion; test asserts `random_attr` in message |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | `header_rows=None` + `idx = len(self.header.header_rows)` — exact match; `test_rst_with_header_rows` with units correct |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 3 | 2 | **10/10** | `len(args) > 0 and isinstance(args[0], ...)` — exact fix; test covers both direct call and `identify_format` |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | `re.IGNORECASE` + `v.upper() == "NO"` — exact match; parametrized `lowercase=[False, True]` test |
| 12 | `astropy__astropy-14369` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | PLY left-recursive grammar rules correct; associativity trace accurate; test cases match |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 2 | 2 | **9/10** | `str()` + `e`→`E` normalization + `elif`→`if` all correct; `> 20 chars` threshold over-engineered vs likely simpler ground truth |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | `"P" in col.format or "Q" in col.format` — exact fix; updated diff counts (13→15, 68.18%) match |
| 15 | `astropy__astropy-145995` | <15m | 3 | 2 | 3 | 2 | **10/10** | `elif operand is None:` → `elif operand.mask is None:` — exact fix; bitmask test covers all 5 combinations |
| 16 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 2 | 2 | **9/10** | ⚠️ **Stuck question** (see reflection above). Two-bug root cause correctly identified; regex `(?:''│[ -&(-~])*?` and `.replace()` removal both correct; minor deduction — exact regex form vs ground truth unverifiable |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 3 | 2 | **10/10** | `inspect.isdatadescriptor(val)` added — exact match |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | 2 | **10/10** | `and wrapped_signature.return_annotation is not None` — exact match |
| 19 | `astropy__astropy-7606` | <15m | 3 | 2 | 3 | 2 | **10/10** | `try/except (ValueError, UnitsError, TypeError)` mirrors `UnitBase.__eq__` pattern — exact match |
| 20 | `astropy__astropy-7671` | <15m | 3 | 2 | 3 | 2 | **10/10** | Strip non-numeric version suffixes with regex before `LooseVersion` — correct fix |
| 21 | `astropy__astropy-8707` | <15m | 3 | 2 | 3 | 2 | **10/10** | Both `Card.fromstring` and `Header.fromstring` byte decoding — exact match |
| 22 | `astropy__astropy-8872` | <15m | 3 | 2 | 3 | 2 | **10/10** | `np.can_cast(np.float32, ...)` → `np.issubdtype(..., np.inexact)` at both locations — exact match |

---

## Summary Scorecard

| Metric | Value |
|--------|-------|
| **Total score** | **216 / 220** |
| **Percentage** | **98.2%** |
| Perfect (10/10) | 18 / 22 |
| Near-perfect (9/10) | 4 / 22 |
| Partial (≤7/10) | 0 / 22 |

---

## Tasks at 9/10

| Instance | Deduction reason |
|----------|-----------------|
| `astropy__astropy-13398` | Patch −1: ERFA refraction constant values unverifiable without running tests; all structural decisions correct |
| `astropy__astropy-13453` | Patch −1: Missing `self.data.cols = cols` line from ground truth; single `_set_col_formats()` call may be sufficient if cols is already set upstream |
| `astropy__astropy-14508` | Patch −1: Unnecessary `> 20 chars` fallback threshold not in ground truth; functionally equivalent |
| `astropy__astropy-14598` | Patch −1: Exact `_strg` regex form vs ground truth unverifiable; conceptually and mechanically correct — **this was the question the team got stuck on** (see reflection above) |

---

## Overall Assessment

**Score: 216/220 (98.2%)**

### Strengths
- **Root cause accuracy: 22/22** — Correctly diagnosed every bug, including two-bug compound issues (`14598`), grammar associativity (`14369`), topocentric ERFA transforms (`13398`), and descriptor invocation edge cases (`14096`).
- **File identification: 22/22** — Never pointed at the wrong file; correctly identified multi-file changes including new-file creation.
- **Simple bugs: near-perfect** — All `<15 min` difficulty tasks resolved with exact or functionally equivalent one-line fixes.
- **Test awareness: 22/22** — Proposed appropriate tests in every task; parametrized fixtures, regression tests, and round-trip checks consistently correct.

### Weaknesses
- **Complex multi-file features** (`13398`): Exact ERFA constant values unverifiable without execution.
- **Minor patch incompleteness** (`13453`): Missed one setup line; fix likely still works in context.
- **Over-engineered fallback** (`14508`): Unnecessary threshold; functionally correct but diverges from likely simpler ground truth.
- **Stuck on `14598`**: Required the most MCP tool calls (18) and wall-clock time (1192s). The two-bug compound nature (regex + double-decode interaction) was the hardest diagnostic in the set. Ultimately resolved correctly despite the confusion documented in the reflection above.
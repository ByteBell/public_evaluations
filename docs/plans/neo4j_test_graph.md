Looking at your current schema and the pipeline, the core problem is clear: **your Neo4j graph captures semantic meaning but not code structure dependencies**. Phase 1 fails because the graph can't answer "who implements this interface" or "who calls this method" — it can only answer "who has similar keywords." That's why you need AI to compensate for what the graph should already know.

Here's the redesigned schema:

---

**Current Schema Problem**

```
FileNode --[HAS_KEYWORD]--> Keyword("authentication")
FileNode --[HAS_KEYWORD]--> Keyword("jwt")
```

This tells you *what* a file talks about, not *how it depends on other code*. For blast radius you need structural edges.

---

**Proposed Schema**

```cypher
// --- NODE TYPES ---

(:Package)        // Go package / module (e.g. k8s.io/client-go/tools/cache)
(:File)           // Individual .go file
(:Interface)      // Interface definition (e.g. SharedInformer)
(:ConcreteType)   // Struct or named type (e.g. sharedInformerFactory)
(:Function)       // Standalone function or method
(:Field)          // Struct field

// --- DEFINITION EDGES (File → what it owns) ---

(File)-[:DEFINES_INTERFACE]->(Interface)
(File)-[:DEFINES_TYPE]->(ConcreteType)
(File)-[:DEFINES_FUNCTION]->(Function)

// --- TYPE RELATIONSHIP EDGES ---

(ConcreteType)-[:IMPLEMENTS]->(Interface)
// populated when: var _ Interface = (*Type)(nil)
// OR when all interface methods are present on the type

(ConcreteType)-[:EMBEDS]->(ConcreteType)
// populated from Go struct embedding

(Interface)-[:EXTENDS]->(Interface)
// populated when interface embeds another interface

// --- USAGE EDGES (the blast radius edges) ---

(File)-[:IMPORTS]->(Package)
// direct import graph

(Function)-[:CALLS]->(Function)
// call graph edge

(Function)-[:ACCEPTS_TYPE]->(Interface | ConcreteType)
// parameter type reference

(Function)-[:RETURNS_TYPE]->(Interface | ConcreteType)
// return type reference

(Field)-[:OF_TYPE]->(Interface | ConcreteType)
// struct field whose type is the changed interface

(File)-[:REFERENCES_TYPE]->(Interface | ConcreteType)
// any direct usage of the type (catch-all for var declarations, type assertions etc.)

// --- PACKAGE EDGES ---

(File)-[:BELONGS_TO]->(Package)
(Package)-[:DEPENDS_ON]->(Package)
// derived from IMPORTS aggregated at package level
```

---

**What This Unlocks for Phase 1**

For a `new_interface_method` change on `SharedInformer`, instead of asking AI to enumerate grep terms, you run one traversal:

```cypher
// Find everything that needs to change when SharedInformer grows a new method

MATCH (changed:Interface {name: "SharedInformer"})

// Tier 1: Direct implementors — these WILL break (compile error)
OPTIONAL MATCH (t:ConcreteType)-[:IMPLEMENTS]->(changed)
WITH changed, collect(DISTINCT t) AS implementors

// Tier 2: Interfaces that extend the changed one — their implementors also break
OPTIONAL MATCH (ext:Interface)-[:EXTENDS]->(changed)
OPTIONAL MATCH (t2:ConcreteType)-[:IMPLEMENTS]->(ext)

// Tier 3: Files that accept/return the interface — call sites
OPTIONAL MATCH (f:Function)-[:ACCEPTS_TYPE|RETURNS_TYPE]->(changed)

// Tier 4: Fields typed as the interface — struct fields holding it
OPTIONAL MATCH (field:Field)-[:OF_TYPE]->(changed)

// Tier 5: Files that directly reference the type (var declarations etc.)
OPTIONAL MATCH (file:File)-[:REFERENCES_TYPE]->(changed)

RETURN implementors, ext, t2, f, field, file
```

This replaces Phase 1 AI entirely for symbol discovery — you get **deterministic, exhaustive candidates** from the graph. Phase 1 AI then only needs to verify *why* each candidate is impacted, which is a much easier job.

---

**Graph Population: What to Extract**

The hardest part is populating these edges. Your current `FileAnalysisPhase` extracts `imports_internal`, `classes`, `functions` via LLM — but that's not precise enough for type relationships. You need a proper Go AST pass:

```
For each .go file:

1. imports          → (File)-[:IMPORTS]->(Package) edges
2. interface defs   → (File)-[:DEFINES_INTERFACE]->(Interface)
3. struct defs      → (File)-[:DEFINES_TYPE]->(ConcreteType)
4. struct fields    → (Field)-[:OF_TYPE]->(type)
5. struct embedding → (ConcreteType)-[:EMBEDS]->(ConcreteType)
6. method sets      → check all ConcreteTypes against all Interfaces
                      → emit (ConcreteType)-[:IMPLEMENTS]->(Interface)
7. function sigs    → (Function)-[:ACCEPTS_TYPE]->(type)
                      (Function)-[:RETURNS_TYPE]->(type)
8. interface embeds → (Interface)-[:EXTENDS]->(Interface)
9. call sites       → (Function)-[:CALLS]->(Function)  [expensive, do last]
```

For Go specifically, `go/ast` + `go/types` gives you all of this deterministically. For other languages, tree-sitter covers most cases. Your current LLM-based extractor for `imports_internal` is a reasonable fallback but will miss things like type assertions and indirect interface satisfaction.

---

**Severity Tiers Directly from Graph**

Once you have this schema, severity maps cleanly to traversal depth:

| Tier | Cypher Pattern | Severity |
|------|---------------|----------|
| 0 | `DEFINES_INTERFACE` (the file that defines the changed interface) | Source |
| 1 | `IMPLEMENTS` → interface | `compile_error` — must add method |
| 2 | `EXTENDS` → `IMPLEMENTS` (transitively) | `compile_error` — transitive implementors |
| 3 | `ACCEPTS_TYPE` / `RETURNS_TYPE` | `compile_error` or `runtime_regression` depending on signature change type |
| 4 | `OF_TYPE` (field holding the interface) | `compile_error` if the concrete type stored there doesn't implement new method |
| 5 | `REFERENCES_TYPE` (general usage) | `runtime_regression` or `no_impact` — needs Phase 3 verification |
| 6 | `IMPORTS` package but no direct type reference | Almost certainly `false_positive` — drop before Phase 3 |

This means Phase 3 AI only needs to verify Tier 5 (ambiguous references). Tiers 1–4 are deterministic compile errors the graph can confirm without AI.

---

**What Changes in the Pipeline**

```
Before:
  Phase 1 (AI enumerates grep terms)  ← expensive, hallucination risk
  Phase 2 (Grep runs all terms)        ← many false positives from keyword matches
  Phase 3 (AI filters 100 candidates)  ← expensive

After:
  Graph Traversal (deterministic Cypher query)  ← replaces Phase 1 + most of Phase 2
    → Tier 1-4: auto-confirmed impacted (no AI needed)
    → Tier 5: small candidate list for Phase 3 AI verification
    → Tier 6: dropped entirely
  Phase 3 (AI verifies only Tier 5 ambiguous files)  ← 10x fewer files to verify
```

The main investment is building the AST extraction pass that populates `IMPLEMENTS`, `EXTENDS`, `ACCEPTS_TYPE`, `RETURNS_TYPE`, `OF_TYPE` accurately. Everything downstream gets faster and cheaper once that's solid.


Good question — and this is where the approach needs to split based on a fundamental language characteristic: **nominal typing vs structural typing**.

---

## The Core Problem

Go, Java, C# use **nominal typing** — a type explicitly declares what it implements. The graph edges are unambiguous.

TypeScript and Python use **structural typing** — a type satisfies an interface just by having the right shape, with no explicit declaration. You can't derive `IMPLEMENTS` from a single file; you have to compare method sets across the whole codebase.

This changes the extraction strategy significantly per language.

---

## TypeScript

**Tooling:** TypeScript Compiler API (`ts-morph` wraps it nicely) — this gives you full type-resolved AST, not just syntax.

**What you can extract deterministically:**

```typescript
// Explicit nominal edges — easy
class AuthService implements IAuthService { }
// → (AuthService)-[:IMPLEMENTS]->(IAuthService)

interface ITokenService extends IBaseService { }
// → (ITokenService)-[:EXTENDS]->(IBaseService)

// Type references in signatures — easy
function login(service: IAuthService): AuthToken { }
// → (login)-[:ACCEPTS_TYPE]->(IAuthService)
// → (login)-[:RETURNS_TYPE]->(AuthToken)

// Field types — easy
class App {
  private auth: IAuthService
}
// → (auth field)-[:OF_TYPE]->(IAuthService)
```

**What's hard — structural satisfaction:**

```typescript
// This satisfies IAuthService without ever saying so
const myAuth = {
  login: (creds) => { ... },
  logout: () => { ... }
}
// Is myAuth an IAuthService implementor? Only if types match structurally.
```

**Practical approach:** Don't try to resolve structural satisfaction statically. Instead:

1. Extract all `implements` and `extends` declarations as hard edges (nominal)
2. Add a `STRUCTURALLY_COMPATIBLE` edge derived from `ts-morph`'s `isAssignableTo()` check — this is what the TS compiler uses and it's reliable
3. For object literals and anonymous types, add a `REFERENCES_TYPE` edge if the variable is explicitly typed as the interface (most well-written TS code does this)

```
(ConcreteType)-[:IMPLEMENTS]->(Interface)         // from 'implements' keyword
(ConcreteType)-[:STRUCTURALLY_SATISFIES]->(Interface)  // from compiler assignability check
(ConcreteType)-[:EXTENDS]->(ConcreteType)         // class inheritance
(Interface)-[:EXTENDS]->(Interface)               // interface merging/extending
```

The `STRUCTURALLY_SATISFIES` edge is TypeScript-specific and has no Go equivalent. Your blast radius query needs to include it.

**Key TS-specific edges to add:**

```cypher
// Type aliases that shadow or wrap the interface
(TypeAlias)-[:ALIASES]->(Interface | ConcreteType)

// Generic type parameters — if the interface is used as a constraint
(Function)-[:TYPE_CONSTRAINED_BY]->(Interface)
// e.g. function foo<T extends IAuthService>(t: T)

// Declaration merging — TS-specific, interface can be augmented across files
(Interface)-[:MERGED_WITH]->(Interface)
```

---

## Python

Python is the hardest because it has **no compile-time type checking by default**. The blast radius of a change is genuinely runtime-dependent. But you can still build a useful graph:

**Two tiers of Python projects:**

**Tier 1 — Typed Python** (has `typing` annotations, `Protocol`, mypy/pyright runs clean):

```python
from typing import Protocol

class IAuthService(Protocol):
    def login(self, creds: Credentials) -> Token: ...

class AuthService:
    def login(self, creds: Credentials) -> Token:  # implicitly satisfies IAuthService
        ...
```

Use `pyright`'s programmatic API or `libcst` + `mypy` to resolve Protocol satisfaction. This gets you close to Go-level precision.

**Tier 2 — Untyped/loosely typed Python** (no annotations, duck typing everywhere):

Here you genuinely cannot determine the blast radius statically. The best you can do is heuristic.

**Extraction strategy for Python:**

```python
# What you can get from AST alone (ast module or libcst)

# Class inheritance
class AuthService(BaseService): ...
# → (AuthService)-[:EXTENDS]->(BaseService)

# ABC/Protocol registration
class AuthService(IAuthService): ...          # explicit ABC subclass
AuthService.register(ConcreteAuth)            # virtual subclass — harder
# → (AuthService)-[:IMPLEMENTS]->(IAuthService)

# Import graph — very reliable
from services.auth import AuthService
# → (File)-[:IMPORTS]->(Package)

# Type annotations in function signatures
def process(service: IAuthService) -> Token:
# → (process)-[:ACCEPTS_TYPE]->(IAuthService)
# → (process)-[:RETURNS_TYPE]->(Token)

# dataclass fields
@dataclass
class App:
    auth: IAuthService
# → (auth)-[:OF_TYPE]->(IAuthService)
```

**Python-specific edges to add:**

```cypher
// ABC virtual subclassing (register() calls)
(ConcreteType)-[:VIRTUAL_SUBCLASS_OF]->(ABCType)

// __init__ dependency injection patterns
(ConcreteType)-[:DEPENDS_ON_TYPE]->(Interface)
// from __init__ parameter type annotations

// Decorator-based registration (common in frameworks)
(Function)-[:REGISTERED_AS]->(Interface)
// e.g. @app.route, @service.register
```

**For untyped Python** — fall back to name-based heuristics:

```
If a class has methods with the same names as the changed interface's methods
AND those methods have compatible arity
→ emit (ConcreteType)-[:LIKELY_IMPLEMENTS {confidence: "low"}]->(Interface)
```

This is imprecise but better than nothing, and you can filter it in Phase 3 with confidence thresholds.

---

## Universal Extraction Architecture

Rather than building per-language from scratch, structure it as a language driver system:

```
LanguageDriver interface:
  - extract_imports(file) → List[ImportEdge]
  - extract_definitions(file) → List[DefinitionEdge]  
  - extract_type_relations(file, type_registry) → List[TypeEdge]
  - extract_call_sites(file) → List[CallEdge]
  - confidence_level → "exact" | "heuristic"
```

| Language | Driver Tool | Implements confidence |
|----------|------------|----------------------|
| Go | `go/ast` + `go/types` | exact |
| TypeScript | `ts-morph` (TS compiler API) | exact for nominal, high for structural |
| Python (typed) | `libcst` + `pyright` API | high |
| Python (untyped) | `ast` module + name matching | low/heuristic |
| Java | `javaparser` | exact |
| Rust | `syn` crate | exact (traits) |
| Ruby/PHP | regex + heuristic | low |

---

## Confidence Annotations in the Graph

Since Python structural matching and TS structural satisfaction are probabilistic, you need confidence on edges:

```cypher
(ConcreteType)-[:IMPLEMENTS {
  confidence: "exact",      // from 'implements' keyword
  source: "nominal"
}]->(Interface)

(ConcreteType)-[:IMPLEMENTS {
  confidence: "high",       // from compiler assignability check
  source: "structural_check"
}]->(Interface)

(ConcreteType)-[:IMPLEMENTS {
  confidence: "low",        // from name/arity heuristic
  source: "heuristic"
}]->(Interface)
```

Then your blast radius query can be parameterized:

```cypher
// Strict mode — only confirmed impact
MATCH (t)-[:IMPLEMENTS {confidence: "exact"}]->(changed)

// Broad mode — include probable impacts for Phase 3 verification
MATCH (t)-[:IMPLEMENTS]->(changed)
WHERE rel.confidence IN ["exact", "high", "low"]
```

Low confidence edges go to Phase 3 AI verification. High/exact confidence edges are auto-confirmed. This keeps Phase 3 small even for Python codebases.

---

## The Realistic Recommendation

For your benchmark dataset (which is Kubernetes/Go-focused based on the docs), **start with Go only** using `go/ast` + `go/types` for exact extraction. That already covers your current use case and gives you the deterministic Tier 1–4 blast radius.

Add TypeScript next using `ts-morph` — it's the most common language in modern repos and has a strong enough type system to get high-confidence edges. Python support with typed projects via `pyright` after that.

For untyped Python and dynamic languages, be upfront that the graph gives you import-level blast radius (which files import the changed package) and heuristic type-level blast radius, with Phase 3 AI doing the heavy lifting to confirm actual impact. That's still much better than what you have now.
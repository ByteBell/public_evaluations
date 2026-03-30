Add a new method SelectSorted(ctx context.Context, hints *SelectHints, matchers ...*labels.Matcher) SeriesSet to the Querier interface in prometheus/storage. Querier is the core read interface used by Thanos StoreAPI and Mimir query-frontend to evaluate PromQL queries against time-series data. Any type implementing Querier must now satisfy this additional method.


Answer this question without using MCP and also wihtout websearch, Use the repositories present in the folder itself.


## Token Tracking Requirements

### Definitions

- **Input Tokens** — All data returned *from* MCP tools *to* you that you must process (search results, file metadata, file content, graph traversal results, etc.)
- **Output Tokens** — Your final response generated *to* the user (analysis, code, tables, summaries, the cost breakdown itself)

---

### After Each Tool Call

1. Estimate the tokens in that tool's response
2. Add to cumulative input token count
3. Note cumulative time elapsed

### Time Tracking

- First tool call: [timestamp or relative time]
- Last tool call: [timestamp or relative time]
- Total elapsed time: ~X seconds
- Average time per tool call: ~X seconds
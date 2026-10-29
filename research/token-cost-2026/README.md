# Token cost of MCP tool lists (measured 2026-10-22)

The 16 of the 30 most-downloaded MCP server packages on npm that start without an API key, at their current
version: `initialize` and `tools/list` only, never a tool call. Tokens are counted with tiktoken `cl100k_base` on
the tools exactly as the server sent them. Claude's tokeniser gives different absolute numbers; comparisons between
servers and versions are like for like.

- 250 tools, 92,520 tokens. Input schemas 62,490 (68%), descriptions 22,013.
- Notion 2.5.2: 24 tools, 16,894 tokens. Every tool carries the same `$defs` block; 10,889 tokens (64%) are
  definitions the carrying tool's schema never reaches through `$ref`.
- MongoDB 2.1.1 → 3.0.0: 5,003 → 14,232 tokens, same 27 tool names (export, explain, aggregate, create-index
  account for almost all of it).
- Firecrawl 3.22.3 → 3.23.1 → 3.33.4: 17,132 → 8,016 → 11,893. CircleCI 0.18.0 → 0.19.0: 14,195 → 10,776.
- Three packages come from the earlier probe: Currents 2.7.0 refused to start without `CURRENTS_API_KEY`
  (2.2.18 used); CircleCI and nx had no release since 2026-09-10.

## Files
- `data/live-probe-latest-2026-10-22.json`: current-version probe (made with
  `../tool-churn-2026/scripts/live_probe_churn.py --since 2026-09-10 --until 2026-10-22 --max-versions 1`).
- `data/live-probe-recent-releases-2026-10-20.json`: every release 2026-08-30 to 2026-10-21 for 12 packages
  (MongoDB 3.x, Firecrawl 3.31+).
- Older versions: `../tool-churn-2026/data/live-probe-churn-2026-10-04.json`.
- `data/token-cost-2026-10-22.json`: the table, from
  `python scripts/token_cost.py data/live-probe-latest-2026-10-22.json ../tool-churn-2026/data/live-probe-churn-2026-10-04.json`.

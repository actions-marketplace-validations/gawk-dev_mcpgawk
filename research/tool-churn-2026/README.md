# MCP tool churn, March to September 2026

Every stable release of the 30 most-downloaded MCP server packages on npm, launched without API keys,
`initialize` and `tools/list` only, never a tool call. Each version's tool surface (name, description,
input schema, annotations) is diffed against the one before it.

- 107 version-to-version updates compared, 49 changed the tool surface (46%)
- 25 of those 49 let a tool do something new (new tool, rewritten description, a new parameter that points
  at a URL, path or headers, or a safety label change); 24 only reshuffled
- details: `summary.md`, `risk-classes.md`; raw data in `data/`

Rerun the sorting: `python scripts/risk_classes_2026-10-20.py` from a clone of this repo (uses the rule in
`src/mcpgawk/drift.py`). Caveats are in both write-ups: keyless launches understate servers that gate tools
on a key, and 8 packages would not start without one.

# Archived MCP servers, still installed (snapshot 2026-10-22)

Five reference servers the Model Context Protocol project archived on 2025-05-29 (commit d53d6cc75c,
"Archive unmaintained servers") are still among the 30 most-downloaded MCP server packages on npm. Plus
CircleCI's npm package, deprecated in favour of its hosted server.

| Package | latest | published | npm deprecation message |
|---|---|---|---|
| @modelcontextprotocol/server-github | 2025.4.8 | 2025-04-08 | "Package no longer supported. Contact Support at https://www.npmjs.com/support for more info." |
| @modelcontextprotocol/server-slack | 2025.4.25 | 2025-04-25 | same |
| @modelcontextprotocol/server-postgres | 0.6.2 | 2024-12-04 | same |
| @modelcontextprotocol/server-puppeteer | 2025.5.12 | 2025-05-12 | same |
| @modelcontextprotocol/server-brave-search | 0.6.2 | 2024-12-04 | same |
| @circleci/mcp-server-circleci | 0.20.0 | 2026-08-06 | "Deprecated: use CircleCI's hosted MCP server or CircleCI CLI MCP instead…" |

All five npm READMEs still show an `"npx", "-y"` install line. Only server-github's carries a deprecation
notice (pointing at github/github-mcp-server).

## Downloads
- The five reference servers, per month: 407,645 in June 2025, 1,738,924 in July 2026. 15,794,694 from
  2025-06-01 to 2026-10-21. That total is a floor: npm reports some whole days as zero (see `zero_days`).
- Week 21–27 Sep 2026, all six packages: 455,402. server-postgres alone: 109,622.
- Do not use the week 12–18 Oct 2026 (215,807): it contains zero days across every package, a stats gap.
- For comparison, maintained reference servers over the same months: server-filesystem 174,541 → 2,399,054;
  server-memory 93,023 → 535,816.
- Downloads count CI jobs and mirrors as well as people. They are not users.

## server-postgres: a known bug, fix merged, never published
Datadog Security Labs, 2025-08-21: a query starting `COMMIT;` ends the server's read-only transaction, and
later statements run with the database role's full rights
(https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/).
The fix, modelcontextprotocol/servers PR #1889, was merged to main on 2025-05-29, the day of the archive. npm
still serves 0.6.2 from 2024-12-04. Datadog counted about 21,000 weekly downloads then.

## Is the warning visible?
With a fresh npm cache, `npx -y @modelcontextprotocol/server-postgres <url>` prints `npm warn deprecated …` to
stderr on the first start. A second start, from npx's cache, prints nothing.

## Rerun
`python scripts/fetch.py > data/snapshot-$(date +%F).json` (standard library only). `data/snapshot-2026-10-22.json`
holds this snapshot: version, deprecation text, monthly and daily downloads, zero days.

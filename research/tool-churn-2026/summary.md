# Live-probe tool-surface churn, 10 Mar → 9 Sep 2026 — the numbers (run 2026-10-04, partial)

Method: scripts/live_probe_churn.py. For each of the 30 most-downloaded MCP server npm packages (list from
npm-tool-churn-2026-09-29.json), every stable version published in the window (newest 12), launched KEYLESS with
`npx -y <pkg>@<version>` in a throwaway HOME (no API keys in the environment), probed with initialize + tools/list
only, tool surface stored (name, description, inputSchema, annotations), transitions between consecutive
successfully-probed versions diffed per tool and per parameter. One environment for every version — Nueravi's recipe,
with her firecrawl trap avoided by construction. Data: live-probe-churn-2026-10-04.json. Runs stopped twice by a full
disk; 23 of 30 packages reached (7 not yet probed: @netlify/mcp, @mastra/mcp-docs-server, @circleci/mcp-server-circleci,
@perplexity-ai/mcp-server, @modelcontextprotocol/server-puppeteer, @modelcontextprotocol/server-brave-search,
@hubspot/mcp-server; @salesforce/mcp incomplete).

## Headline, framed as it must be said
Of the 23 packages probed, 14 launched keyless at least once. Across their 86 version-to-version transitions, 40
changed the tool surface: 47%. Nueravi measured 48% across 96 releases of nine servers. Two independent runs, two
methods, the same number.

| | count |
|---|---|
| packages probed | 23 (of 30) |
| launched keyless at least once | 14 |
| versions probed | 152 |
| transitions between consecutive launchable versions | 86 |
| transitions that changed the tool surface | 40 (47%) |
| tools added / removed across all transitions | 12 / 4 |
| transitions with any inputSchema change | 33 |
| transitions with a description change only (no schema, no add/remove) | 4 |
| transitions with an annotation change | 4 |
| parameter-level changes: added / removed / type changed / description changed / other | 77 / 16 / 5 / 92 / 8 |

The parameter-level split is the answer to her hand-read: "wording inside a parameter" is the LARGEST category (92
parameter descriptions rewritten across the window), not the rarest; type changes are the rarest (5). Descriptions-only
at the tool level are rare (4 transitions); the churn lives in the schemas.

## Per package (transitions / changed), keyless
chrome-devtools-mcp 11/8 (29→29 tools) · firecrawl-mcp 11/7 (26→25 keyless; the keyed surface has two more) ·
@playwright/mcp 10/6 (21→24) · @shopify/dev-mcp 10/6 (5→6) · mongodb-mcp-server 9/4 (24→27) · @currents/mcp 4/4
(30→32; 7 of 12 versions would not start keyless) · @upstash/context7-mcp 11/3 (2→2: same two tools, descriptions and
schemas moved three times) · server-filesystem 2/1 · server-sequential-thinking 1/1 · server-everything 2/0 ·
notion-mcp-server 4/0 · server-memory 1/0 · @ui5/mcp-server 9/0 · nx-mcp 1/0.
Would not start keyless (every version exited before initialize, typically demanding a credential): @azure/mcp,
@sentry/mcp-server, @azure-devops/mcp, @supabase/mcp-server-supabase, @launchdarkly/mcp-server, @salesforce/mcp.
No stable release in the window: server-github, server-slack, server-postgres (archived reference servers).

## Caveats, stated before anyone else states them
Keyless probing understates servers that gate tools on a key (firecrawl: 25 vs 27) and excludes the six that refuse to
start without one. "Changed the tool surface" is the four-field pin (name, description, inputSchema, annotations); a
transition counts once however many tools moved. 7 packages still to probe when disk allows.

## Completed 2026-10-07 — all 30 packages reached
Resumed with the same script and settings for the 8 missing packages (7 never reached + @salesforce/mcp incomplete).
A recompute of the 4 Oct subset reproduces every published figure (40/86, 12/4 added/removed, 92 parameter descriptions,
77 parameters added, 5 type changes); the only delta there is 152 → 155 versions, the 3 @salesforce/mcp versions finished now.

| | 4 Oct (23 of 30) | complete (30 of 30) |
|---|---|---|
| launched keyless at least once | 14 | 16 |
| versions probed | 152 | 185 |
| transitions | 86 | 107 |
| changed the tool surface | 40 (47%) | 49 (46%) |
| tools added / removed | 12 / 4 | 12 / 8 |
| transitions with any inputSchema change | 33 | 39 |
| description-only transitions | 4 | 5 |
| annotation-change transitions | 4 | 5 |
| parameters added / removed / type / description / other | 77 / 16 / 5 / 92 / 8 | 77 / 16 / 5 / 94 / 14 |

New packages: @circleci/mcp-server-circleci 10/7 (17 → 13 tools at 0.19.0), @mastra/mcp-docs-server 11/2 (13 → 13).
No stable release in the window: @netlify/mcp, @modelcontextprotocol/server-puppeteer, server-brave-search, @hubspot/mcp-server.
Would not start keyless: @perplexity-ai/mcp-server (all 7), @salesforce/mcp (all 12) — joins the six listed above (eight now).
Concentration: six servers (chrome-devtools-mcp 8, firecrawl 7, circleci 7, playwright 6, shopify dev 6, mongodb 4) hold
38 of the 49 changed transitions; notion, ui5, nx, server-everything and server-memory moved 0 times in 17 transitions.
Headline for anything new: **46% across all 30 (49 of 107)**. The 7 Oct Medium reply quoted the 23-package 47%; both stand.
Recompute:  (sum of transitions[].any_change / parameters[].change per package).

## Nueravi's nine, like for like (2026-10-07)
Her study ("We Diffed 96 Releases of 9 Agent Tool Servers — 48% Broke the Cache Prefix", 9 Sep 2026): server-filesystem,
-memory, -sequential-thinking, @playwright/mcp, @upstash/context7-mcp, firecrawl-mcp, exa-mcp-server, tavily-mcp,
@notionhq/notion-mcp-server; every stable release 10 Mar – 9 Sep (9 Sep inclusive); change = name/description/inputSchema.
Probed keyless, every release (`--max-versions 200 --until 2026-09-10`), data live-probe-nueravi-nine-2026-10-07.json,
compare scripts/research/nine_server_compare.py. Run twice: 85 of 85 versions byte-identical across runs (determinism).
First run used `--until 2026-09-09` and missed context7 4.0.7 (published 9 Sep 14:03Z) — the window boundary matters.

| server | releases | launched keyless | transitions | changed (her def.) | + annotations | Nueravi |
|---|---|---|---|---|---|---|
| firecrawl-mcp | 36 | 26 | 25 | 18 | 18 | 23/35 (dummy key for 10) |
| @upstash/context7-mcp | 27 | 27 | 26 | 8 | 8 | 8/26 |
| @playwright/mcp | 12 | 12 | 11 | 6 | 6 | 6/11 |
| exa-mcp-server | 4 | 4 | 3 | 2 | 3 | 2/3 |
| tavily-mcp | 5 | 5 | 4 | 1 | 1 | 1/4 |
| @notionhq/notion-mcp-server | 5 | 5 | 4 | 0 | 0 | 0/4 |
| server-filesystem | 3 | 3 | 2 | 1 | 1 | 1/2 |
| server-memory + -sequential-thinking | 4 | 4 | 2 | 1 | 1 | 1/2 (by remainder) |
| **total** | 96 | 86 | 77 | **37 (48%)** | 38 | 42/87 (48%) |

Eight of nine match her per-server counts exactly (19 of 52); the only gap is firecrawl's 10 key-gated releases.
Annotation-only change her byte definition cannot see: exa-mcp-server 3.4.0 → 3.4.1 flipped openWorldHint false → true on
web_search_exa and web_fetch_exa, no description or schema change (3.2.0 → 3.2.1 had added openWorldHint=false).

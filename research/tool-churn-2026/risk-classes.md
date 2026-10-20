# Risk classes of the 49 tool-surface changes (live probe, 30 packages) — 2026-10-20

Script: scripts/risk_classes_2026-10-20.py. Rule: mcpgawk's shipped drift.py (`destination_param`, `execution_param`, `DriftReport.escalations`). Each transition counted once, by its most severe class.

| class | meaning | guard | transitions |
|---|---|---|---|
| A | permission growth (new destination/execution param, or annotation escalation) | BLOCK | 6 |
| B | new tool added | BLOCK | 7 |
| C | tool description rewritten | BLOCK | 12 |
| D | schema-only, no growth | queue, calls continue | 23 |
| E | tools removed only | queue | 1 |
| | **changed / all transitions** | | **49 / 107** |

## Reconciliation against the summary

- transitions 107 (summary 107); changed 49 (summary 49)
- tools added / removed 12 / 8 (summary 12 / 8)
- parameter changes added/removed/type/description/other: 77/16/5/94/14 (summary 77/16/5/94/14)
- tool-level description rewrites: 67 (tool, transition) pairs in 19 transitions; parameter-description rewrites: 94 in 20 transitions
- of the tool-description rewrites, 1 are whitespace-only; 1 class-C transitions are whitespace-only throughout
- class A transitions driven by annotations alone (no new parameter): 2

## Per package (A / B / C / D / E)

| package | A | B | C | D | E | A+B+C |
|---|---|---|---|---|---|---|
| chrome-devtools-mcp | 3 | 0 | 3 | 2 | 0 | 6 |
| firecrawl-mcp | 0 | 1 | 4 | 2 | 0 | 5 |
| @playwright/mcp | 1 | 2 | 0 | 3 | 0 | 3 |
| @shopify/dev-mcp | 0 | 1 | 2 | 3 | 0 | 3 |
| @circleci/mcp-server-circleci | 1 | 0 | 2 | 3 | 1 | 3 |
| mongodb-mcp-server | 1 | 1 | 0 | 2 | 0 | 2 |
| @currents/mcp | 0 | 2 | 0 | 2 | 0 | 2 |
| @modelcontextprotocol/server-filesystem | 0 | 0 | 1 | 0 | 0 | 1 |
| @upstash/context7-mcp | 0 | 0 | 0 | 3 | 0 | 0 |
| @modelcontextprotocol/server-sequential-thinking | 0 | 0 | 0 | 1 | 0 | 0 |
| @mastra/mcp-docs-server | 0 | 0 | 0 | 2 | 0 | 0 |

## Every changed transition

### @playwright/mcp 0.0.70 → 0.0.71 — class A
- GROWTH `browser_tabs`: new destination parameter `url` — URL to navigate to in the new tab, used for new.
- added tools: browser_drop
  - new tool `browser_drop` flags: params ['paths'] annotations {'readOnlyHint': False, 'destructiveHint': True, 'openWorldHint': True}
- parameter changes: {'added': 11, 'removed': 8, 'other': 1, 'description': 1}

### @playwright/mcp 0.0.71 → 0.0.72 — class B
- added tools: browser_network_request, browser_run_code_unsafe
  - new tool `browser_network_request` flags: params [] annotations {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}
  - new tool `browser_run_code_unsafe` flags: params [] annotations {'readOnlyHint': False, 'destructiveHint': True, 'openWorldHint': True}
- removed tools: browser_run_code
- description `browser_network_requests`:
  - before: Returns all network requests since loading the page
  - after: Returns a numbered list of network requests since loading the page. Use browser_network_request with the number to get full details.
- parameter changes: {'removed': 2}

### @playwright/mcp 0.0.73 → 0.0.74 — class D
- parameter changes: {'description': 1}

### @playwright/mcp 0.0.76 → 0.0.77 — class D
- parameter changes: {'added': 1}

### @playwright/mcp 0.0.77 → 0.0.78 — class B
- added tools: browser_find
  - new tool `browser_find` flags: params [] annotations {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}

### @playwright/mcp 0.0.78 → 0.0.79 — class D
- parameter changes: {'description': 2}

### chrome-devtools-mcp 0.26.0 → 1.0.1 — class A
- GROWTH `evaluate_script`: new destination parameter `filePath` — The absolute or relative path to a file to save the script output to. If omitted, the output is returned inline.
- parameter changes: {'description': 1, 'added': 1}

### chrome-devtools-mcp 1.0.1 → 1.1.0 — class A
- GROWTH `emulate`: new destination parameter `extraHttpHeaders` — Extra HTTP headers as a JSON string object, e.g. {"X-Custom": "value", "Authorization": "Bearer token"}. Headers are included into every HTTP request originating from the page and persist across navigations until cleared…
- added tools: take_heapsnapshot
  - new tool `take_heapsnapshot` flags: params ['filePath'] annotations {'readOnlyHint': False}
- removed tools: take_memory_snapshot
- parameter changes: {'added': 1}

### chrome-devtools-mcp 1.1.1 → 1.2.0 — class D
- parameter changes: {'added': 1}

### chrome-devtools-mcp 1.4.0 → 1.5.0 — class C
- description `evaluate_script`:
  - before: Evaluate a JavaScript function inside the currently selected page. Returns the response as JSON, so returned values have to be JSON-serializable.
  - after: Evaluate a JavaScript function inside the currently selected page. Returns the response as JSON, so returned values have to be JSON-serializable.
- parameter changes: {'description': 1}

### chrome-devtools-mcp 1.5.0 → 1.6.0 — class D
- parameter changes: {'other': 1}

### chrome-devtools-mcp 1.6.0 → 1.7.0 — class C
- description `list_network_requests`:
  - before: List all requests for the currently selected page since the last navigation.
  - after: Lists the most recent requests for the currently selected page since the last navigation.

### chrome-devtools-mcp 1.7.0 → 1.8.0 — class A
- GROWTH `upload_file`: new destination parameter `filePaths` — One or more files paths to upload. File paths have to be local to the browser instance (not the MCP).
- description `emulate`:
  - before: Emulates various features on the selected page.
  - after: Emulates various features on the target page.
- description `evaluate_script`:
  - before: Evaluate a JavaScript function inside the currently selected page. Returns the response as JSON, so returned values have to be JSON-serializable.
  - after: Evaluate a JavaScript function inside the target page. Returns the response as JSON, so returned values have to be JSON-serializable.
- description `list_console_messages`:
  - before: List all console messages for the currently selected page since the last navigation.
  - after: List all console messages for the target page since the last navigation.
- description `list_network_requests`:
  - before: Lists the most recent requests for the currently selected page since the last navigation.
  - after: Lists the most recent requests for the target page since the last navigation.
- description `performance_start_trace`:
  - before: Start a performance trace on the selected webpage. Use to find frontend performance issues, Core Web Vitals (LCP, INP, CLS), and improve page load speed.
  - after: Start a performance trace on the target webpage. Use to find frontend performance issues, Core Web Vitals (LCP, INP, CLS), and improve page load speed.
- description `performance_stop_trace`:
  - before: Stop the active performance trace recording on the selected webpage.
  - after: Stop the active performance trace recording on the target webpage.
- description `resize_page`:
  - before: Resizes the selected page's window so that the page has specified dimension
  - after: Resizes the page's window so that the page has specified dimension
- description `take_heapsnapshot`:
  - before: Capture a heap snapshot of the currently selected page. Use to analyze the memory distribution of JavaScript objects and debug memory leaks.
  - after: Capture a heap snapshot of the target page. Use to analyze the memory distribution of JavaScript objects and debug memory leaks.
- description `take_snapshot`:
  - before: Take a text snapshot of the currently selected page based on the a11y tree. The snapshot lists page elements along with a unique identifier (uid). Always use the latest snapshot. Prefer taking a snapshot over taking a sc…
  - after: Take a text snapshot of the target page based on the a11y tree. The snapshot lists page elements along with a unique identifier (uid). Always use the latest snapshot. Prefer taking a snapshot over taking a screenshot. Th…
- parameter changes: {'added': 28, 'description': 2, 'removed': 1}

### chrome-devtools-mcp 1.8.0 → 1.9.0 — class C
- description `get_network_request`:
  - before: Gets a network request by an optional reqid, if omitted returns the currently selected request in the DevTools Network panel.
  - after: Gets a network request by an optional reqid, if omitted returns the currently selected request in the DevTools Network panel. Useful for inspecting request headers (including 'Cookie') and response headers (including 'Se…
- parameter changes: {'description': 1}

### @modelcontextprotocol/server-filesystem 2026.7.4 → 2026.7.10 — class C
- description `read_media_file`:
  - before: Read an image or audio file. Returns the base64 encoded data and MIME type. Only works within allowed directories.
  - after: Read a file and return it as a base64-encoded content block with its MIME type. Image and audio files are returned as image/audio content; any other file type is returned as an embedded resource. Only works within allowe…

### @upstash/context7-mcp 3.2.2 → 3.2.3 — class D
- parameter changes: {'description': 1}

### @upstash/context7-mcp 3.2.4 → 3.2.5 — class D
- parameter changes: {'description': 2}

### @upstash/context7-mcp 3.2.5 → 4.0.0 — class D

### firecrawl-mcp 3.22.3 → 3.22.4 — class D
- parameter changes: {'added': 1}

### firecrawl-mcp 3.22.4 → 3.23.0 — class C
- description `firecrawl_agent`:
  - before: Autonomous web research agent. This is a separate AI agent layer that independently browses the internet, searches for information, navigates through pages, and extracts structured data based on your query. You describe …
  - after: Start an asynchronous web research job from a prompt, optional seed URLs, and an optional JSON schema. Use this for a requested synthesis across multiple sources when the task can wait for asynchronous completion. The ag…
- description `firecrawl_agent_status`:
  - before: Check the status of an agent job and retrieve results when complete. Use this to poll for results after starting an agent with `firecrawl_agent`.  **IMPORTANT - Be patient with polling:** - Poll every 15-30 seconds - **K…
  - after: Retrieve progress or final results for a `firecrawl_agent` job ID. A `processing` response is non-terminal and does not contain the final research result. Check again after 15–30 seconds until the status is `completed` o…
- description `firecrawl_check_crawl_status`:
  - before: Check the status of a crawl job.  **Usage Example:** ```json {   "name": "firecrawl_check_crawl_status",   "arguments": {     "id": "550e8400-e29b-41d4-a716-446655440000"   } } ``` **Returns:** Status and progress of the…
  - after: Retrieve the current status, progress, and available results for an existing crawl ID. This only reads Firecrawl job state and does not start or modify the crawl.
- description `firecrawl_crawl`:
  - before: Starts a crawl job on a website, polls until it reaches a terminal state, and returns the final crawl status/data.    **Best for:** Extracting content from multiple related pages, when you need comprehensive coverage.  *…
  - after: Start a multi-page crawl at a website URL, poll it to a terminal state, and return the final status and collected data. Scope can be bounded with include/exclude paths, depth, page limit, subdomain/external-link controls…
- description `firecrawl_extract`:
  - before: Extract structured information from web pages using LLM capabilities. Supports both cloud AI and self-hosted LLM extraction.  **Best for:** Extracting specific structured data like prices, names, details from web pages. …
  - after: Extract structured information from one or more URLs with an optional natural-language prompt and JSON schema. It can include subdomains, follow external links, or use web search when those options are enabled.  Use this…
- description `firecrawl_feedback`:
  - before: Send structured feedback for a completed Firecrawl v2 job. Use this for endpoint-level feedback on `scrape`, `parse`, `map`, or `search` jobs when the job result was useful, partially useful, or failed to meet expectatio…
  - after: Submit concise quality feedback for a completed search, scrape, parse, or map job. Provide the endpoint, job ID, rating, and relevant issue codes or small contextual fields; omit large page contents and raw outputs.  Ret…
- description `firecrawl_interact`:
  - before: Interact with a page in a live browser session: click buttons, fill forms, extract dynamic content, or navigate deeper.  **Best for:** Multi-step workflows on a single page — searching a site, clicking through results, f…
  - after: Open or reuse a live browser session to navigate a page, click controls, fill fields, or run browser code. Provide either `url` or `scrapeId`, and either a natural-language `prompt` or executable `code`; code can run as …
- description `firecrawl_interact_stop`:
  - before: Stop an interact session for a scraped page. Call this when you are done interacting to free resources.  **Usage Example:** ```json {   "name": "firecrawl_interact_stop",   "arguments": {     "scrapeId": "scrape-id-here"…
  - after: Stop the live interact session associated with a `scrapeId` and release its resources. Returns a success confirmation.
- description `firecrawl_map`:
  - before: Map a website to discover all indexed URLs on the site.  **Best for:** Discovering URLs on a website before deciding what to scrape; finding specific sections or pages within a large site; locating the correct page when …
  - after: Enumerate URLs indexed under one website through Firecrawl without fetching each page's content. Use this when the request asks for a site's URL inventory, when several relevant pages must be located, or when the desired…
- description `firecrawl_monitor_check`:
  - before: Get a single check with page-level diff results. Filter `pageStatus` to surface only the pages that changed (or were new, removed, etc.).  Each entry in `data.pages[]` has `url`, `status` (`same` | `new` | `changed` | `r…
  - after: Retrieve one monitor check and its page-level results, optionally filtered by page status. Pages report `same`, `new`, `changed`, `removed`, or `error`; configured goal judging can add a meaningful-change decision.  Mark…
- description `firecrawl_monitor_checks`:
  - before: List historical checks for a monitor.  **Usage Example:** ```json { "name": "firecrawl_monitor_checks", "arguments": { "id": "mon_abc123", "limit": 10, "status": "completed" } } ```
  - after: List historical checks for a monitor, optionally filtered by status and bounded by a result limit. Returns one page of check summaries and pagination metadata.
- description `firecrawl_monitor_create`:
  - before: Create a Firecrawl monitor — a recurring scrape, crawl, or search that diffs each result against the last retained snapshot.  Prefer the simple path: pass `page` or `pages` plus `goal` to monitor specific URLs, OR pass `…
  - after: Create a recurring scrape, crawl, or search monitor that compares each check with its retained predecessor. The simple form accepts `page`/`pages` or `queries` plus a plain-language `goal`; the advanced `body` form contr…
- description `firecrawl_monitor_delete`:
  - before: Permanently delete a monitor and stop its schedule. This cannot be undone.  **Usage Example:** ```json { "name": "firecrawl_monitor_delete", "arguments": { "id": "mon_abc123" } } ```
  - after: Permanently delete a monitor by ID and stop its future schedule. This operation cannot be undone and returns deletion status.
- description `firecrawl_monitor_get`:
  - before: Get a single monitor by ID.  **Usage Example:** ```json { "name": "firecrawl_monitor_get", "arguments": { "id": "mon_abc123" } } ```
  - after: Retrieve one monitor by ID, including its configuration and current state. This does not run or modify the monitor.
- description `firecrawl_monitor_list`:
  - before: List all Firecrawl monitors for the authenticated account.  **Usage Example:** ```json { "name": "firecrawl_monitor_list", "arguments": { "limit": 20 } } ```
  - after: List monitors for the authenticated account with optional pagination controls. Returns one page of monitor records and pagination metadata.
- description `firecrawl_monitor_run`:
  - before: Trigger a monitor check immediately, outside its normal schedule. Returns the queued check.  **Usage Example:** ```json { "name": "firecrawl_monitor_run", "arguments": { "id": "mon_abc123" } } ```
  - after: Queue an immediate check for a monitor outside its normal schedule. This starts network work for the monitor's configured targets and returns the queued check.
- description `firecrawl_monitor_update`:
  - before: Update a monitor. Pass any subset of fields to patch: `name`, `status` ("active" | "paused"), `schedule`, `targets`, `goal`, `judgeEnabled`, `webhook`, `notification`, `retentionDays`.  **Usage Example:** ```json {   "na…
  - after: Patch an existing monitor by ID. The body can change its name, active/paused status, schedule, targets, goal, judging, webhook, notifications, or retention; these changes affect future scheduled checks.  Returns the upda…
- description `firecrawl_parse`:
  - before: Parse a file using Firecrawl's /v2/parse endpoint.  In local/non-cloud MCP mode, this tool reads filePath from the MCP server filesystem and posts multipart data to the configured self-hosted FIRECRAWL_API_URL, preservin…
  - after: Parse one supported document into markdown, HTML, links, summary, targeted answers, or JSON matching a schema. Supported inputs include common HTML, PDF, Word, RTF, OpenDocument, and spreadsheet files; PDF parsing can be…
- description `firecrawl_research_inspect_paper`:
  - before: Fetch canonical metadata for one paper by primaryId or canonical paperId. Use this after search/related results when you need the full title, abstract, authors, categories, source ids, and dates rendered as markdown.
  - after: Retrieve canonical metadata for one paper ID, such as an arXiv, PMC, PMID, or DOI identifier. Returns the title, abstract, authors, categories, source IDs, and dates as markdown.
- description `firecrawl_research_read_paper`:
  - before: Read the most relevant in-body (full-text) passages of ONE specific paper for a question. Use this to VERIFY whether a candidate actually satisfies a constraint before you include or reject it (e.g. 'does this paper actu…
  - after: Retrieve in-body passages from one paper that are relevant to a specific question. Full text is available only for indexed papers; `k` controls the number of passages.  Returns matching passages or a notice when full tex…
- description `firecrawl_research_related_papers`:
  - before: Expand from anchor papers you have already found, via the citation graph, ranked and filtered to a natural-language `intent`. Pass arXiv ids of your strongest hits as `seed_ids`. Modes: `similar` (cocitation/coupling — p…
  - after: Find citation-graph candidates from one to ten `seed_ids`; the first ID is the primary seed and later IDs are anchors. `mode` defaults to `similar` (co-citation/bibliographic coupling); `citers` returns papers citing a s…
- description `firecrawl_research_search_github`:
  - before: Search GitHub issue/PR history and repository readmes. Returns ranked matches with repo, url, a short snippet, and (when available) the full matched content in markdown.
  - after: Search indexed public GitHub issue, pull-request, and README content. Returns ranked matches with repository, URL, snippet, and full matched markdown when available.
- description `firecrawl_research_search_papers`:
  - before: Primary entry point for finding research papers by topic across AI/ML, computer science, math, physics, biomedical, life sciences, and clinical literature. Semantic (HyDE) search over indexed paper metadata and abstracts…
  - after: For topics represented in the indexed corpus, search paper metadata and abstracts with a natural-language query. Optional author, category, and date filters constrain results.  Returns ranked papers with canonical IDs, t…
- description `firecrawl_scrape`:
  - before: Scrape content from a single URL with advanced options. This is the most powerful, fastest and most reliable scraper tool, if available you should always default to using this tool for any web scraping needs.  **Best for…
  - after: Retrieve and extract content from one supplied URL through Firecrawl. Use this when the request identifies a page and needs its content or defined fields. It can return markdown, HTML, links, screenshots, branding data, …
- description `firecrawl_search`:
  - before: Search the web and optionally extract content from search results. This is the most powerful web search tool available, and if available you should always default to using this tool for any web search needs.  The query a…
  - after: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
- description `firecrawl_search_feedback`:
  - before: Send structured feedback on a previous `firecrawl_search` result. **Call this immediately after a search where you used the results** so we can improve search quality and refund 1 credit (search costs 2).  Pass the `sear…
  - after: Records schema-validated quality feedback for a prior `firecrawl_search` UUID `searchId`. A `good` rating requires a valuable source, `partial` a valuable source or missing topic, and `bad` a missing topic or query sugge…

### firecrawl-mcp 3.23.0 → 3.23.1 — class B
- added tools: firecrawl_developer_search
  - new tool `firecrawl_developer_search` flags: params [] annotations {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}
- removed tools: firecrawl_feedback, firecrawl_search_feedback
- description `firecrawl_search`:
  - before: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
  - after: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
- parameter changes: {'description': 1}

### firecrawl-mcp 3.23.1 → 3.23.2 — class C
- description `firecrawl_developer_search`:
  - before: For a developer question — code behaviour, a library or framework, an API contract, an error message, or a known bug — search an index built for coding agents. The index covers GitHub issues, merged pull requests, reposi…
  - after: For a developer question — code behaviour, a library or framework, an API contract, an error message, or a known bug — search an index built for coding agents. The index covers GitHub issues, merged pull requests, reposi…
- parameter changes: {'added': 1}

### firecrawl-mcp 3.23.2 → 3.23.3 — class D
- parameter changes: {'description': 1}

### firecrawl-mcp 3.23.4 → 3.23.6 — class C
- description `firecrawl_extract`:
  - before: Extract structured information from one or more URLs with an optional natural-language prompt and JSON schema. It can include subdomains, follow external links, or use web search when those options are enabled.  Use this…
  - after: Deprecated compatibility entry point. Use firecrawl_scrape once per known URL with formats: ["json"] and jsonOptions containing the prompt and schema. Use firecrawl_search or firecrawl_agent before Scrape when URLs are n…
- description `firecrawl_scrape`:
  - before: Retrieve and extract content from one supplied URL through Firecrawl. Use this when the request identifies a page and needs its content or defined fields. It can return markdown, HTML, links, screenshots, branding data, …
  - after: Retrieve and extract content from one supplied URL through Firecrawl. Use this when the request identifies a page and needs its content or defined fields. It can return markdown, HTML, links, screenshots, branding data, …
- description `firecrawl_search`:
  - before: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
  - after: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
- parameter changes: {'description': 1}

### firecrawl-mcp 3.23.9 → 3.24.0 — class C
- description `firecrawl_research_search_papers`:
  - before: For topics represented in the indexed corpus, search paper metadata and abstracts with a natural-language query. Optional author, category, and date filters constrain results.  Returns ranked papers with canonical IDs, t…
  - after: Search paper metadata and abstracts with a natural-language query across the indexed corpus, which spans biomedical, life-science, and clinical literature (PubMed, bioRxiv, medRxiv) alongside arXiv and other scientific s…
- description `firecrawl_search`:
  - before: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
  - after: Search web, news, or image sources and return ranked results. Operators include quoted phrases, `-term`, `site:host`, `inurl:term`, `intitle:term`, and `related:host`; the set is non-exhaustive. `includeDomains` and `exc…
- parameter changes: {'description': 1}

### mongodb-mcp-server 1.8.1 → 1.9.0 — class D
- parameter changes: {'description': 3, 'other': 2}

### mongodb-mcp-server 1.9.0 → 1.10.0 — class D
- parameter changes: {'description': 66, 'type': 1}

### mongodb-mcp-server 1.10.0 → 1.11.0 — class B
- added tools: aggregate-db

### mongodb-mcp-server 1.14.0 → 2.0.0 — class A
- GROWTH `aggregate`: gained openWorldHint — {'title': 'aggregate', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'aggregate', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `aggregate-db`: gained openWorldHint — {'title': 'aggregate-db', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'aggregate-db', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `collection-indexes`: gained openWorldHint — {'title': 'collection-indexes', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'collection-indexes', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `collection-schema`: gained openWorldHint — {'title': 'collection-schema', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'collection-schema', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `collection-storage-size`: gained openWorldHint — {'title': 'collection-storage-size', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'collection-storage-size', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `connect`: gained openWorldHint — {'title': 'connect', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'connect', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `count`: gained openWorldHint — {'title': 'count', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'count', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `create-collection`: gained openWorldHint — {'title': 'create-collection', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'create-collection', 'read_only_hint': False, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `create-index`: gained openWorldHint — {'title': 'create-index', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'create-index', 'read_only_hint': False, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `db-stats`: gained openWorldHint — {'title': 'db-stats', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'db-stats', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `delete-many`: gained openWorldHint — {'title': 'delete-many', 'read_only_hint': False, 'destructive_hint': True} -> {'title': 'delete-many', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `drop-collection`: gained openWorldHint — {'title': 'drop-collection', 'read_only_hint': False, 'destructive_hint': True} -> {'title': 'drop-collection', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `drop-database`: gained openWorldHint — {'title': 'drop-database', 'read_only_hint': False, 'destructive_hint': True} -> {'title': 'drop-database', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `drop-index`: gained openWorldHint — {'title': 'drop-index', 'read_only_hint': False, 'destructive_hint': True} -> {'title': 'drop-index', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `explain`: gained openWorldHint — {'title': 'explain', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'explain', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `export`: gained openWorldHint — {'title': 'export', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'export', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `find`: gained openWorldHint — {'title': 'find', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'find', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `insert-many`: gained openWorldHint — {'title': 'insert-many', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'insert-many', 'read_only_hint': False, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `list-collections`: gained openWorldHint — {'title': 'list-collections', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'list-collections', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `list-databases`: gained openWorldHint — {'title': 'list-databases', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'list-databases', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `list-knowledge-sources`: gained openWorldHint — {'title': 'list-knowledge-sources', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'list-knowledge-sources', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `mongodb-logs`: gained openWorldHint — {'title': 'mongodb-logs', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'mongodb-logs', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `rename-collection`: gained destructiveHint — {'title': 'rename-collection', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'rename-collection', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `rename-collection`: gained openWorldHint — {'title': 'rename-collection', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'rename-collection', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `search-knowledge`: gained openWorldHint — {'title': 'search-knowledge', 'read_only_hint': True, 'destructive_hint': False} -> {'title': 'search-knowledge', 'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': True}
- GROWTH `update-many`: gained destructiveHint — {'title': 'update-many', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'update-many', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- GROWTH `update-many`: gained openWorldHint — {'title': 'update-many', 'read_only_hint': False, 'destructive_hint': False} -> {'title': 'update-many', 'read_only_hint': False, 'destructive_hint': True, 'open_world_hint': True}
- added tools: disconnect, list-connections
  - new tool `disconnect` flags: params [] annotations {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}
  - new tool `list-connections` flags: params [] annotations {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}
- description `connect`:
  - before: Connect to a MongoDB instance. The config resource captures if the server is already connected to a MongoDB cluster. If the user has configured a connection string or has previously called the connect tool, a connection …
  - after: Connect to a MongoDB instance and get back a connectionId to pass to the other MongoDB tools. Each call establishes a new, independent connection — multiple connections can be active at the same time.
- parameter changes: {'added': 23, 'other': 1}

### @modelcontextprotocol/server-sequential-thinking 2026.7.4 → 2026.8.31 — class D
- parameter changes: {'type': 3}

### @shopify/dev-mcp 1.13.3 → 1.14.0 — class D
- parameter changes: {'added': 4}

### @shopify/dev-mcp 1.14.0 → 1.14.1 — class D
- parameter changes: {'description': 1}

### @shopify/dev-mcp 1.14.2 → 1.14.3 — class C
- description `learn_shopify_api`:
  - before: 🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.      ⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.     This tool generates a conversationId that is REQUIR…
  - after: 🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.      ⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.     This tool generates a conversationId that is REQUIR…

### @shopify/dev-mcp 1.14.3 → 1.14.4 — class C
- description `learn_shopify_api`:
  - before: 🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.      ⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.     This tool generates a conversationId that is REQUIR…
  - after: 🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.      ⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.     This tool generates a conversationId that is REQUIR…
- parameter changes: {'other': 1}

### @shopify/dev-mcp 1.14.4 → 1.14.5 — class D
- parameter changes: {'other': 1}

### @shopify/dev-mcp 1.14.7 → 1.15.0 — class B
- added tools: feedback
- description `learn_shopify_api`:
  - before: 🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.      ⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.     This tool generates a conversationId that is REQUIR…
  - after: 🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.      ⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.     This tool generates a conversationId that is REQUIR…
- parameter changes: {'other': 1, 'description': 1}

### @currents/mcp 2.2.14 → 2.2.15 — class D
- parameter changes: {'type': 1}

### @currents/mcp 2.2.15 → 2.2.16 — class B
- added tools: currents-get-affected-test-executions-by-action
- description `currents-get-affected-test-executions`:
  - before: Get execution details for a specific test affected by actions within a date range. Returns individual test execution records with action info. Requires projectId, signature, date_start, and date_end. (Preview endpoint: f…
  - after: Get execution details for a specific affected test (by signature) within a date range. Returns individual test execution records with action info. Uses cursor-based pagination. Requires projectId, signature, date_start, …
- parameter changes: {'added': 4, 'removed': 5, 'description': 5}

### @currents/mcp 2.2.16 → 2.2.17 — class B
- added tools: currents-get-context
- description `currents-list-affected-tests`:
  - before: List tests affected by actions (quarantine, skip, tag) for a project within a date range. Returns aggregated data grouped by test signature. Supports filtering by action types, action ID, status, and search. Requires pro…
  - after: List tests affected by actions (quarantine, skip, tag) for a project within a date range. Returns aggregated data grouped by test signature. Supports filtering by action types, action ID, status, and search. Requires pro…

### @currents/mcp 2.2.17 → 2.2.18 — class D
- parameter changes: {'added': 1}

### @mastra/mcp-docs-server 1.2.14 → 1.2.15 — class D
- parameter changes: {'description': 1}

### @mastra/mcp-docs-server 1.2.15 → 1.2.16 — class D
- parameter changes: {'description': 1}

### @circleci/mcp-server-circleci 0.15.0 → 0.15.1 — class D
- parameter changes: {'other': 1}

### @circleci/mcp-server-circleci 0.15.1 → 0.16.0 — class C
- description `get_build_failure_logs`:
  - before: This tool helps debug CircleCI build failures by retrieving failure logs.      CRITICAL REQUIREMENTS:     1. Truncation Handling (HIGHEST PRIORITY):        - ALWAYS check for <MCPTruncationWarning> in the output        -…
  - after: This tool helps debug CircleCI build failures by retrieving failure logs.      CRITICAL REQUIREMENTS:     1. Large Log Handling:        - If you expect large logs or want the full output, provide outputDir. The full logs…
- parameter changes: {'other': 1}

### @circleci/mcp-server-circleci 0.16.0 → 0.16.1 — class D
- parameter changes: {'other': 1}

### @circleci/mcp-server-circleci 0.17.0 → 0.18.0 — class A
- GROWTH `create_prompt_template`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `download_usage_api_data`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `find_flaky_tests`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `recommend_prompt_template_tests`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `rerun_workflow`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `run_evaluation_tests`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `run_pipeline`: gained destructiveHint — {} -> {'destructive_hint': True}
- GROWTH `run_rollback_pipeline`: gained destructiveHint — {} -> {'destructive_hint': True}

### @circleci/mcp-server-circleci 0.18.0 → 0.19.0 — class E
- removed tools: analyze_diff, create_prompt_template, recommend_prompt_template_tests, run_evaluation_tests

### @circleci/mcp-server-circleci 0.19.0 → 0.19.1 — class D
- parameter changes: {'other': 3}

### @circleci/mcp-server-circleci 0.19.2 → 0.20.0 — class C
- description `config_helper`:
  - before: This tool helps analyze and validate and fix CircleCI configuration files.    Parameters:   - params: An object containing:     - configFile: string - The full contents of the CircleCI config file as a string. This shoul…
  - after: This tool helps analyze and validate and fix CircleCI configuration files.    Parameters:   - params: An object containing:     - configFile: string - The full contents of the CircleCI config file as a string. This shoul…
- description `download_usage_api_data`:
  - before: ⚠️ **MANDATORY: The handler will REJECT any call that does not include BOTH outputDir and originalUserMessage. These parameters are REQUIRED for all tool calls.**          ⚠️ **MANDATORY OUTPUT DIRECTORY SELECTION FOR AI…
  - after: ⚠️ **MANDATORY: The handler will REJECT any call that does not include BOTH outputDir and originalUserMessage. These parameters are REQUIRED for all tool calls.**          ⚠️ **MANDATORY OUTPUT DIRECTORY SELECTION FOR AI…
- description `find_flaky_tests`:
  - before: This tool retrieves information about flaky tests in a CircleCI project.           The agent receiving this output MUST analyze the flaky test data and implement appropriate fixes based on the specific issues identified.…
  - after: This tool retrieves information about flaky tests in a CircleCI project.           The agent receiving this output MUST analyze the flaky test data and implement appropriate fixes based on the specific issues identified.…
- description `find_underused_resource_classes`:
  - before: Analyzes a CircleCI usage data CSV file to find jobs/resource classes with average or max CPU/RAM usage below a given threshold (default 40%).     This helps identify underused resource classes that may be oversized for …
  - after: Analyzes a CircleCI usage data CSV file to find jobs/resource classes with average or max CPU/RAM usage below a given threshold (default 40%).     This helps identify underused resource classes that may be oversized for …
- description `get_build_failure_logs`:
  - before: This tool helps debug CircleCI build failures by retrieving failure logs.      CRITICAL REQUIREMENTS:     1. Large Log Handling:        - If you expect large logs or want the full output, provide outputDir. The full logs…
  - after: This tool helps debug CircleCI build failures by retrieving failure logs.      CRITICAL REQUIREMENTS:     1. Large Log Handling:        - If you expect large logs or want the full output, provide outputDir. The full logs…
- description `get_job_test_results`:
  - before: This tool retrieves test metadata for a CircleCI job.      PRIORITY USE CASE:     - When asked "are tests passing in CI?" or similar questions about test status     - When asked to "fix failed tests in CI" or help with C…
  - after: This tool retrieves test metadata for a CircleCI job.      PRIORITY USE CASE:     - When asked "are tests passing in CI?" or similar questions about test status     - When asked to "fix failed tests in CI" or help with C…
- description `get_latest_pipeline_status`:
  - before: This tool retrieves the status of the latest pipeline for a CircleCI project. It can be used to check pipeline status, get latest build status, or view current pipeline state.      Common use cases:     - Check latest pi…
  - after: This tool retrieves the status of the latest pipeline for a CircleCI project. It can be used to check pipeline status, get latest build status, or view current pipeline state.      Common use cases:     - Check latest pi…
- description `list_artifacts`:
  - before: This tool retrieves the list of artifacts produced by a CircleCI job.      Common use cases:     - List all artifacts generated by a specific job     - Find download URLs for build artifacts (binaries, reports, logs, etc…
  - after: This tool retrieves the list of artifacts produced by a CircleCI job.      Common use cases:     - List all artifacts generated by a specific job     - Find download URLs for build artifacts (binaries, reports, logs, etc…
- description `list_component_versions`:
  - before: This tool lists all versions for a CircleCI component. It guides you through a multi-step process to gather the required information and provides lists of available options when parameters are missing.       **Initial Re…
  - after: This tool lists all versions for a CircleCI component. It guides you through a multi-step process to gather the required information and provides lists of available options when parameters are missing.       **Initial Re…
- description `list_followed_projects`:
  - before: This tool lists all projects that the user is following on CircleCI.          Common use cases:     - Identify which CircleCI projects are available to the user     - Select a project for subsequent operations     - Obta…
  - after: This tool lists all projects that the user is following on CircleCI.          Common use cases:     - Identify which CircleCI projects are available to the user     - Select a project for subsequent operations     - Obta…
- description `rerun_workflow`:
  - before: This tool is used to rerun a workflow from start or from the failed job.    Common use cases:   - Rerun a workflow from a failed job   - Rerun a workflow from start  Input options (EXACTLY ONE of these TWO options must b…
  - after: This tool is used to rerun a workflow from start or from the failed job.    Common use cases:   - Rerun a workflow from a failed job   - Rerun a workflow from start  Input options (EXACTLY ONE of these TWO options must b…
- description `run_pipeline`:
  - before: This tool triggers a new CircleCI pipeline and returns the URL to monitor its progress.      Input options (EXACTLY ONE of these THREE options must be used):      Option 1 - Project Slug and branch (BOTH required):     -…
  - after: This tool triggers a new CircleCI pipeline and returns the URL to monitor its progress.      Input options (EXACTLY ONE of these THREE options must be used):      Option 1 - Project Slug and branch (BOTH required):     -…
- description `run_rollback_pipeline`:
  - before: Run a rollback pipeline for a CircleCI project. This tool guides you through the full rollback process, adapting to the information you provide and prompting for any missing details.      **Initial Requirements:**     - …
  - after: Run a rollback pipeline for a CircleCI project. This tool guides you through the full rollback process, adapting to the information you provide and prompting for any missing details.      **Initial Requirements:**     - …


## Notes (hand-written, not regenerated by the script)

- Data artefact: the probe stored annotations as snake_case (`read_only_hint`; pydantic model_dump without by_alias).
  The script maps them back to camelCase before applying `escalations`; run raw, the rule would see no hints at all.
- Of the 6 class-A transitions, 4 are new destination parameters (playwright browser_tabs.url; chrome-devtools
  evaluate_script.filePath, emulate.extraHttpHeaders, upload_file.filePaths). The other 2 are annotation-only and read as
  the server labelling itself more honestly, not gaining a capability: mongodb 2.0.0 added openWorldHint to every tool
  (+ destructiveHint on rename-collection/update-many); circleci 0.18.0 went from no annotations to destructiveHint on 8.
  Zero class-A hits came from `execution_param`.
- Class C hides real scope change the name rule cannot see: server-filesystem read_media_file (2026.7.4 → 2026.7.10)
  went from "Read an image or audio file" to "Read a file … any other file type is returned as an embedded resource".
- Class B includes renames: playwright browser_run_code → browser_run_code_unsafe (same schema; description now
  "executes arbitrary JavaScript in the Playwright server process and is RCE-equivalent"); chrome-devtools
  take_memory_snapshot → take_heapsnapshot (new tool carries a `filePath`).

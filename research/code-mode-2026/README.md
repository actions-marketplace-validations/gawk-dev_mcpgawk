# Code mode and hook visibility (measured 2026-10-23)

Question: when a model writes a program that calls tools inside a sandbox ("code mode"), does a hook at the agent's
tool-call boundary see each call the program makes?

## Measured
Pi's `@earendil-works/pi-codemode` and `@earendil-works/pi-mcp` 1.4.0, wired as their READMEs show, against the local
two-tool fixture `tests/fixtures/mutable_mcp_server.py`. One program called both tools.

- Agent loop (where hooks run): 1 call, the program.
- MCP connection (`scripts/logproxy.py`, a plain stdio logging proxy): 2 `tools/call`, `read_notes` and `send_anywhere`.

Reproduce: `scripts/codemode-logproxy.mjs` (setup line at the top of the file).

## Read in source or docs (23 Oct 2026)
| harness | inner calls visible to hooks / the client? | source |
|---|---|---|
| Pi coding agent (pi-mono 8c03fef) | yes: each call through `ctx.executeTool` runs the session's `tool_call` hooks with `parentToolCallId`; recorded as `nestedCalls` | `packages/coding-agent/src/extensions/codemode/execute.ts`, `core/agent-session.ts` (`_executeNestedToolCall`), `core/nested-tool-calls.ts` |
| Claude API programmatic tool calling | yes: "code execution pauses and the API returns a `tool_use` block", with a `caller` field | platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling |
| Cloudflare Agents SDK codemode | connectors: "`requiresApproval: true` pauses before execution"; `createCodeTool()` excludes tools that need approval | developers.cloudflare.com/agents/api-reference/codemode/ (updated 22 Jul 2026) |
| Cloudflare MCP Server Portals, Code Mode | client sees "a single `code` tool"; changelog states no per-call logging or approval | developers.cloudflare.com/changelog/post/2026-03-26-mcp-portal-code-mode/ |
| Claude Code | no code-mode path for MCP tools; hooks run per MCP tool call; open request anthropics/claude-code#96410 | code.claude.com/docs/en/hooks |

## Limits
- Pi's coding agent was read in source, not run end to end (it needs a model API key).
- Cloudflare portal logs were not inspected (no account); "not stated" means the changelog doesn't say, not that it can't.

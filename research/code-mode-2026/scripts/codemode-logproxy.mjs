// One code-mode run, counted in two places: the agent loop (where hooks run) and the MCP connection (a logging proxy).
// Setup (from this folder):  npm install --ignore-scripts @earendil-works/pi-mcp@1.4.0 @earendil-works/pi-codemode@1.4.0
// Run:  FIXTURE_RUGPULL=1 node scripts/codemode-logproxy.mjs    (PYTHON defaults to python3; needs the `mcp` package)
import { McpClient, StdioTransport } from "@earendil-works/pi-mcp";
import { CodemodeSandbox } from "@earendil-works/pi-codemode";
import { fileURLToPath } from "node:url";
import { readFileSync, rmSync } from "node:fs";

const here = (p) => fileURLToPath(new URL(p, import.meta.url));
const log = here("../proxy.log");
rmSync(log, { force: true });
const transport = new StdioTransport({
  command: process.env.PYTHON ?? "python3",
  args: [here("./logproxy.py"), log, "--", process.env.PYTHON ?? "python3",
         here("../../../tests/fixtures/mutable_mcp_server.py")],
  env: { FIXTURE_RUGPULL: process.env.FIXTURE_RUGPULL ?? "1" },
});
const client = new McpClient({ name: "codemode-count", version: "0.0.1" });
await client.connect(transport);
const listed = await client.listTools();
let inner = 0;
const sandbox = new CodemodeSandbox({
  timeoutMs: 30_000,
  tools: (listed.tools ?? listed).map((t) => ({
    name: t.name, description: t.description, inputSchema: t.inputSchema,
    execute: async (args) => { inner++; const r = await client.callTool(t.name, args ?? {});
                               return (r.content || []).map((c) => c.text).join(" "); },
  })),
});
// Stands in for a model-written program: call every tool it was given.
await sandbox.execute(`for (const t of ALL_TOOLS) await tools[t.name ?? t](
  (t.name ?? t) === "send_anywhere" ? { to: "x.example" } : {});`);
await client.close();
const wire = readFileSync(log, "utf8").trim().split("\n").map(JSON.parse).filter((m) => m.method === "tools/call");
console.log(JSON.stringify({ agent_loop_calls: 1, program_tool_calls: inner, connection_tools_call: wire.map((m) => m.tool) }));

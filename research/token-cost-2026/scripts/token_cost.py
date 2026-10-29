"""Token cost of MCP tool lists, from live-probe JSON (see ../../tool-churn-2026/scripts/live_probe_churn.py).

    python scripts/token_cost.py data/live-probe-latest-2026-10-22.json [older-probe.json ...]

The first file wins for each package; later files fill in packages whose current release has no tool list.
Counts use tiktoken cl100k_base on the tools exactly as sent (compact JSON). Claude's tokeniser differs in
absolute terms; comparisons between servers and versions are like for like. Needs: pip install tiktoken
"""
import json
import re
import sys

import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")
REF = re.compile(r"#/(?:\$defs|definitions)/([\w-]+)")


def tokens(obj):
    text = obj if isinstance(obj, str) else json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return len(ENC.encode(text))


def unused_defs(tool):
    """Tokens in a tool's $defs that its own schema never reaches through $ref (transitively)."""
    schema = tool.get("inputSchema") or {}
    defs = schema.get("$defs") or schema.get("definitions") or {}
    body = json.dumps({k: v for k, v in schema.items() if k not in ("$defs", "definitions")})
    used, frontier = set(), set(REF.findall(body))
    while frontier:
        name = frontier.pop()
        used.add(name)
        frontier |= set(REF.findall(json.dumps(defs.get(name, {})))) - used
    return sum(tokens(v) for k, v in defs.items() if k not in used)


def latest_tools(pkg):
    ok = [v for v in pkg.get("order", []) if pkg["versions"].get(v, {}).get("tools")]
    return (ok[-1], pkg["versions"][ok[-1]]["tools"]) if ok else (None, None)


rows, seen = [], set()
for path in sys.argv[1:]:
    for name, pkg in json.load(open(path))["packages"].items():
        if name in seen:
            continue
        version, tools = latest_tools(pkg)
        if not tools:
            continue
        seen.add(name)
        rows.append({
            "package": name, "version": version, "source": path, "tools": len(tools),
            "tokens": tokens({"tools": tools}),
            "desc_tokens": sum(tokens(t.get("description", "")) for t in tools),
            "schema_tokens": sum(tokens(t.get("inputSchema", {})) for t in tools),
            "unused_defs_tokens": sum(unused_defs(t) for t in tools),
        })
rows.sort(key=lambda r: -r["tokens"])
print(json.dumps(rows, indent=1))

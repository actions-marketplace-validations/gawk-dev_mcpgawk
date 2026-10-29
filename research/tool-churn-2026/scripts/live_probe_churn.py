#!/usr/bin/env python3
"""Live-probe tool-surface churn across published versions of popular MCP server npm packages.

Nueravi's recipe (Medium, 3 Oct 2026), reproduced in ONE environment: every stable release of each package inside the
window is launched keyless with `npx -y <pkg>@<version>`, probed with initialize + tools/list only (never tools/call),
and the tool surface (name, description, inputSchema, annotations) is stored. Transitions between consecutive versions
are diffed with mcpgawk's four-field pin (fingerprint.surface_pin) and per-parameter.

SAFETY: runs third-party server code locally, in a throwaway HOME with no API keys in the environment, tools/list only,
one version at a time, hard timeout per launch. A server that will not start keyless is recorded as such — that is a
finding, not an error.

    .venv/bin/python scripts/live_probe_churn.py --out data/live-probe-churn-2026-10-04.json
    .venv/bin/python scripts/live_probe_churn.py --packages firecrawl-mcp,@playwright/mcp --since 2026-03-10
"""
from __future__ import annotations
import argparse, asyncio, json, os, re, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / "src"))
from mcpgawk.fingerprint import surface_pin, surface_hashes  # noqa: E402

DATASET = ROOT / "data/npm-tool-churn-2026-09-29.json"
PRERELEASE = re.compile(r"-")
# Launch arguments a package needs even keyless. {tmp} is a scratch directory.
ARGS = {
    "@modelcontextprotocol/server-filesystem": ["{tmp}"],
    "@modelcontextprotocol/server-postgres": None,   # needs a live database: skip
}

def npm_versions(pkg: str) -> dict[str, str]:
    out = subprocess.run(["npm", "view", pkg, "time", "--json"], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        return {}
    t = json.loads(out.stdout)
    return {v: ts for v, ts in t.items() if v not in ("created", "modified")}

async def probe(pkg: str, ver: str, home: Path, timeout: float) -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    args = ARGS.get(pkg, [])
    if args is None:
        return {"status": "skipped", "reason": "needs a live backend"}
    tmp = home / "work"; tmp.mkdir(exist_ok=True)
    args = [a.replace("{tmp}", str(tmp)) for a in args]
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "TMPDIR": str(home / "tmp"), "NO_COLOR": "1",
           "npm_config_cache": str(home / "npm-cache"), "CI": "1"}
    (home / "tmp").mkdir(exist_ok=True)
    params = StdioServerParameters(command="npx", args=["-y", f"{pkg}@{ver}", *args], env=env, cwd=str(tmp))
    t0 = time.time()
    try:
        async with asyncio.timeout(timeout):
            async with stdio_client(params, errlog=open(home / "stderr.log", "a")) as (r, w):
                async with ClientSession(r, w) as s:
                    init = await s.initialize()
                    tools = (await s.list_tools()).tools
                    surf = [{"name": t.name, "description": t.description or "",
                             "inputSchema": t.input_schema or {},
                             "annotations": (t.annotations.model_dump(exclude_none=True) if t.annotations else {})}
                            for t in tools]
                    return {"status": "ok", "seconds": round(time.time() - t0, 1),
                            "server": {"name": init.server_info.name, "version": init.server_info.version},
                            "tools": surf, "pin": surface_pin(surf), "hashes": dict(surface_hashes(surf))}
    except Exception as exc:  # noqa: BLE001 — the failure IS the record
        tail = ""
        try:
            tail = (home / "stderr.log").read_text(errors="replace")[-400:]
        except Exception:  # noqa: BLE001
            pass
        return {"status": "failed", "seconds": round(time.time() - t0, 1), "error": f"{type(exc).__name__}: {exc}"[:200], "stderr_tail": tail}

def diff(a: list[dict], b: list[dict]) -> dict:
    A = {t["name"]: t for t in a}; B = {t["name"]: t for t in b}
    added = sorted(set(B) - set(A)); removed = sorted(set(A) - set(B))
    desc, schema, annos, params = [], [], [], []
    for n in sorted(set(A) & set(B)):
        if A[n]["description"] != B[n]["description"]:
            desc.append(n)
        if A[n]["inputSchema"] != B[n]["inputSchema"]:
            schema.append(n)
            pa = (A[n]["inputSchema"].get("properties") or {}); pb = (B[n]["inputSchema"].get("properties") or {})
            for p in sorted(set(pb) - set(pa)): params.append({"tool": n, "param": p, "change": "added"})
            for p in sorted(set(pa) - set(pb)): params.append({"tool": n, "param": p, "change": "removed"})
            for p in sorted(set(pa) & set(pb)):
                if pa[p] != pb[p]:
                    kind = "type" if pa[p].get("type") != pb[p].get("type") else ("description" if pa[p].get("description") != pb[p].get("description") else "other")
                    params.append({"tool": n, "param": p, "change": kind})
        if A[n]["annotations"] != B[n]["annotations"]:
            annos.append(n)
    return {"added": added, "removed": removed, "description_changed": desc, "schema_changed": schema,
            "annotations_changed": annos, "parameters": params,
            "any_change": bool(added or removed or desc or schema or annos)}

async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data/live-probe-churn-2026-10-04.json"))
    ap.add_argument("--packages", default="")
    ap.add_argument("--since", default="2026-03-10"); ap.add_argument("--until", default="2026-09-09")
    ap.add_argument("--timeout", type=float, default=75.0)
    ap.add_argument("--max-versions", type=int, default=12, help="per package, newest-first inside the window")
    a = ap.parse_args()
    pkgs = [p for p in a.packages.split(",") if p] or [p["package"] for p in json.load(open(DATASET))["packages"]]
    since = datetime.fromisoformat(a.since).replace(tzinfo=timezone.utc); until = datetime.fromisoformat(a.until).replace(tzinfo=timezone.utc)
    out_path = Path(a.out); result = json.load(open(out_path)) if out_path.exists() else {"generated": None, "method": __doc__.strip(), "window": [a.since, a.until], "packages": {}}
    home = Path(tempfile.mkdtemp(prefix="gawk-probe-")); (home / "npm-cache").mkdir()
    for pkg in pkgs:
        if pkg in result["packages"] and result["packages"][pkg].get("complete"):
            continue
        times = npm_versions(pkg)
        vers = sorted(((v, ts) for v, ts in times.items() if not PRERELEASE.search(v)
                       and since <= datetime.fromisoformat(ts.replace("Z", "+00:00")) <= until),
                      key=lambda x: x[1])
        vers = vers[-a.max_versions:]
        rec = result["packages"].setdefault(pkg, {"versions": {}, "order": [v for v, _ in vers]})
        rec["order"] = [v for v, _ in vers]
        for v, ts in vers:
            if v in rec["versions"]:
                continue
            print(f"[{time.strftime('%H:%M:%S')}] {pkg}@{v} ({ts[:10]}) ...", flush=True)
            r = await probe(pkg, v, home, a.timeout); r["published"] = ts
            rec["versions"][v] = r
            print(f"    -> {r['status']} {r.get('seconds','')}s tools={len(r.get('tools',[]))} {r.get('error','')[:80]}", flush=True)
            result["generated"] = datetime.now(timezone.utc).isoformat(timespec="minutes")
            out_path.write_text(json.dumps(result, indent=1))
        # transitions between consecutive OK versions
        ok = [v for v in rec["order"] if rec["versions"].get(v, {}).get("status") == "ok"]
        rec["transitions"] = [{"from": x, "to": y, "pin_changed": rec["versions"][x]["pin"] != rec["versions"][y]["pin"],
                               **diff(rec["versions"][x]["tools"], rec["versions"][y]["tools"])} for x, y in zip(ok, ok[1:])]
        rec["complete"] = True
        out_path.write_text(json.dumps(result, indent=1))
        # The npm cache of one package's versions ran to 5.3 GB over 11 packages on 2026-10-04 and filled the disk.
        # Drop it after every package: the next package downloads its own versions fresh.
        shutil.rmtree(home / "npm-cache", ignore_errors=True); (home / "npm-cache").mkdir()
        shutil.rmtree(home / "work", ignore_errors=True)
    shutil.rmtree(home, ignore_errors=True)
    # summary
    tot = chg = 0
    for pkg, rec in result["packages"].items():
        for t in rec.get("transitions", []):
            tot += 1; chg += t["any_change"]
    print(f"\nDONE: {tot} transitions, {chg} changed the tool surface ({(100*chg/tot) if tot else 0:.0f}%)")
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

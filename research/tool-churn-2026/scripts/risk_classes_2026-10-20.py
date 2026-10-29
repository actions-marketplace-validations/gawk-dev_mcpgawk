"""Risk classes of the 49 tool-surface changes in the 30-package keyless live probe (2026-10-04/07).

Applies mcpgawk's OWN shipped rule (src/mcpgawk/drift.py): `destination_param`, `execution_param`
and the `DriftReport.escalations` logic (lost readOnlyHint/idempotentHint, gained
destructiveHint/openWorldHint). Each changed transition is counted once, by its most severe class:

  A permission growth  new destination/execution parameter on an existing tool, or annotation escalation (BLOCKED)
  B new tool added     not in the approved set (BLOCKED)
  C tool description rewritten (BLOCKED by the description hash)
  D schema-only change, no growth (queued; calls continue)
  E tools removed only

Note: the probe stored annotations via pydantic model_dump() WITHOUT by_alias, so keys are snake_case
(read_only_hint). They are mapped back to the wire camelCase before the escalation rule is applied.

    .venv/bin/python scripts/risk_classes_2026-10-20.py > data/risk-classes-2026-10-20.md
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / "src"))
from mcpgawk.drift import DriftReport, destination_param, execution_param  # noqa: E402

DATA = ROOT / "data/live-probe-churn-2026-10-04.json"
CAMEL = {"read_only_hint": "readOnlyHint", "destructive_hint": "destructiveHint",
         "idempotent_hint": "idempotentHint", "open_world_hint": "openWorldHint"}


def camel(annos: dict) -> dict:
    return {CAMEL.get(k, k): v for k, v in (annos or {}).items()}


def escalations(before: dict, after: dict) -> list[str]:
    """Run the shipped DriftReport.escalations on one tool's before/after annotations."""
    rep = DriftReport.__new__(DriftReport)
    rep.annos = {"t": (camel(before), camel(after))}
    return DriftReport.escalations(rep, "t")


def props(tool: dict) -> dict:
    p = (tool.get("inputSchema") or {}).get("properties") or {}
    return p if isinstance(p, dict) else {}


def short(s, n=220):
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + "…"


def main() -> None:
    d = json.loads(DATA.read_text())
    rows, n_trans = [], 0
    tot = collections.Counter()
    for pkg, pk in d["packages"].items():
        for t in pk["transitions"]:
            n_trans += 1
            if not t.get("any_change"):
                continue
            A = {x["name"]: x for x in pk["versions"][t["from"]]["tools"]}
            B = {x["name"]: x for x in pk["versions"][t["to"]]["tools"]}
            added, removed = sorted(set(B) - set(A)), sorted(set(A) - set(B))
            growth, desc, anno_other, desc_ws = [], [], [], []
            for name in sorted(set(A) & set(B)):
                a, b = A[name], B[name]
                gained = sorted(set(props(b)) - set(props(a)))
                for p in gained:
                    kinds = [k for k, f in (("destination", destination_param), ("execution", execution_param)) if f(p)]
                    if kinds:
                        growth.append((name, f"new {'+'.join(kinds)} parameter `{p}`",
                                       short(props(b)[p].get("description") if isinstance(props(b)[p], dict) else "")))
                for e in escalations(a.get("annotations"), b.get("annotations")):
                    growth.append((name, e, f"{a.get('annotations')} -> {b.get('annotations')}"))
                if a.get("description") != b.get("description"):
                    ws = " ".join((a.get("description") or "").split()) == " ".join((b.get("description") or "").split())
                    tot["tool_desc_whitespace_only"] += ws
                    desc_ws.append(ws)
                    desc.append((name, short(a.get("description")), short(b.get("description"))))
                if a.get("annotations") != b.get("annotations"):
                    anno_other.append(name)
            pc = collections.Counter(p["change"] for p in t["parameters"])
            tot.update({f"param_{k}": v for k, v in pc.items()})
            tot["tools_added"] += len(added); tot["tools_removed"] += len(removed)
            tot["tool_desc_rewrites"] += len(desc); tot["tool_desc_transitions"] += bool(desc)
            tot["param_desc_transitions"] += bool(pc.get("description"))
            schema = bool(t["schema_changed"]) or bool(anno_other)
            cls = ("A" if growth else "B" if added else "C" if desc else "D" if schema
                   else "E" if removed else "?")
            # flag anything risky inside the newly added tools (informational, B is already blocked)
            new_tool_flags = []
            for name in added:
                bt = B[name]
                f = [p for p in props(bt) if destination_param(p) or execution_param(p)]
                an = camel(bt.get("annotations"))
                if f or an.get("destructiveHint") is True or an.get("openWorldHint") is True:
                    new_tool_flags.append((name, f, {k: v for k, v in an.items() if k != "title"}))
            if cls == "C" and all(desc_ws):
                tot["C_whitespace_only_transitions"] += 1
            if cls == "A" and all(not g[1].startswith("new ") for g in growth):
                tot["A_annotation_only_transitions"] += 1
            rows.append(dict(pkg=pkg, frm=t["from"], to=t["to"], cls=cls, growth=growth, added=added,
                             removed=removed, desc=desc, params=dict(pc), new_tool_flags=new_tool_flags))

    out = []
    w = out.append
    by = collections.Counter(r["cls"] for r in rows)
    w("# Risk classes of the 49 tool-surface changes (live probe, 30 packages) — 2026-10-20\n")
    w("Script: scripts/risk_classes_2026-10-20.py. Rule: mcpgawk's shipped drift.py (`destination_param`, "
      "`execution_param`, `DriftReport.escalations`). Each transition counted once, by its most severe class.\n")
    w("| class | meaning | guard | transitions |\n|---|---|---|---|")
    meaning = {"A": ("permission growth (new destination/execution param, or annotation escalation)", "BLOCK"),
               "B": ("new tool added", "BLOCK"), "C": ("tool description rewritten", "BLOCK"),
               "D": ("schema-only, no growth", "queue, calls continue"), "E": ("tools removed only", "queue"),
               "?": ("unclassified", "-")}
    for c in "ABCDE?":
        if by[c] or c != "?":
            w(f"| {c} | {meaning[c][0]} | {meaning[c][1]} | {by[c]} |")
    w(f"| | **changed / all transitions** | | **{len(rows)} / {n_trans}** |\n")
    w("## Reconciliation against the summary\n")
    w(f"- transitions {n_trans} (summary 107); changed {len(rows)} (summary 49)")
    w(f"- tools added / removed {tot['tools_added']} / {tot['tools_removed']} (summary 12 / 8)")
    w(f"- parameter changes added/removed/type/description/other: {tot['param_added']}/{tot['param_removed']}/"
      f"{tot['param_type']}/{tot['param_description']}/{tot['param_other']} (summary 77/16/5/94/14)")
    w(f"- tool-level description rewrites: {tot['tool_desc_rewrites']} (tool, transition) pairs in "
      f"{tot['tool_desc_transitions']} transitions; parameter-description rewrites: {tot['param_description']} in "
      f"{tot['param_desc_transitions']} transitions")
    w(f"- of the tool-description rewrites, {tot['tool_desc_whitespace_only']} are whitespace-only; "
      f"{tot['C_whitespace_only_transitions']} class-C transitions are whitespace-only throughout")
    w(f"- class A transitions driven by annotations alone (no new parameter): {tot['A_annotation_only_transitions']}\n")
    w("## Per package (A / B / C / D / E)\n")
    w("| package | A | B | C | D | E | A+B+C |\n|---|---|---|---|---|---|---|")
    pp = collections.defaultdict(collections.Counter)
    for r in rows:
        pp[r["pkg"]][r["cls"]] += 1
    for pkg, c in sorted(pp.items(), key=lambda kv: -(kv[1]["A"] + kv[1]["B"] + kv[1]["C"])):
        w(f"| {pkg} | {c['A']} | {c['B']} | {c['C']} | {c['D']} | {c['E']} | {c['A'] + c['B'] + c['C']} |")
    w("\n## Every changed transition\n")
    for r in rows:
        w(f"### {r['pkg']} {r['frm']} → {r['to']} — class {r['cls']}")
        for g in r["growth"]:
            w(f"- GROWTH `{g[0]}`: {g[1]} — {g[2]}")
        if r["added"]:
            w(f"- added tools: {', '.join(r['added'])}")
        for f in r["new_tool_flags"]:
            w(f"  - new tool `{f[0]}` flags: params {f[1]} annotations {f[2]}")
        if r["removed"]:
            w(f"- removed tools: {', '.join(r['removed'])}")
        for dsc in r["desc"]:
            w(f"- description `{dsc[0]}`:\n  - before: {dsc[1]}\n  - after: {dsc[2]}")
        if r["params"]:
            w(f"- parameter changes: {r['params']}")
        w("")
    print("\n".join(out))


if __name__ == "__main__":
    main()

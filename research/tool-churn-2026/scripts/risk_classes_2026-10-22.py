"""Risk classes of the 49 tool-surface changes in the 30-package keyless live probe (2026-10-04/07).

Revision of risk_classes_2026-10-20.py (which is left untouched: the published article cites it).
Two changes, both promised publicly:

  (a) "points somewhere" parameter detection walks NESTED schema, not only top-level
      inputSchema property names. It recurses into object `properties` (`a.b`), array `items`
      (`a[]`), `anyOf`/`oneOf`/`allOf` branches (same path), dict-valued `additionalProperties`
      (`a.*`) and local `$ref`s into `$defs`/`definitions` (cycle-guarded). A gained path whose
      LAST name matches the shipped `destination_param`/`execution_param` rule is reported by its
      dotted path. The 10-20 script missed circleci 0.15.1 -> 0.16.0 `params.outputDir`.
  (b) Each tool-description rewrite gets a deterministic sub-class from `description_rewrite_kind`:
      whitespace_only / addresses_agent / documents_tool. Added text = sentences present in the new
      description and absent from the old one (sentence-level set difference). The rule is
      `addresses_agent` with the pattern list AGENT_DIRECTIVE_PATTERNS; nothing is hand-labelled.

Applies mcpgawk's OWN shipped rule (src/mcpgawk/drift.py): `destination_param`, `execution_param`
and the `DriftReport.escalations` logic (lost readOnlyHint/idempotentHint, gained
destructiveHint/openWorldHint). Each changed transition is counted once, by its most severe class:

  A permission growth  new destination/execution parameter (at any depth) on an existing tool, or annotation escalation (BLOCKED)
  B new tool added     not in the approved set (BLOCKED)
  C tool description rewritten (BLOCKED by the description hash)
  D schema-only change, no growth (queued; calls continue)
  E tools removed only

Note: the probe stored annotations via pydantic model_dump() WITHOUT by_alias, so keys are snake_case
(read_only_hint). They are mapped back to the wire camelCase before the escalation rule is applied.

    .venv/bin/python research/tool-churn-2026/scripts/risk_classes_2026-10-22.py > research/tool-churn-2026/risk-classes-2026-10-22.md
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / "src"))
from mcpgawk.drift import DriftReport, destination_param, execution_param  # noqa: E402

DATA = ROOT / "data/live-probe-churn-2026-10-04.json"
CAMEL = {"read_only_hint": "readOnlyHint", "destructive_hint": "destructiveHint",
         "idempotent_hint": "idempotentHint", "open_world_hint": "openWorldHint"}

#: The 2026-10-20 published numbers (risk-classes.md), for the CHANGES section.
BASELINE_1020 = {"A": 6, "B": 7, "C": 12, "D": 23, "E": 1, "changed": 49, "transitions": 107,
                 "ABC": 25, "pointing_param_transitions": 4}
#: 10-20 class of the transitions this revision can move (from risk-classes.md).
BASELINE_1020_CLASS = {("@circleci/mcp-server-circleci", "0.15.1", "0.16.0"): "C",
                       ("mongodb-mcp-server", "1.8.1", "1.9.0"): "D"}

#: The 2026-10-22 hand check (made before the rule was written): rewrites that address the agent.
HAND_CHECK_AGENT = {("@circleci/mcp-server-circleci", "0.19.2", "0.20.0"),
                    ("@circleci/mcp-server-circleci", "0.15.1", "0.16.0"),
                    ("firecrawl-mcp", "3.23.4", "3.23.6"), ("firecrawl-mcp", "3.22.4", "3.23.0"),
                    ("@shopify/dev-mcp", "1.14.3", "1.14.4"), ("@shopify/dev-mcp", "1.14.2", "1.14.3")}

RULE_NOTE = """**Known misses of the description rule (hand-written review).** At transition level the rule has no false
positive or false negative against the hand check. At sentence level: `must` fires on documentation once
(firecrawl_map "several relevant pages must be located"; the same sentence also opens with "Use this when"), and
imperatives outside the pattern list do not fire: firecrawl 3.23.1 → 3.23.2 "Set skills to "only" to limit the
search…" (classed documents the tool, as the hand check also has it), firecrawl_agent_status "Check again after
15–30 seconds…", firecrawl_feedback "Provide the endpoint…", firecrawl_scrape "Set `maxAge: 0`…". Those last three sit
in transitions that already fire on other sentences. Two class-B transitions also address the agent:
playwright 0.0.71 → 0.0.72 ("Use browser_network_request with the number…") and shopify 1.14.7 → 1.15.0
("Do NOT call feedback after individual searches…")."""

#: Hand-written review of the rule's output (the rule itself is not tuned to any one string).
REVIEW_NOTE = """**Review of the rule's output (hand-written).** The nested walk applies the shipped name rule unchanged,
and it now fires on two transitions, not one. circleci 0.15.1 → 0.16.0 `params.outputDir` is the expected catch: the
call writes the full logs to that directory. mongodb-mcp-server 1.8.1 → 1.9.0 is a **false positive of the name
rule**: the four `…$vectorSearch.path` / `…fields[].path` hits are document field paths inside a MongoDB query
("Field, in dot notation, where to search"), not filesystem or network destinations. Read strictly by the shipped
rule the numbers are 6 pointing-parameter transitions and 26/49 blocked; setting the mongodb false positive aside
(it returns to class D) they are 5 and 25/49, with class counts A 7 / B 7 / C 11 / D 23 / E 1. The rule is
left as shipped here; a context exception for `path` would be a change to drift.py, not to this report."""


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


# --- (a) nested parameter paths ----------------------------------------------------------------

def _resolve(node, root: dict, seen: frozenset):
    """Follow a local `$ref` (#/$defs/X or #/definitions/X). Returns (schema, seen, via_ref)."""
    via = False
    while isinstance(node, dict) and isinstance(node.get("$ref"), str):
        ref = node["$ref"]
        if not ref.startswith("#/") or ref in seen:
            return None, seen, via
        seen = seen | {ref}
        target = root
        for part in ref[2:].split("/"):
            target = target.get(part) if isinstance(target, dict) else None
        node, via = target, True
    return node, seen, via


def schema_paths(schema: dict) -> dict[str, dict]:
    """Every parameter path in an inputSchema -> {"leaf": last property name, "schema", "via_ref"}.

    Paths: object property `a.b`, array items `a[]`, additionalProperties `a.*`; anyOf/oneOf/allOf
    branches share their parent's path (so reordering branches is not a change). Top-level
    properties keep their bare name, so the 10-20 top-level results are a subset of these.
    """
    out: dict[str, dict] = {}
    root = schema if isinstance(schema, dict) else {}

    def walk(node, prefix: str, seen: frozenset, via: bool) -> None:
        node, seen, v = _resolve(node, root, seen)
        via = via or v
        if not isinstance(node, dict):
            return
        for kw in ("anyOf", "oneOf", "allOf"):
            for br in node.get(kw) or []:
                walk(br, prefix, seen, via)
        p = node.get("properties")
        if isinstance(p, dict):
            for name, sub in p.items():
                path = f"{prefix}.{name}" if prefix else name
                rsub, _, rv = _resolve(sub, root, seen)
                out.setdefault(path, {"leaf": name, "schema": rsub if isinstance(rsub, dict) else {},
                                      "via_ref": via or rv})
                walk(sub, path, seen, via)
        items = node.get("items")
        for it in (items if isinstance(items, list) else [items] if isinstance(items, dict) else []):
            walk(it, f"{prefix}[]", seen, via)
        ap = node.get("additionalProperties")
        if isinstance(ap, dict):
            walk(ap, f"{prefix}.*", seen, via)

    walk(root, "", frozenset(), False)
    return out


def gained_pointing_params(a: dict, b: dict) -> list[dict]:
    """Paths new in tool `b` (vs `a`) whose last name matches destination_param/execution_param.

    Each hit: {"path", "kinds", "description", "via_ref", "moved_from"}; `moved_from` lists old
    paths with the same leaf name (a restructure, not necessarily a new capability).
    """
    pa, pb = schema_paths(a.get("inputSchema") or {}), schema_paths(b.get("inputSchema") or {})
    hits = []
    for path in sorted(set(pb) - set(pa)):
        leaf = pb[path]["leaf"]
        kinds = [k for k, f in (("destination", destination_param), ("execution", execution_param)) if f(leaf)]
        if kinds:
            hits.append({"path": path, "kinds": kinds, "description": short(pb[path]["schema"].get("description")),
                         "via_ref": pb[path]["via_ref"],
                         "moved_from": sorted(p for p, v in pa.items() if v["leaf"] == leaf)})
    return hits


# --- (b) description rewrites: addresses the agent vs documents the tool ------------------------

#: Clause start: start of sentence, after ; : ( — – or after so/then/otherwise/instead.
_CLAUSE = r"(?:^|[;:(—–]\s*|\b(?:so|then|otherwise|instead)\s+)"

#: (name, regex) pairs, matched case-insensitively against each ADDED sentence after markdown
#: emphasis (** __ `) is stripped and curly apostrophes are straightened. A sentence that matches
#: any one of them is a directive to the agent rather than a description of the tool.
AGENT_DIRECTIVE_PATTERNS: list[tuple[str, str]] = [
    ("always/never", r"\b(?:always|never)\b"),
    ("must", r"\bmust\b"),
    ("you should/need to", r"\byou (?:should|need to)\b"),
    ("do not / don't", r"\b(?:do not|don't|dont|does not need to)\b(?= \w)"),
    ("before/after/instead of calling", r"\b(?:before|after|instead of) (?:calling|using|invoking|making)\b"),
    ("tell/ask the user", r"\b(?:tell|ask|inform|remind|warn|notify) the user\b"),
    ("ignore", r"\bignore\b"),
    ("prefer", r"\bprefer\b"),
    ("choose this", r"\bchoose (?:this|it)\b"),
    ("skip", _CLAUSE + r"skip\b"),
    ("use (imperative)", _CLAUSE + r"use\b"),
    ("please", r"\bplease\b"),
]
_COMPILED = [(n, re.compile(p, re.IGNORECASE)) for n, p in AGENT_DIRECTIVE_PATTERNS]
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_BULLET = re.compile(r"^(?:[-*•]|\d+[.)])\s+")


def sentences(text: str | None) -> list[str]:
    """Split on newlines first, then on . ! ? + whitespace; collapse whitespace; drop bullets."""
    out = []
    for line in (text or "").splitlines():
        for s in _SENT_SPLIT.split(line):
            s = _BULLET.sub("", " ".join(s.split()))
            if s:
                out.append(s)
    return out


def added_sentences(old: str | None, new: str | None) -> list[str]:
    """Sentences of `new` that do not occur in `old`, in `new`'s order (sentence-level diff)."""
    have = set(sentences(old))
    seen, out = set(), []
    for s in sentences(new):
        if s not in have and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def addresses_agent(sentence: str) -> list[str]:
    """Names of the AGENT_DIRECTIVE_PATTERNS that match one sentence (empty = documentation).

    The pattern list is the whole rule: absolutes (always/never/must), prohibitions (do not),
    call-ordering (before/after calling), relaying to the user (tell/ask the user), selection
    directives (prefer, choose this, skip, clause-initial use), and please. `use` and `skip`
    only count at the start of a clause, so "Useful for…" and "…or use web search" do not fire.
    """
    s = sentence.replace("**", "").replace("__", "").replace("`", "").replace("’", "'")
    return [n for n, rx in _COMPILED if rx.search(s)]


def description_rewrite_kind(old: str | None, new: str | None) -> tuple[str, list[tuple[str, list[str]]]]:
    """Sub-class one tool-description rewrite.

    whitespace_only  the texts are equal after collapsing whitespace (unchanged from 10-20)
    addresses_agent  some ADDED sentence matches AGENT_DIRECTIVE_PATTERNS; hits = [(sentence, names)]
    documents_tool   any other word change (including pure deletions)
    """
    if " ".join((old or "").split()) == " ".join((new or "").split()):
        return "whitespace_only", []
    hits = [(s, m) for s in added_sentences(old, new) if (m := addresses_agent(s))]
    return ("addresses_agent" if hits else "documents_tool"), hits


# --- analysis -----------------------------------------------------------------------------------

def analyse(d: dict):
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
            growth, desc, anno_other, desc_ws, desc_kinds = [], [], [], [], []
            n_param_growth = n_nested = n_ref = 0
            for name in sorted(set(A) & set(B)):
                a, b = A[name], B[name]
                for g in gained_pointing_params(a, b):
                    nested = "." in g["path"] or "[" in g["path"]
                    n_param_growth += 1; n_nested += nested; n_ref += g["via_ref"]
                    note = (" (via $ref)" if g["via_ref"] else "") + \
                           (f" (same name existed at {', '.join(g['moved_from'])})" if g["moved_from"] else "")
                    growth.append((name, f"new {'+'.join(g['kinds'])} parameter `{g['path']}`{note}", g["description"]))
                for e in escalations(a.get("annotations"), b.get("annotations")):
                    growth.append((name, e, f"{a.get('annotations')} -> {b.get('annotations')}"))
                if a.get("description") != b.get("description"):
                    ws = " ".join((a.get("description") or "").split()) == " ".join((b.get("description") or "").split())
                    tot["tool_desc_whitespace_only"] += ws
                    desc_ws.append(ws)
                    kind, hits = description_rewrite_kind(a.get("description"), b.get("description"))
                    desc_kinds.append((name, kind, hits))
                    desc.append((name, short(a.get("description")), short(b.get("description"))))
                if a.get("annotations") != b.get("annotations"):
                    anno_other.append(name)
            pc = collections.Counter(p["change"] for p in t["parameters"])
            tot.update({f"param_{k}": v for k, v in pc.items()})
            tot["tools_added"] += len(added); tot["tools_removed"] += len(removed)
            tot["tool_desc_rewrites"] += len(desc); tot["tool_desc_transitions"] += bool(desc)
            tot["param_desc_transitions"] += bool(pc.get("description"))
            tot["pointing_param_transitions"] += bool(n_param_growth)
            tot["pointing_params"] += n_param_growth
            tot["pointing_params_nested"] += n_nested
            tot["pointing_params_via_ref"] += n_ref
            schema = bool(t["schema_changed"]) or bool(anno_other)
            cls = ("A" if growth else "B" if added else "C" if desc else "D" if schema
                   else "E" if removed else "?")
            kinds = {k for _, k, _ in desc_kinds}
            desc_kind = ("addresses_agent" if "addresses_agent" in kinds else
                         "whitespace_only" if kinds == {"whitespace_only"} else
                         "documents_tool" if kinds else None)
            new_tool_flags = []
            for name in added:
                bt = B[name]
                f = [p for p, v in schema_paths(bt.get("inputSchema") or {}).items()
                     if destination_param(v["leaf"]) or execution_param(v["leaf"])]
                an = camel(bt.get("annotations"))
                if f or an.get("destructiveHint") is True or an.get("openWorldHint") is True:
                    new_tool_flags.append((name, f, {k: v for k, v in an.items() if k != "title"}))
            if cls == "C" and all(desc_ws):
                tot["C_whitespace_only_transitions"] += 1
            if cls == "A" and all(not g[1].startswith("new ") for g in growth):
                tot["A_annotation_only_transitions"] += 1
            rows.append(dict(pkg=pkg, frm=t["from"], to=t["to"], cls=cls, growth=growth, added=added,
                             removed=removed, desc=desc, desc_kinds=desc_kinds, desc_kind=desc_kind,
                             params=dict(pc), new_tool_flags=new_tool_flags))
    tot["transitions"] = n_trans
    return rows, tot


def render(rows, tot) -> str:
    out = []
    w = out.append
    n_trans = tot["transitions"]
    by = collections.Counter(r["cls"] for r in rows)
    abc = by["A"] + by["B"] + by["C"]
    pp = collections.defaultdict(collections.Counter)
    for r in rows:
        pp[r["pkg"]][r["cls"]] += 1
    ranked = sorted(pp.items(), key=lambda kv: -(kv[1]["A"] + kv[1]["B"] + kv[1]["C"]))
    rewrites = [r for r in rows if r["desc_kind"]]
    agent = [r for r in rewrites if r["desc_kind"] == "addresses_agent"]
    c_rows = [r for r in rows if r["cls"] == "C"]
    b0 = BASELINE_1020

    w("# Risk classes of the 49 tool-surface changes (live probe, 30 packages) — 2026-10-22\n")
    w("Script: scripts/risk_classes_2026-10-22.py (regenerates this whole file). Rule: mcpgawk's shipped drift.py "
      "(`destination_param`, `execution_param`, `DriftReport.escalations`), now applied to parameter paths at any "
      "depth. Each transition counted once, by its most severe class. Supersedes risk-classes.md (2026-10-20), "
      "which is kept unchanged because it is cited.\n")
    w("## CHANGES vs 2026-10-20\n")
    w("1. Pointing-parameter detection walks nested schema (object properties `a.b`, array items `a[]`, "
      "anyOf/oneOf/allOf, additionalProperties `a.*`, local `$ref`) and reports the dotted path. 10-20 checked "
      "top-level `inputSchema.properties` names only.")
    w("2. Every tool-description rewrite is sub-classed by a runnable rule (`description_rewrite_kind`, patterns "
      "below): whitespace-only / addresses the agent / documents the tool. Whitespace-only normalisation is unchanged.\n")
    w("| number | 2026-10-20 | 2026-10-22 |\n|---|---|---|")
    for c in "ABCDE":
        w(f"| class {c} transitions | {b0[c]} | {by[c]} |")
    w(f"| A+B+C (blocked) / changed | {b0['ABC']}/{b0['changed']} | {abc}/{len(rows)} |")
    w(f"| transitions with a new pointing parameter | {b0['pointing_param_transitions']} | "
      f"{tot['pointing_param_transitions']} |")
    groups = collections.defaultdict(list)
    for p, c in ranked:
        groups[c["A"] + c["B"] + c["C"]].append(p)
    top = "; ".join(f"{n}: {', '.join(ps)}" for n, ps in sorted(groups.items(), reverse=True)[:3])
    w(f"| top 3 A+B+C values (packages) | 6: chrome-devtools-mcp; 5: firecrawl-mcp; 3: @playwright/mcp, "
      f"@shopify/dev-mcp, @circleci/mcp-server-circleci | {top} |")
    w("")
    moved = [r for r in rows if r["cls"] == "A" and any("parameter `" in g[1] and ("." in g[1] or "[]" in g[1])
                                                         for g in r["growth"])]
    for r in moved:
        w(f"- {r['pkg']} {r['frm']} → {r['to']} is class {r['cls']} now: "
          + "; ".join(f"`{g[0]}` {g[1]}" for g in r["growth"] if g[1].startswith("new ")))
    w(f"- Pointing parameters found: {tot['pointing_params']} in {tot['pointing_param_transitions']} transitions; "
      f"{tot['pointing_params_nested']} of them nested, {tot['pointing_params_via_ref']} reached through a `$ref`.")
    for r in moved:
        before = BASELINE_1020_CLASS.get((r["pkg"], r["frm"], r["to"]))
        if before and before != r["cls"]:
            blocked = "both blocked, so A+B+C does not move" if before in "ABC" else \
                f"{before} was queued, so A+B+C rises by one for {r['pkg']}"
            w(f"- {r['pkg']} {r['frm']} → {r['to']}: class {before} → {r['cls']} ({blocked}).")
    w("\n" + REVIEW_NOTE + "\n")

    w("| class | meaning | guard | transitions |\n|---|---|---|---|")
    meaning = {"A": ("permission growth (new destination/execution param at any depth, or annotation escalation)", "BLOCK"),
               "B": ("new tool added", "BLOCK"), "C": ("tool description rewritten", "BLOCK"),
               "D": ("schema-only, no growth", "queue, calls continue"), "E": ("tools removed only", "queue"),
               "?": ("unclassified", "-")}
    for c in "ABCDE?":
        if by[c] or c != "?":
            w(f"| {c} | {meaning[c][0]} | {meaning[c][1]} | {by[c]} |")
    w(f"| | **changed / all transitions** | | **{len(rows)} / {n_trans}** |\n")

    w("## Description rewrites: addresses the agent vs documents the tool\n")
    w("Added text = sentences in the new description that are not in the old one (split on newlines, then on "
      "`.`/`!`/`?`; whitespace collapsed; leading bullets dropped). A rewrite **addresses the agent** when an added "
      "sentence matches one of these patterns (case-insensitive, markdown emphasis and backticks stripped first):\n")
    w("| pattern | regex |\n|---|---|")
    for n, p in AGENT_DIRECTIVE_PATTERNS:
        w(f"| {n} | `{p.replace('|', '¦')}` |")
    w("\n(`¦` stands for regex alternation `|` inside the table.)\n")
    k_all = collections.Counter(r["desc_kind"] for r in rewrites)
    k_c = collections.Counter(r["desc_kind"] for r in c_rows)
    w(f"- transitions with a tool-description rewrite: {len(rewrites)} — addresses the agent "
      f"{k_all['addresses_agent']}, documents the tool {k_all['documents_tool']}, whitespace-only {k_all['whitespace_only']}")
    w(f"- of the {len(c_rows)} class-C transitions: addresses the agent {k_c['addresses_agent']}, documents the tool "
      f"{k_c['documents_tool']}, whitespace-only {k_c['whitespace_only']}")
    pairs = collections.Counter(k for r in rewrites for _, k, _ in r["desc_kinds"])
    w(f"- per (tool, transition) pair: addresses the agent {pairs['addresses_agent']}, documents the tool "
      f"{pairs['documents_tool']}, whitespace-only {pairs['whitespace_only']} (of {sum(pairs.values())})\n")
    w("| package | transition | class | rewrite | first matched added sentence (pattern) |\n|---|---|---|---|---|")
    for r in rewrites:
        first = next(((n, h) for n, k, hs in r["desc_kinds"] for h in hs[:1]), None)
        cell = f"`{first[0]}`: {short(first[1][0], 140)} ({', '.join(first[1][1])})" if first else ""
        w(f"| {r['pkg']} | {r['frm']} → {r['to']} | {r['cls']} | {r['desc_kind']} | {cell.replace('|', '¦')} |")
    w("")
    old_c = [r for r in rows if r["cls"] == "C" or BASELINE_1020_CLASS.get((r["pkg"], r["frm"], r["to"])) == "C"]
    agree = [r for r in old_c if (r["desc_kind"] == "addresses_agent") == ((r["pkg"], r["frm"], r["to"]) in HAND_CHECK_AGENT)]
    w(f"**Against the hand check** (the 12 transitions that were class C on 2026-10-20; the hand check names "
      f"{len(HAND_CHECK_AGENT)} as addressing the agent, counting shopify 1.14.2 → 1.14.3 in its parenthesis): the rule "
      f"agrees on {len(agree)} of {len(old_c)}.")
    for r in old_c:
        if r not in agree:
            w(f"- DISAGREES: {r['pkg']} {r['frm']} → {r['to']}: rule {r['desc_kind']}, hand "
              f"{'addresses_agent' if (r['pkg'], r['frm'], r['to']) in HAND_CHECK_AGENT else 'documents_tool'}")
    w("\n" + RULE_NOTE + "\n")

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
    for pkg, c in ranked:
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
        kinds = {n: (k, hs) for n, k, hs in r["desc_kinds"]}
        for dsc in r["desc"]:
            k, hs = kinds[dsc[0]]
            w(f"- description `{dsc[0]}` ({k}):\n  - before: {dsc[1]}\n  - after: {dsc[2]}")
            for s, m in hs:
                w(f"  - directive: {short(s, 200)} ({', '.join(m)})")
        if r["params"]:
            w(f"- parameter changes: {r['params']}")
        w("")
    return "\n".join(out)


def main() -> None:
    print(render(*analyse(json.loads(DATA.read_text()))))


if __name__ == "__main__":
    main()

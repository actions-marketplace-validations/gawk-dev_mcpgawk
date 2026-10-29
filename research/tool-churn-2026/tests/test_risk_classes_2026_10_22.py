"""Tests for scripts/risk_classes_2026-10-22.py: nested pointing-parameter paths and the
agent-addressed sub-classification of description rewrites.

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -c /dev/null -p no:cacheprovider \
        --rootdir=research/tool-churn-2026 research/tool-churn-2026/tests
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("risk_classes_2026_10_22", ROOT / "scripts/risk_classes_2026-10-22.py")
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)


@pytest.fixture(scope="module")
def data():
    return json.loads((ROOT / "data/live-probe-churn-2026-10-04.json").read_text())


@pytest.fixture(scope="module")
def analysed(data):
    return rc.analyse(data)


def _row(rows, pkg, frm, to):
    (r,) = [r for r in rows if (r["pkg"], r["frm"], r["to"]) == (pkg, frm, to)]
    return r


def _tool(props):
    return {"name": "t", "inputSchema": {"type": "object", "properties": props}}


# --- (a) nested pointing-parameter detection -------------------------------------------------

def test_nested_object_property_reports_dotted_path():
    a = _tool({"params": {"type": "object", "properties": {"branch": {"type": "string"}}}})
    b = _tool({"params": {"type": "object", "properties": {"branch": {"type": "string"},
                                                          "outputDir": {"type": "string"}}}})
    paths = [g["path"] for g in rc.gained_pointing_params(a, b)]
    assert paths == ["params.outputDir"]


def test_array_items_property_reports_bracket_path():
    item = lambda extra: {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, **extra}}}
    a = _tool({"files": item({})})
    b = _tool({"files": item({"uploadUrl": {"type": "string"}})})
    paths = [g["path"] for g in rc.gained_pointing_params(a, b)]
    assert paths == ["files[].uploadUrl"]


def test_anyof_branch_property_is_found():
    a = _tool({"target": {"anyOf": [{"type": "object", "properties": {"id": {"type": "string"}}}]}})
    b = _tool({"target": {"anyOf": [{"type": "object", "properties": {"id": {"type": "string"}}},
                                    {"type": "object", "properties": {"webhook": {"type": "string"}}}]}})
    paths = [g["path"] for g in rc.gained_pointing_params(a, b)]
    assert paths == ["target.webhook"]


def test_top_level_still_detected_and_non_pointing_ignored():
    a = _tool({"q": {"type": "string"}})
    b = _tool({"q": {"type": "string"}, "url": {"type": "string"}, "limit": {"type": "integer"}})
    assert [g["path"] for g in rc.gained_pointing_params(a, b)] == ["url"]


def test_schema_paths_handles_ref_cycles():
    s = {"type": "object", "$defs": {"node": {"type": "object", "properties": {
        "child": {"$ref": "#/$defs/node"}, "path": {"type": "string"}}}},
        "properties": {"root": {"$ref": "#/$defs/node"}}}
    paths = rc.schema_paths(s)
    assert "root.path" in paths and "root.child" in paths  # terminates: a $ref already followed is not re-entered


def test_circleci_outputdir_from_real_data_is_class_a(analysed):
    rows, tot = analysed
    r = _row(rows, "@circleci/mcp-server-circleci", "0.15.1", "0.16.0")
    assert r["cls"] == "A"
    assert any(g[0] == "get_build_failure_logs" and "params.outputDir" in g[1] for g in r["growth"])


def test_pointing_parameter_transition_count(analysed):
    rows, tot = analysed
    # 10-20 (top-level names only): 4. The nested walk adds circleci 0.15.1 -> 0.16.0 (expected) and
    # mongodb 1.8.1 -> 1.9.0, whose `...$vectorSearch.path` is a MongoDB field path: a false positive of the
    # shipped name rule, measured here rather than tuned away.
    assert tot["pointing_param_transitions"] == 6
    r = _row(rows, "mongodb-mcp-server", "1.8.1", "1.9.0")
    assert r["cls"] == "A" and all(g[1].endswith("path`") for g in r["growth"])


# --- (b) description rewrites: addresses the agent vs documents the tool ---------------------

def test_added_sentences_is_sentence_level_and_ignores_rewrap():
    old = "Reads a file. Returns text."
    new = "Reads a file.\nReturns   text. Always call list first."
    assert rc.added_sentences(old, new) == ["Always call list first."]


@pytest.mark.parametrize("old,new", [
    ("Gets config.", "Gets config. Please tell the user to migrate to CircleCI's hosted MCP server."),
    ("Logs.", "Logs. When truncated, output will contain <MCPTruncationWarning> and you MUST acknowledge:"),
    ("Extract.", "Extract. Use firecrawl_search or firecrawl_agent before Scrape when URLs are not known."),
    ("Parse.", "Parse. Upload locally, then call again with the returned `uploadRef`; do not send both fields together."),
    ("Learn.", "Learn. Choose this (not `admin`) whenever the ask is for numbers."),
    ("Learn.", "Learn. Skip for API-only understanding or codegen with no CLI execution."),
    ("Learn.", "Learn. Do **not** choose `admin` first for app monetization."),
])
def test_agent_addressed_positives(old, new):
    label, hits = rc.description_rewrite_kind(old, new)
    assert label == "addresses_agent", hits
    assert hits


@pytest.mark.parametrize("old,new", [
    ("List requests.", "List requests. Lists the most recent requests for the target page since the last navigation."),
    ("Get a request.", "Get a request. Useful for inspecting request headers (including 'Cookie')."),
    ("Extract.", "Extract. It can include subdomains, follow external links, or use web search when enabled."),
    ("Read a file.", "Read a file and return it as a base64-encoded content block with its MIME type."),
])
def test_documentation_negatives(old, new):
    label, hits = rc.description_rewrite_kind(old, new)
    assert label == "documents_tool", hits


def test_whitespace_only_rewrite():
    label, hits = rc.description_rewrite_kind("Evaluate a  script.\n Returns JSON.", "Evaluate a script. Returns JSON.")
    assert label == "whitespace_only" and hits == []


def test_word_change_is_not_whitespace_only():
    label, _ = rc.description_rewrite_kind("Evaluate a script.", "Evaluate the script.")
    assert label == "documents_tool"


def test_real_data_hand_check_transitions_fire(analysed):
    rows, _ = analysed
    for key in [("@circleci/mcp-server-circleci", "0.19.2", "0.20.0"),
                ("@circleci/mcp-server-circleci", "0.15.1", "0.16.0"),
                ("firecrawl-mcp", "3.23.4", "3.23.6"),
                ("firecrawl-mcp", "3.22.4", "3.23.0"),
                ("@shopify/dev-mcp", "1.14.3", "1.14.4"),
                ("@shopify/dev-mcp", "1.14.2", "1.14.3")]:
        assert _row(rows, *key)["desc_kind"] == "addresses_agent", key


def test_patterns_are_documented():
    assert rc.AGENT_DIRECTIVE_PATTERNS and all(len(p) == 2 for p in rc.AGENT_DIRECTIVE_PATTERNS)
    assert rc.addresses_agent.__doc__ and "pattern" in rc.addresses_agent.__doc__.lower()

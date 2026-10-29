"""Non-negotiables for credential injection in `wrap` (slice doc: docs/design-credential-injection-2026-10-23.md).

Written BEFORE the code, as the ContextKey rule requires. Context: Christian Posta's thread (21 Oct
2026) — inject credentials on egress, never hand them to the agent — and the LiteLLM 1.107.0
compromise the same day, where the gateway's own credentials table was the prize. We take the
custody half (the config holds a reference, the server gets the value) and refuse the gateway half
(no store of our own). The thread's objection — "injection protects the key, not the call" — is the
half mcpgawk already covers at call time.

The constraints:

1. RESOLVE, NEVER STORE. The resolver reads one named Keychain item and writes nothing: no
   `add-generic-password`, no `delete-generic-password`, no `-U`, no file under ~/.mcpgawk.
2. ONE PLACE. Only the launch line (`wrap`, `verify`) resolves. scan, panel, daemon, fleet never
   see a secret value.
3. THE VALUE TOUCHES NOTHING BUT THE CHILD ENV. Not the parent's os.environ, not the config file,
   not the spool/runlog/evidence, not stderr. It is registered with the redactor so a log line
   that somehow carries it is masked.
4. FAIL CLOSED. An unresolvable reference means the server is NOT launched, exit 2, and the
   message names the reference, never a value.
5. IDENTITY AS DECLARED. The `keychain:` reference, not the resolved token, is what fingerprint/
   credentials treat as the login — the lesson of credentials.IDENTITY_AS_DECLARED.
6. TESTABLE WITHOUT THE KEYCHAIN. The resolver is injectable; the suite's `security` shim is the
   only `security` any test reaches (FOUNDER 2026-09-25).

Tests are `xfail(strict=True)` until `mcpgawk.inject` exists: visibly red by design, never a
vacuous pass (memory: a step that cannot run is not passing). Building the slice flips them.
"""
from __future__ import annotations

import ast
import importlib
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "mcpgawk"
INJECT = SRC / "inject.py"

_built = INJECT.exists()
needs_slice = pytest.mark.xfail(not _built, strict=True, reason="slice not built: src/mcpgawk/inject.py")


def _src(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def _calls_security_with(src: str, verb: str) -> bool:
    return verb in src


# --- 1. resolve, never store -------------------------------------------------------------------

@needs_slice
def test_the_resolver_only_ever_reads_the_keychain():
    src = _src(INJECT)
    assert _calls_security_with(src, "find-generic-password")
    for forbidden in ("add-generic-password", "delete-generic-password", "set-generic-password",
                      "\"-U\"", "'-U'", "security-dump", "dump-keychain"):
        assert forbidden not in src, forbidden


@needs_slice
def test_the_resolver_never_opens_a_file_for_writing():
    assert INJECT.exists()                      # an absent module must not pass vacuously
    tree = ast.parse(_src(INJECT))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = ast.unparse(node.func)
            if fn in ("open", "os.open", "Path.write_text", "Path.write_bytes") or fn.endswith((".write_text", ".write_bytes", ".mkdir", ".makedirs")):
                pytest.fail(f"inject.py writes to disk via {fn}")
            if fn.endswith("open") and len(node.args) > 1:
                mode = ast.unparse(node.args[1])
                assert "w" not in mode and "a" not in mode, mode


# --- 2. one place ------------------------------------------------------------------------------

@needs_slice
def test_only_the_launch_line_imports_the_resolver():
    assert INJECT.exists()                      # an absent module must not pass vacuously
    importers = {p.name for p in SRC.glob("*.py") if re.search(r"\bfrom \.inject\b|\bimport inject\b|mcpgawk\.inject", _src(p))}
    assert importers <= {"wrap.py", "verify.py", "cli.py"}, importers
    for never in ("panel.py", "daemon.py", "fleet.py", "discover.py", "probe.py", "spool.py", "runlog.py"):
        assert never not in importers, never


# --- 3. the value touches nothing but the child env -------------------------------------------

@needs_slice
def test_resolution_leaves_the_parent_environment_untouched(monkeypatch):
    inject = importlib.import_module("mcpgawk.inject")
    monkeypatch.setenv("GAWK_TEST_SENTINEL", "1")
    before = dict(os.environ)
    env = inject.child_env({"TOKEN": "keychain:mcpgawk-test-item"}, resolve=lambda ref: "s3cr3t-value")
    assert env["TOKEN"] == "s3cr3t-value"
    assert dict(os.environ) == before


@needs_slice
def test_a_resolved_value_is_registered_with_the_redactor():
    inject = importlib.import_module("mcpgawk.inject")
    from mcpgawk import redact
    inject.child_env({"TOKEN": "keychain:mcpgawk-test-item"}, resolve=lambda ref: "zq8-resolved-9k2")
    assert "zq8-resolved-9k2" not in redact.redact("header zq8-resolved-9k2 tail")


@needs_slice
def test_a_literal_or_unprefixed_value_passes_through_unchanged():
    inject = importlib.import_module("mcpgawk.inject")
    env = inject.child_env({"A": "plain", "B": "$HOME", "C": "op://vault/item"}, resolve=lambda ref: pytest.fail("resolver must not run"))
    assert env["A"] == "plain" and env["B"] == "$HOME" and env["C"] == "op://vault/item"


# --- 4. fail closed ----------------------------------------------------------------------------

@needs_slice
def test_an_unresolvable_reference_refuses_to_launch_and_names_the_reference_only():
    inject = importlib.import_module("mcpgawk.inject")
    with pytest.raises(inject.Unresolved) as err:
        inject.child_env({"TOKEN": "keychain:missing-item"}, resolve=lambda ref: None)
    msg = str(err.value)
    assert "keychain:missing-item" in msg
    assert err.value.exit_code == 2


@needs_slice
def test_wrap_does_not_start_the_server_when_a_reference_fails(monkeypatch, capsys):
    from mcpgawk import wrap
    inject = importlib.import_module("mcpgawk.inject")
    monkeypatch.setattr(inject, "default_resolver", lambda ref: None)
    monkeypatch.setenv("TOKEN", "keychain:missing-item")
    started = []
    import subprocess
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: started.append(a) or pytest.fail("server launched"))
    rc = wrap.run(["true"], name="t")
    assert rc == 2 and not started
    assert "keychain:missing-item" in capsys.readouterr().err


# --- 5. identity as declared -------------------------------------------------------------------

def test_the_declared_reference_is_the_login_identity_not_the_resolved_value():
    """Holds today: identity is computed from the config AS DECLARED. Pinned here so the slice
    cannot move it: two scans with a rotated token must agree on the server."""
    from mcpgawk import credentials
    declared = {"command": "x", "env": {"TOKEN": "keychain:gh-work"}}
    a = credentials.material(declared)
    rotated = dict(declared, **{credentials.IDENTITY_AS_DECLARED: credentials.material(declared)})
    rotated["env"] = {"TOKEN": "a-brand-new-access-token"}
    assert credentials.material(rotated) == a


def test_configcheck_treats_a_keychain_reference_as_the_right_pattern_today():
    from mcpgawk import configcheck
    assert "keychain:" in configcheck._INDIRECTION_PREFIXES
    findings = configcheck._plaintext_credentials("gh", {"env": {"GITHUB_TOKEN": "keychain:gh-work"}})
    assert findings == []


# --- 6. testable without the keychain ----------------------------------------------------------

@needs_slice
def test_the_default_resolver_calls_only_the_shim_and_is_refused_here(_never_the_real_keychain):
    inject = importlib.import_module("mcpgawk.inject")
    log = _never_the_real_keychain
    before = log.read_text()
    assert inject.default_resolver("keychain:mcpgawk-test-item") is None     # the shim refuses
    assert "find-generic-password" in log.read_text()[len(before):]
    log.write_text(before)


def test_no_module_but_oauth_login_writes_to_the_keychain():
    """Holds today, pinned for the slice: the only Keychain WRITER in the package stays the OAuth
    store key, created once. inject.py must never join it."""
    writers = {p.name for p in SRC.glob("*.py") if "add-generic-password" in _src(p)}
    assert writers <= {"oauth_login.py"}, writers

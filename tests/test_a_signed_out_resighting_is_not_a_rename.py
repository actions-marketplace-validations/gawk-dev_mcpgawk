"""An incomplete sign-in must not be reported as a server that RENAMED itself.

MEASURED on the founder's own machine (2026-09-15, released 0.1.45). `kite` was approved while
signed in, so it advertised `serverInfo.name = "Kite MCP Server"` and keyed `mcp:Kite MCP Server`.
A later scan reached kite NOT signed in: a not-authenticated remote advertises no name, so it keyed
by config name, `stdio:kite`. `identity_change` saw a "different server" and the scan printed
`⛔ kite now identifies itself as a DIFFERENT server … treat as unreviewed` — a rug-pull-shaped
alarm over a server whose tool surface was byte-for-byte the approved one (identical pin). The
scariest false alarm there is: it teaches a user to distrust a correct baseline.

The discriminator is the pin, the rug-pull anchor. A re-identification whose surface EQUALS the
approved baseline is not evasion — there is nothing changed to hide behind the new name — so the
baseline carries over and no alarm fires. A re-identification whose surface DIFFERS (a real
rename-evasion) still fires: that guard must survive this fix, and the last test here is its
mutation check.
"""
from __future__ import annotations

from mcpgawk import cli, history
from mcpgawk.measure import Measurement
from mcpgawk.probe import ServerSnapshot

NOW = "2026-09-15T00:00:00+00:00"


def _snap(asserted_name: str | None):
    """kite as one config entry ("kite"), signed in (advertises a name) or not (advertises none)."""
    return ServerSnapshot(name="kite", transport="stdio", protocol_version="1",
                          tools=[{"name": "get_holdings"}], enumerated=["tool"],
                          server_info=({"name": asserted_name} if asserted_name else {}),
                          login_id=("01bf6485c5ed" if asserted_name else None))


def _meas(pin: str):
    return Measurement(tokenizer="cl100k_base", total_tokens=100, tool_count=1, tools=[],
                       integrity_pin=pin)


def _store(monkeypatch, tmp_path):
    monkeypatch.setenv("MCPGAWK_HISTORY", str(tmp_path / "history.json"))


def test_the_signed_in_baseline_keys_by_asserted_name(monkeypatch, tmp_path):
    """Guards the guard: if the two snapshots keyed the SAME way, everything below would pass for
    the wrong reason."""
    _store(monkeypatch, tmp_path)
    signed_in = cli._record_sighting(_snap("Kite MCP Server"), _meas("PIN-A"), now=NOW)
    assert signed_in.key == "mcp:Kite MCP Server"
    signed_out_key = history.key_for(_snap(None))
    assert signed_out_key == "stdio:kite" and signed_out_key != signed_in.key


def test_a_signed_out_resighting_with_the_same_surface_is_not_a_rename(monkeypatch, tmp_path):
    """THE REGRESSION. Same tools (same pin), no sign-in, a new key — and NO rename alarm, with the
    approved baseline carried onto the new key."""
    _store(monkeypatch, tmp_path)
    cli._record_sighting(_snap("Kite MCP Server"), _meas("PIN-A"), now=NOW)   # approved baseline
    out = cli._record_sighting(_snap(None), _meas("PIN-A"), now=NOW)          # signed out, same tools
    assert out.key == "stdio:kite"
    assert out.reidentified_from is None, "an auth-state change was reported as a rename"
    assert out.previous is not None and out.previous.get("pin") == "PIN-A", (
        "the approved baseline did not carry over to the re-keyed entry")


def test_same_surface_is_the_discriminator(monkeypatch, tmp_path):
    _store(monkeypatch, tmp_path)
    cli._record_sighting(_snap("Kite MCP Server"), _meas("PIN-A"), now=NOW)
    store = history.load()
    assert history.same_surface(store, "mcp:Kite MCP Server", {"pin": "PIN-A"}) is True
    assert history.same_surface(store, "mcp:Kite MCP Server", {"pin": "PIN-B"}) is False
    assert history.same_surface(store, "mcp:Kite MCP Server", {"pin": ""}) is False
    assert history.same_surface(store, "mcp:never-seen", {"pin": "PIN-A"}) is False


def test_a_real_rename_with_a_CHANGED_surface_still_fires(monkeypatch, tmp_path):
    """THE MUTATION CHECK for the security guard. Different tools (different pin) under a new key is
    the rename-evasion this whole mechanism exists to catch — it must NOT be suppressed."""
    _store(monkeypatch, tmp_path)
    cli._record_sighting(_snap("Kite MCP Server"), _meas("PIN-A"), now=NOW)   # approved baseline
    out = cli._record_sighting(_snap(None), _meas("PIN-CHANGED"), now=NOW)    # new key AND new surface
    assert out.reidentified_from == "mcp:Kite MCP Server", (
        "a rename with a changed tool surface was silently suppressed — rug-pull evasion is back")

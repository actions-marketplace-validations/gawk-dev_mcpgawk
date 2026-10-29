"""Resolve `keychain:` references in a server's environment at launch — and hold nothing.

A config entry can say `GITHUB_TOKEN=keychain:gh-work` instead of pasting the token. `configcheck`
has called that the right pattern since July; until this module nothing made it work, so the
server was handed the literal string. Now `wrap` resolves it on the way in: the config holds a
reference, the agent sees a reference, the server process gets the value, mcpgawk keeps nothing.

Design constraints, pinned by tests/test_credential_injection_constraints.py and argued in
docs/design-credential-injection-2026-10-23.md:

* RESOLVE, NEVER STORE. One read-only `security find-generic-password` per reference. No add, no
  delete, no `-U`, no file. The Keychain is the store; it is per-user and already there.
* ONLY THE LAUNCH LINE calls this. scan, panel, fleet never need a value and never get one.
* THE VALUE TOUCHES NOTHING BUT THE CHILD ENV. The parent's os.environ is left alone and every
  resolved value is registered with `redact` so no log line can carry it.
* FAIL CLOSED. A reference that does not resolve means the server is not launched. The message
  names the reference, never a value.
* IDENTITY AS DECLARED. The reference is the login as far as fingerprint/credentials are
  concerned; the token behind it rotates and must not mint a new server.

Grammar: `keychain:<service>` or `keychain:<service>@<account>`. Anything else — `$VAR`,
`op://…`, `vault:…`, a literal — passes through byte for byte. Not ours to resolve here.
"""
from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping

from . import redact

PREFIX = "keychain:"

#: A resolver takes the whole reference (`keychain:svc@acct`) and returns the value, or None when
#: the item does not exist or cannot be read. Injectable so the suite never reaches the Keychain.
Resolver = Callable[[str], "str | None"]


class Unresolved(RuntimeError):
    """A `keychain:` reference the launch line could not resolve. Carries the exit code `wrap`
    returns (2: refused before the server started) and names the reference only."""

    exit_code = 2

    def __init__(self, reference: str, variable: str) -> None:
        self.reference = reference
        self.variable = variable
        super().__init__(
            f"{variable} is set to {reference} and that Keychain item could not be read. "
            f"The server was not started. Create the item in Keychain Access (service = the name "
            f"after keychain:) or point {variable} at an item that exists.")


def is_reference(value: str) -> bool:
    return isinstance(value, str) and value.startswith(PREFIX) and len(value) > len(PREFIX)


def parse(reference: str) -> tuple[str, str | None]:
    """`keychain:svc@acct` → ("svc", "acct"); `keychain:svc` → ("svc", None)."""
    body = reference[len(PREFIX):]
    service, sep, account = body.partition("@")
    return service, (account if sep and account else None)


def default_resolver(reference: str) -> str | None:
    """Read ONE generic-password item from the user's own Keychain. Read-only by construction:
    this function knows exactly one `security` verb. Any failure — no item, locked Keychain,
    `security` missing, timeout — is None, and the caller fails closed."""
    service, account = parse(reference)
    argv = ["security", "find-generic-password", "-s", service]
    if account:
        argv += ["-a", account]
    argv.append("-w")
    try:
        got = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if got.returncode != 0:
        return None
    value = got.stdout.rstrip("\r\n")
    return value or None


def child_env(declared: Mapping[str, str], *, resolve: Resolver | None = None) -> dict[str, str]:
    """The environment the SERVER gets: `declared` with every `keychain:` value replaced.

    `declared` is normally a copy of the launcher's own environment. It is never mutated; a new
    dict is returned. Raises Unresolved on the first reference that does not resolve, before any
    server starts.
    """
    resolver = resolve or default_resolver
    out = dict(declared)
    for key, value in declared.items():
        if not is_reference(value):
            continue
        got = resolver(value)
        if not got:
            raise Unresolved(value, key)
        redact.register_value(got)
        out[key] = got
    return out

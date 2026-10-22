"""A plain stdio MCP proxy: passes every byte through and logs each JSON-RPC request method (and tool name) to a file.

    python logproxy.py LOGFILE -- <server command...>
No mcpgawk code. Used to show that a check on the MCP connection sees calls an agent's tool-call hook does not.
"""
import json, subprocess, sys, threading

log_path = sys.argv[1]
cmd = sys.argv[sys.argv.index("--") + 1:]
child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
log = open(log_path, "a", buffering=1)


def upstream():
    for line in sys.stdin.buffer:
        try:
            msg = json.loads(line)
            if "method" in msg:
                name = (msg.get("params") or {}).get("name", "")
                log.write(json.dumps({"dir": "client->server", "method": msg["method"], "tool": name}) + "\n")
        except ValueError:
            pass
        child.stdin.write(line)
        child.stdin.flush()
    child.stdin.close()


threading.Thread(target=upstream, daemon=True).start()
for line in child.stdout:
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()
sys.exit(child.wait())

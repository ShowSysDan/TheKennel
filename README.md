# The Kennel

**Version 1.1.0**

A single-file Python dashboard that gathers all of our production tools into one
place ("our tools — one kennel"). Serves a card grid grouped by section, with
built-in search, an inline stream player for DPC Radio, and a web-based admin
editor. No dependencies beyond the Python 3 standard library.

## Files

| File        | Purpose                                                            |
|-------------|--------------------------------------------------------------------|
| `kennel.py` | The entire server: config, HTML templates, and HTTP handler.       |
| `data.json` | The tool list. Created automatically on first run; edited via the admin page. |

## Running

```bash
sudo python3 kennel.py
```

Port 80 requires root on Linux/macOS (Administrator on Windows). Host, port,
and the stream player are configured in the `SERVER CONFIG` and
`STREAM PLAYER CONFIG` blocks at the top of `kennel.py`.

- Dashboard: `http://<host>/`
- Admin editor: `http://<host>/kennel-admin` — add, edit, reorder, and delete
  tools; changes are written to `data.json` and take effect immediately.

## Troubleshooting history: intermittent 30–70 second page hangs (fixed in 1.1.0)

### Symptom

Sometimes the page would not load at all, then 30–70 seconds later it would
suddenly finish loading and work fine. The service daemon showed no errors, and
port 80 never actually closed.

### Root cause

Versions before 1.1.0 used `socketserver.TCPServer`, which is
**single-threaded**: it handles exactly one connection at a time, and the
request handler had **no read timeout**.

Modern browsers (Chrome, Edge, etc.) open speculative "preconnect" TCP
connections to speed up anticipated navigation. These sockets connect but may
never send an HTTP request. The old server would `accept()` one of these empty
connections and then block forever waiting for a request line — and while it
was blocked, **every other connection sat unanswered in the kernel's listen
queue**. The page finally loaded when the browser gave up on its idle socket
(browsers drop unused preconnects after roughly 30–60 seconds), which matches
the observed 30–70 second hangs exactly.

This is also why the daemon log was clean and port 80 appeared healthy: nothing
crashed and the port never closed. The kernel kept accepting and queueing
connections — the Python process was simply stuck reading a socket that would
never speak. The same stall could be triggered by any slow or half-open client:
a port scanner, a monitoring probe that only checks TCP connect (e.g. an Uptime
Kuma TCP monitor), or a flaky Wi-Fi client.

The bug was reproduced by opening a raw TCP socket to the server without
sending anything: all other requests timed out until that socket was closed,
after which they completed in ~10 ms.

### Fix (1.1.0)

1. **Threaded server** — `http.server.ThreadingHTTPServer` replaces
   `socketserver.TCPServer`. Each connection is handled in its own daemon
   thread, so one slow or silent client can no longer block anyone else.
   (`ThreadingHTTPServer` also sets `allow_reuse_address`, preserving the
   fast-restart fix from before.)
2. **Per-connection timeout** — the handler now sets `timeout = 10`, so a
   connection that sends nothing for 10 seconds is closed instead of held
   open indefinitely. Reaped connections show up in the log as
   `Request timed out` lines — those are harmless preconnects/probes being
   cleaned up, not errors.
3. **Consistent `Content-Length` on every response** (including 404s and API
   errors), so clients never wait on a response whose end they can't detect.
4. **Non-blocking web fonts** — the Google Fonts stylesheet now loads
   asynchronously. Previously it was render-blocking, so a client machine
   without internet access (common on the production network) would show a
   blank page until the fonts request timed out. The page now renders
   immediately with fallback fonts and upgrades when/if the fonts arrive.

## Version history

| Version | Changes |
|---------|---------|
| 1.1.0   | Fixed intermittent 30–70 s page hangs: threaded HTTP server, 10 s idle-connection timeout, `Content-Length` on all responses, async font loading. Version shown in page footers and startup banner. |
| 1.0.x   | Initial single-file server: card grid with sections and search, inline stream player with pre-buffering, `/kennel-admin` editor, `data.json` persistence, `SO_REUSEADDR` restart fix. |

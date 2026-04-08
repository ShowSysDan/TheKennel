#!/usr/bin/env python3
"""
The Kennel — single-file Python server
Run with:  sudo python3 kennel.py
(port 80 requires root on Linux/macOS; on Windows run as Administrator)
"""

# ═══════════════════════════════════════════════════════════════
#  SERVER CONFIG
# ───────────────────────────────────────────────────────────────
PORT = 80
HOST = ""           # "" = all interfaces; "127.0.0.1" = localhost only
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
#  STREAM PLAYER CONFIG
# ───────────────────────────────────────────────────────────────
STREAM_URL   = "http://10.201.2.102:5500/stream"
STREAM_NAME  = "DPC Radio"
SHOW_PLAYER  = True
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
#  TOOLS  — default data (seeds data.json on first run)
# ───────────────────────────────────────────────────────────────
TOOLS_DEFAULT = [
    {"name": "Uptime Kuma",           "url": "http://10.201.2.102:5400",                                                      "desc": "Production Network uptime monitor.",                            "section": "Monitoring"},
    {"name": "Uptime Kuma Dashboard", "url": "http://10.201.2.102:5400/status/dpcpn",                                          "desc": "Production Network uptime monitor dashboard.",                  "section": "Monitoring"},
    {"name": "FetchLog",              "url": "http://10.201.2.102:5200",                                                      "desc": "SysLog Server for Production Equipment",                        "section": "Monitoring"},
    {"name": "QSYS Status",           "url": "http://10.201.111.10/api-uci/v0/ucis/89b8c863-bbab-423d-9d85-72539864e4ab",     "desc": "WebUI for Qsys Status UCI",                                     "section": "Monitoring"},
    {"name": "WebRetriever",          "url": "http://10.1.248.193:7212",                                                      "desc": "Retrieves HTML & image content for display on the NDI network.", "section": "Media"},
    {"name": "Multiview 1",           "url": "http://10.1.248.191:8901",                                                      "desc": "Tractus Multiview for NDI.",                                    "section": "Media"},
    {"name": "Multiview 2",           "url": "http://10.1.248.192:8901",                                                      "desc": "Tractus Multiview for NDI.",                                    "section": "Media"},
    {"name": "Icecast",               "url": "http://10.201.2.102:5500/admin/",                                               "desc": "Radio Station Service",                                         "section": "Media"},
    {"name": "Bark Extractor",        "url": "http://10.201.2.102:5100",                                                      "desc": "Youtube audio downloader",                                      "section": "Media"},
    {"name": "Doggie Door",           "url": "http://10.201.2.101:5500",                                                      "desc": "Production WireGuard VPN.",                                     "section": "Network"},
    {"name": "LabVision",             "url": "http://10.201.2.102:5000",                                                      "desc": "ArtsVision API Manager",                                        "section": "Network"},
    {"name": "PawPad",                "url": "http://10.201.2.102:5300",                                                      "desc": "Basic task manager",                                            "section": "Management"},
    {"name": "Master Control",        "url": "http://10.201.111.10/api-uci/v0/ucis/88708d61-8956-4383-85a3-6ac35307b9db",     "desc": "WebUI for Master Control UCI",                                  "section": "Management"},
]
# ═══════════════════════════════════════════════════════════════


# ─── Nothing below this line normally needs editing ─────────────

import json
import pathlib
import http.server
import socketserver

DATA_FILE = pathlib.Path(__file__).with_name('data.json')


def load_tools():
    """Load tools from data.json; create it from defaults if missing."""
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding='utf-8'))['tools']
        except Exception:
            pass
    save_tools(TOOLS_DEFAULT)
    return list(TOOLS_DEFAULT)


def save_tools(tools_list):
    DATA_FILE.write_text(
        json.dumps({"tools": tools_list}, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>The Kennel</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --wood-dk:   #221208;
      --wood-md:   #2e1a0c;
      --wood-surf: #3d2410;
      --wood-hi:   #5a3818;
      --chain:     #6a7a62;
      --chain-dk:  #424e3c;
      --chain-hi:  #8a9a82;
      --rust:      #6e2006;
      --rust-lt:   #943010;
      --cream:     #cec3ae;
      --cream-dk:  #9a8e7a;
      --card-bg:   #1a0e06;
      --card-text: #bdb2a0;
      --card-sub:  #6a5e50;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      min-height: 100vh;
      font-family: 'Barlow', sans-serif;
      background-color: var(--wood-dk);
      background-image:
        repeating-linear-gradient(180deg, transparent 0px, transparent 68px, rgba(0,0,0,0.22) 68px, rgba(0,0,0,0.22) 71px),
        repeating-linear-gradient(176deg, transparent 0px, transparent 44px, rgba(0,0,0,0.025) 44px, rgba(0,0,0,0.025) 46px),
        linear-gradient(180deg, #261408 0%, #1e0e06 50%, #261408 100%);
    }
    body::before {
      content: '';
      position: fixed; inset: 0;
      pointer-events: none; z-index: 0;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='turbulence' baseFrequency='0.018 0.5' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0.2'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23n)' opacity='0.28'/%3E%3C/svg%3E");
      mix-blend-mode: multiply; opacity: 0.5;
    }
    .mesh-overlay {
      position: fixed; inset: 0; pointer-events: none; z-index: 1;
      background-image:
        repeating-linear-gradient(45deg, transparent, transparent 13px, rgba(80,100,72,0.12) 13px, rgba(80,100,72,0.12) 14px),
        repeating-linear-gradient(-45deg, transparent, transparent 13px, rgba(80,100,72,0.12) 13px, rgba(80,100,72,0.12) 14px);
      background-size: 20px 20px;
    }
    .beam {
      height: 14px; background: var(--wood-md);
      border-top: 1px solid var(--wood-hi); border-bottom: 2px solid rgba(0,0,0,0.85);
      box-shadow: 0 4px 14px rgba(0,0,0,0.7); position: relative; z-index: 3;
    }
    .beam::before, .beam::after {
      content: ''; position: absolute; top: 50%; transform: translateY(-50%);
      width: 9px; height: 9px; border-radius: 50%;
      background: radial-gradient(circle at 38% 38%, #7a5030, #1e0a02);
      border: 1px solid rgba(0,0,0,0.55);
    }
    .beam::before { left: 20px; } .beam::after { right: 20px; }
    .wrapper { position: relative; z-index: 2; max-width: 1120px; margin: 0 auto; padding: 0 24px 60px; }

    /* ── Header bar ── */
    .header-bar {
      display: flex; align-items: stretch; justify-content: space-between;
      border-left: 10px solid var(--wood-surf); border-right: 10px solid var(--wood-surf);
      background: var(--wood-md); border-bottom: 2px solid rgba(0,0,0,0.7);
      box-shadow: 0 6px 20px rgba(0,0,0,0.6); position: relative;
    }
    .header-bar::before, .header-bar::after {
      content: ''; position: absolute; top: 50%; transform: translateY(-50%);
      width: 8px; height: 8px; border-radius: 50%;
      background: radial-gradient(circle at 38% 38%, #7a5030, #1e0a02);
      border: 1px solid rgba(0,0,0,0.5); z-index: 2;
    }
    .header-bar::before { left: -15px; } .header-bar::after { right: -15px; }
    .sign {
      padding: 14px 32px 13px 24px; position: relative;
      border-right: 2px solid rgba(0,0,0,0.35); flex-shrink: 0;
      display: flex; flex-direction: column; justify-content: center;
    }
    .sign::before {
      content: ''; position: absolute; inset: 0; pointer-events: none;
      background: repeating-linear-gradient(172deg, transparent 0, transparent 9px, rgba(0,0,0,0.04) 9px, rgba(0,0,0,0.04) 10px);
    }
    .sign h1 {
      font-family: 'Playfair Display', serif; font-size: clamp(1.6rem, 3.2vw, 2.4rem); font-weight: 900;
      color: var(--cream); text-shadow: 1px 1px 0 #0e0602, 0 2px 8px rgba(0,0,0,0.5);
      letter-spacing: 0.04em; line-height: 1; position: relative; z-index: 1; white-space: nowrap;
    }
    .sign .tagline {
      font-family: 'Barlow Condensed', sans-serif; font-size: 0.62rem; font-weight: 600;
      letter-spacing: 0.4em; text-transform: uppercase; color: rgba(160,148,128,0.45);
      margin-top: 5px; position: relative; z-index: 1; white-space: nowrap;
    }

    /* ── Inline player ── */
    .player-inline {
      flex: 1; display: flex; align-items: stretch; overflow: hidden;
      border-right: 1px solid rgba(0,0,0,0.35);
    }
    .player-btn {
      align-self: stretch; width: 52px; background: rgba(0,0,0,0.25); border: none;
      border-right: 1px solid rgba(0,0,0,0.35); cursor: pointer; display: flex;
      align-items: center; justify-content: center; flex-shrink: 0;
      transition: background 0.15s; outline: none;
    }
    .player-btn:hover { background: rgba(0,0,0,0.4); }
    .player-btn:active { background: rgba(0,0,0,0.5); }
    .player-btn svg { width: 16px; height: 16px; fill: var(--cream); opacity: 0.85; transition: opacity 0.15s; }
    .player-btn:hover svg { opacity: 1; }
    .player-live { display: flex; align-items: center; gap: 7px; padding: 0 14px; border-right: 1px solid rgba(0,0,0,0.25); flex-shrink: 0; }
    .live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--card-sub); flex-shrink: 0; transition: background 0.3s, box-shadow 0.3s; }
    .live-dot.active { background: #c04020; box-shadow: 0 0 6px rgba(192,64,32,0.7); animation: pulse 1.8s ease-in-out infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
    .live-label { font-family: 'Barlow Condensed', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: var(--card-sub); transition: color 0.3s; }
    .live-label.active { color: #c04020; }
    .player-name { padding: 0 14px; border-right: 1px solid rgba(0,0,0,0.25); flex-shrink: 0; display: flex; align-items: center; }
    .player-name span { font-family: 'Barlow Condensed', sans-serif; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream-dk); opacity: 0.55; }
    .player-timer { padding: 0 16px; border-right: 1px solid rgba(0,0,0,0.25); flex-shrink: 0; display: flex; align-items: center; }
    .player-timer span { font-family: 'Barlow Condensed', sans-serif; font-size: 0.95rem; font-weight: 600; letter-spacing: 0.12em; color: var(--cream); opacity: 0.65; font-variant-numeric: tabular-nums; }
    .player-spacer { flex: 1; }
    .player-volume { display: flex; align-items: center; gap: 10px; padding: 0 16px; border-left: 1px solid rgba(0,0,0,0.25); flex-shrink: 0; }
    .player-volume svg { width: 13px; height: 13px; fill: var(--cream-dk); opacity: 0.5; flex-shrink: 0; }
    .volume-slider { -webkit-appearance: none; appearance: none; width: 88px; height: 3px; background: var(--chain-dk); border-radius: 2px; outline: none; cursor: pointer; }
    .volume-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; border-radius: 50%; background: radial-gradient(circle at 38% 38%, #c8a870, #6b3a18); border: 1px solid rgba(0,0,0,0.4); box-shadow: 0 1px 4px rgba(0,0,0,0.5); cursor: pointer; transition: transform 0.1s; }
    .volume-slider::-webkit-slider-thumb:hover { transform: scale(1.2); }
    .volume-slider::-moz-range-thumb { width: 12px; height: 12px; border-radius: 50%; background: radial-gradient(circle at 38% 38%, #c8a870, #6b3a18); border: 1px solid rgba(0,0,0,0.4); cursor: pointer; }

    /* ── Search area ── */
    .search-area { display: flex; justify-content: flex-end; align-items: center; padding: 0 20px 0 0; flex-shrink: 0; }
    .search-wrap { display: flex; align-items: stretch; height: 34px; }
    .search-wrap input {
      background: rgba(0,0,0,0.3); border: 1px solid var(--chain-dk); border-right: none;
      color: var(--cream); font-family: 'Barlow Condensed', sans-serif; font-size: 0.85rem;
      letter-spacing: 0.14em; text-transform: uppercase; padding: 0 16px; width: 200px; height: 34px;
      outline: none; display: block; transition: border-color 0.2s, background 0.2s;
      -webkit-appearance: none; appearance: none;
    }
    .search-wrap input::placeholder { color: var(--card-sub); opacity: 0.9; }
    .search-wrap input:focus { border-color: var(--chain); background: rgba(0,0,0,0.42); }
    .search-wrap .search-btn {
      background: rgba(0,0,0,0.3); border: 1px solid var(--chain-dk); border-left: none;
      color: var(--card-sub); width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .search-wrap .search-btn svg { width: 14px; height: 14px; stroke: var(--card-sub); fill: none; stroke-width: 2; stroke-linecap: round; }

    /* ── Kennel grid ── */
    .kennel-frame { position: relative; padding: 10px 0; margin-top: 10px; }
    .kennel-frame::before, .kennel-frame::after {
      content: ''; position: absolute; left: -10px; right: -10px; height: 10px;
      background: var(--wood-surf); border-top: 1px solid var(--wood-hi);
      border-bottom: 2px solid rgba(0,0,0,0.8); box-shadow: 0 3px 10px rgba(0,0,0,0.5); z-index: 5;
    }
    .kennel-frame::before { top: 0; } .kennel-frame::after { bottom: 0; }
    #kennel-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(265px, 1fr)); gap: 0;
      border: 1px solid var(--wood-md); outline: 6px solid var(--wood-surf); background: var(--card-bg);
      box-shadow: 0 0 0 10px var(--wood-md), 0 0 0 14px var(--wood-dk), 0 18px 55px rgba(0,0,0,0.85);
    }
    .section-header {
      grid-column: 1 / -1; padding: 9px 16px 7px;
      font-family: 'Barlow Condensed', sans-serif; font-size: 0.6rem; font-weight: 700;
      letter-spacing: 0.38em; text-transform: uppercase; color: var(--cream-dk);
      background: rgba(0,0,0,0.18); border-bottom: 1px solid rgba(0,0,0,0.35); opacity: 0.65;
    }
    .kennel-card {
      position: relative; background: var(--card-bg); text-decoration: none;
      display: flex; flex-direction: column; border-right: 2px solid var(--wood-dk);
      border-bottom: 2px solid var(--wood-dk);
      transition: background 0.15s, transform 0.15s, box-shadow 0.15s, border-color 0.15s;
      overflow: hidden; animation: fadeIn 0.32s both; min-height: 175px;
    }
    .kennel-card::before {
      content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 0;
      background-image:
        repeating-linear-gradient(45deg, transparent, transparent 9px, rgba(255,255,255,0.015) 9px, rgba(255,255,255,0.015) 10px),
        repeating-linear-gradient(-45deg, transparent, transparent 9px, rgba(255,255,255,0.015) 9px, rgba(255,255,255,0.015) 10px);
      background-size: 14px 14px;
    }
    .kennel-card:hover {
      background: #221408; transform: scale(1.022) translateY(-3px); z-index: 10;
      box-shadow: 0 14px 36px rgba(0,0,0,0.7), inset 0 0 0 1px var(--rust-lt); border-color: var(--rust);
    }
    .card-rail {
      height: 8px; background: var(--wood-surf); border-bottom: 1px solid rgba(0,0,0,0.75);
      position: relative; z-index: 1; flex-shrink: 0; transition: background 0.15s;
    }
    .kennel-card:hover .card-rail { background: var(--rust); }
    .card-rail-tag {
      position: absolute; right: 8px; top: -1px; background: var(--wood-md);
      border: 1px solid var(--wood-hi); border-top: none;
      font-family: 'Barlow Condensed', sans-serif; font-size: 0.5rem; font-weight: 700;
      letter-spacing: 0.12em; color: var(--cream-dk); padding: 1px 5px 2px; z-index: 2; opacity: 0.6;
    }
    .card-body { padding: 12px 15px 15px; position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column; gap: 3px; }
    .card-name { font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700; color: var(--cream); line-height: 1.2; }
    .card-url { font-family: 'Barlow Condensed', sans-serif; font-size: 0.62rem; letter-spacing: 0.08em; color: var(--chain); text-transform: uppercase; opacity: 0.55; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--chain-dk), transparent); opacity: 0.45; margin: 5px 0; }
    .card-desc { font-size: 0.8rem; color: var(--card-sub); line-height: 1.6; flex: 1; }
    .card-cta { font-family: 'Barlow Condensed', sans-serif; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.26em; text-transform: uppercase; color: var(--rust-lt); margin-top: 8px; opacity: 0; transform: translateY(4px); transition: opacity 0.16s, transform 0.16s; }
    .kennel-card:hover .card-cta { opacity: 1; transform: translateY(0); }
    #empty-msg { display: none; grid-column: 1/-1; text-align: center; color: var(--card-sub); font-family: 'Playfair Display', serif; font-size: 0.95rem; padding: 52px 0; opacity: 0.45; }
    footer { text-align: center; margin-top: 40px; font-family: 'Barlow Condensed', sans-serif; font-size: 0.62rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--wood-hi); opacity: 0.3; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* ── Mobile ── */
    @media (max-width: 640px) {
      .header-bar { flex-direction: column; align-items: flex-start; }
      .sign { border-right: none; border-bottom: 2px solid rgba(0,0,0,0.35); width: 100%; }
      .player-inline { border-right: none; border-left: none; border-bottom: 2px solid rgba(0,0,0,0.35); width: 100%; }
      .search-area { padding: 10px 16px; width: 100%; justify-content: flex-start; }
      .search-wrap input { flex: 1; width: auto; }
    }
  </style>
</head>
<body>
<div class="mesh-overlay"></div>
<div class="beam"></div>
<div class="wrapper">
  <div class="header-bar">
    <div class="sign">
      <h1>The Kennel</h1>
      <div class="tagline">Our tools &mdash; one kennel</div>
    </div>
    <div class="player-inline" id="player-section">
      <button class="player-btn" id="player-btn" title="Play stream">
        <svg id="icon-play" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M8 5v14l11-7z"/></svg>
        <svg id="icon-stop" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="display:none;"><rect x="5" y="5" width="14" height="14" rx="1"/></svg>
      </button>
      <div class="player-live">
        <div class="live-dot" id="live-dot"></div>
        <span class="live-label" id="live-label">Live</span>
      </div>
      <div class="player-name"><span id="player-stream-name">Stream</span></div>
      <div class="player-timer"><span id="player-timer">0:00:00</span></div>
      <div class="player-spacer"></div>
      <div class="player-volume">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
        <input type="range" class="volume-slider" id="volume-slider" min="0" max="1" step="0.02" value="0.8"/>
      </div>
    </div>
    <div class="search-area">
      <div class="search-wrap">
        <input type="text" id="search-input" placeholder="Search&hellip;" autocomplete="off"/>
        <div class="search-btn">
          <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6.5" cy="6.5" r="4.5"/>
            <line x1="10.5" y1="10.5" x2="14" y2="14"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
  <div class="kennel-frame">
    <div id="kennel-grid">
      <div id="empty-msg">No dogs in this run.</div>
    </div>
  </div>
  <footer>The Kennel</footer>
</div>

<script>
  const streamUrl  = __STREAM_URL__;
  const streamName = __STREAM_NAME__;
  const showPlayer = __SHOW_PLAYER__;
  const tools      = __TOOLS__;

  const grid     = document.getElementById('kennel-grid');
  const emptyMsg = document.getElementById('empty-msg');
  const search   = document.getElementById('search-input');

  function appendCard(tool, i) {
    const tag = tool.tag || ('RUN ' + String(i + 1).padStart(2, '0'));
    const displayUrl = tool.url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0];
    const card = document.createElement('a');
    card.className = 'kennel-card';
    card.href = tool.url;
    card.target = '_blank';
    card.rel = 'noopener noreferrer';
    card.title = tool.name;
    card.style.animationDelay = (i * 0.05) + 's';
    card.innerHTML =
      '<div class="card-rail"><span class="card-rail-tag">' + tag + '</span></div>' +
      '<div class="card-body">' +
        '<div class="card-name">' + tool.name + '</div>' +
        '<div class="card-url">' + displayUrl + '</div>' +
        '<div class="card-divider"></div>' +
        '<div class="card-desc">' + (tool.desc || '') + '</div>' +
        '<div class="card-cta">Open &rarr;</div>' +
      '</div>';
    grid.insertBefore(card, emptyMsg);
  }

  function buildCards(list) {
    grid.querySelectorAll('.kennel-card, .section-header').forEach(function(c) { c.remove(); });
    if (list.length === 0) { emptyMsg.style.display = 'block'; return; }
    emptyMsg.style.display = 'none';
    var groups = {}, order = [];
    list.forEach(function(t) {
      var s = t.section || 'Other';
      if (!groups[s]) { groups[s] = []; order.push(s); }
      groups[s].push(t);
    });
    var idx = 0;
    order.forEach(function(sec) {
      var hdr = document.createElement('div');
      hdr.className = 'section-header';
      hdr.textContent = sec;
      grid.insertBefore(hdr, emptyMsg);
      groups[sec].forEach(function(t) { appendCard(t, idx++); });
    });
  }

  function filterTools(q) {
    if (!q) return tools;
    var lq = q.toLowerCase();
    return tools.filter(function(t) {
      return t.name.toLowerCase().includes(lq) ||
             (t.desc || '').toLowerCase().includes(lq) ||
             t.url.toLowerCase().includes(lq);
    });
  }

  function refresh() { buildCards(filterTools(search.value.trim())); }

  search.addEventListener('input', refresh);
  buildCards(tools);

  // ── Player ──────────────────────────────────────────────────────
  var playerSection = document.getElementById('player-section');
  if (!showPlayer) {
    playerSection.style.display = 'none';
  } else {
    document.getElementById('player-stream-name').textContent = streamName;
    var btn       = document.getElementById('player-btn');
    var iconPlay  = document.getElementById('icon-play');
    var iconStop  = document.getElementById('icon-stop');
    var liveDot   = document.getElementById('live-dot');
    var liveLabel = document.getElementById('live-label');
    var timerEl   = document.getElementById('player-timer');
    var volSlider = document.getElementById('volume-slider');
    var audio = null, playing = false, startTime = null, timerTick = null;

    function formatTime(secs) {
      var h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60), s = Math.floor(secs % 60);
      return h + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
    }
    function startTimer() {
      startTime = Date.now();
      timerTick = setInterval(function() { timerEl.textContent = formatTime((Date.now() - startTime) / 1000); }, 1000);
    }
    function stopTimer() { clearInterval(timerTick); timerEl.textContent = '0:00:00'; }
    function setPlaying(state) {
      playing = state;
      iconPlay.style.display = state ? 'none' : '';
      iconStop.style.display = state ? '' : 'none';
      liveDot.classList.toggle('active', state);
      liveLabel.classList.toggle('active', state);
      btn.title = state ? 'Stop stream' : 'Play stream';
    }

    // Pre-buffer: silently load the stream on first interaction so play is instant
    function initAudio() {
      if (audio) return;
      audio = new Audio(streamUrl);
      audio.muted = true;
      audio.volume = parseFloat(volSlider.value);
      audio.play().catch(function() {});
      audio.addEventListener('error', function() { if (!playing) audio = null; }, { once: true });
    }

    // Start pre-buffering as soon as user hovers the player or clicks anywhere
    playerSection.addEventListener('mouseenter', initAudio);
    document.addEventListener('click', initAudio, { once: true });

    btn.addEventListener('click', function() {
      if (!playing) {
        if (!audio) {
          audio = new Audio(streamUrl);
          audio.volume = parseFloat(volSlider.value);
        } else {
          audio.volume = parseFloat(volSlider.value);
        }
        audio.muted = false;
        audio.play().catch(function() {});
        setPlaying(true);
        startTimer();
        audio.addEventListener('error', function() { setPlaying(false); stopTimer(); audio = null; }, { once: true });
      } else {
        // Mute instead of disconnect — stays buffered for instant resume
        audio.muted = true;
        setPlaying(false);
        stopTimer();
      }
    });

    volSlider.addEventListener('input', function() {
      var v = parseFloat(volSlider.value);
      if (audio) audio.volume = v;
    });
  }
</script>
</body>
</html>"""



SETTINGS_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>The Kennel &mdash; Admin</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --wood-dk:   #221208;
      --wood-md:   #2e1a0c;
      --wood-surf: #3d2410;
      --wood-hi:   #5a3818;
      --chain:     #6a7a62;
      --chain-dk:  #424e3c;
      --rust:      #6e2006;
      --rust-lt:   #943010;
      --cream:     #cec3ae;
      --cream-dk:  #9a8e7a;
      --card-bg:   #1a0e06;
      --card-sub:  #6a5e50;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      min-height: 100vh; font-family: 'Barlow', sans-serif;
      background-color: var(--wood-dk);
      background-image:
        repeating-linear-gradient(180deg, transparent 0px, transparent 68px, rgba(0,0,0,0.22) 68px, rgba(0,0,0,0.22) 71px),
        linear-gradient(180deg, #261408 0%, #1e0e06 50%, #261408 100%);
    }
    body::before {
      content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='turbulence' baseFrequency='0.018 0.5' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0.2'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23n)' opacity='0.28'/%3E%3C/svg%3E");
      mix-blend-mode: multiply; opacity: 0.5;
    }
    .mesh-overlay {
      position: fixed; inset: 0; pointer-events: none; z-index: 1;
      background-image:
        repeating-linear-gradient(45deg, transparent, transparent 13px, rgba(80,100,72,0.12) 13px, rgba(80,100,72,0.12) 14px),
        repeating-linear-gradient(-45deg, transparent, transparent 13px, rgba(80,100,72,0.12) 13px, rgba(80,100,72,0.12) 14px);
      background-size: 20px 20px;
    }
    .beam {
      height: 14px; background: var(--wood-md);
      border-top: 1px solid var(--wood-hi); border-bottom: 2px solid rgba(0,0,0,0.85);
      box-shadow: 0 4px 14px rgba(0,0,0,0.7); position: relative; z-index: 3;
    }
    .beam::before, .beam::after {
      content: ''; position: absolute; top: 50%; transform: translateY(-50%);
      width: 9px; height: 9px; border-radius: 50%;
      background: radial-gradient(circle at 38% 38%, #7a5030, #1e0a02);
      border: 1px solid rgba(0,0,0,0.55);
    }
    .beam::before { left: 20px; } .beam::after { right: 20px; }
    .wrapper { position: relative; z-index: 2; max-width: 1280px; margin: 0 auto; padding: 0 24px 60px; }
    .admin-header {
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
      padding: 18px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 22px;
    }
    .back-link {
      font-family: 'Barlow Condensed', sans-serif; font-size: 0.7rem; font-weight: 600;
      letter-spacing: 0.2em; text-transform: uppercase; color: var(--card-sub);
      text-decoration: none; transition: color 0.15s; flex-shrink: 0;
    }
    .back-link:hover { color: var(--cream); }
    .admin-title {
      font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700;
      color: var(--cream); text-shadow: 1px 1px 0 #0e0602;
      letter-spacing: 0.04em; flex: 1; text-align: center;
    }
    .admin-actions { display: flex; gap: 10px; flex-shrink: 0; }
    .action-btn {
      font-family: 'Barlow Condensed', sans-serif; font-size: 0.68rem; font-weight: 700;
      letter-spacing: 0.2em; text-transform: uppercase; padding: 8px 18px; cursor: pointer;
      border: 1px solid var(--chain-dk); background: rgba(0,0,0,0.3); color: var(--cream-dk);
      transition: border-color 0.15s, color 0.15s, background 0.15s; outline: none;
    }
    .action-btn:hover { border-color: var(--chain); color: var(--cream); }
    .action-btn.primary { border-color: var(--rust-lt); color: var(--rust-lt); background: rgba(110,32,6,0.18); }
    .action-btn.primary:hover { background: rgba(110,32,6,0.32); border-color: var(--cream); color: var(--cream); }
    .status-msg {
      display: none; font-family: 'Barlow Condensed', sans-serif; font-size: 0.7rem; font-weight: 600;
      letter-spacing: 0.2em; text-transform: uppercase; padding: 9px 14px;
      margin-bottom: 16px; text-align: center;
    }
    .status-msg.visible { display: block; }
    .status-msg.success { color: #6a9a62; border: 1px solid rgba(106,154,98,0.35); background: rgba(106,154,98,0.08); }
    .status-msg.error   { color: var(--rust-lt); border: 1px solid rgba(148,48,16,0.35); background: rgba(148,48,16,0.08); }
    .table-wrap { overflow-x: auto; }
    table.tools-table {
      width: 100%; border-collapse: collapse;
      border: 1px solid var(--chain-dk); outline: 4px solid var(--wood-surf); background: var(--card-bg);
      box-shadow: 0 0 0 8px var(--wood-md), 0 0 0 12px var(--wood-dk), 0 14px 40px rgba(0,0,0,0.8);
    }
    .tools-table thead tr { background: var(--wood-surf); }
    .tools-table th {
      font-family: 'Barlow Condensed', sans-serif; font-size: 0.58rem; font-weight: 700;
      letter-spacing: 0.3em; text-transform: uppercase; color: var(--cream-dk);
      padding: 10px 10px; text-align: left; border-bottom: 2px solid rgba(0,0,0,0.5); white-space: nowrap;
    }
    .tools-table td { padding: 5px 6px; border-bottom: 1px solid rgba(0,0,0,0.3); vertical-align: middle; }
    .tools-table tr.tool-row:last-child td { border-bottom: none; }
    .tools-table tr.tool-row:hover td { background: rgba(255,255,255,0.02); }
    .tool-input {
      width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--chain-dk);
      color: var(--cream); font-family: 'Barlow', sans-serif; font-size: 0.78rem;
      padding: 5px 8px; outline: none; transition: border-color 0.15s, background 0.15s;
    }
    .tool-input:focus { border-color: var(--chain); background: rgba(0,0,0,0.5); }
    .tool-input.url-input { font-family: 'Barlow Condensed', sans-serif; font-size: 0.72rem; letter-spacing: 0.03em; }
    .tool-input.tag-input { width: 72px; }
    .row-actions { white-space: nowrap; text-align: center; padding: 5px 8px; }
    .row-btn {
      background: none; border: 1px solid transparent; color: var(--card-sub);
      font-size: 0.65rem; padding: 3px 6px; cursor: pointer; outline: none;
      transition: color 0.15s, border-color 0.15s; margin: 0 1px; line-height: 1;
    }
    .row-btn:hover { color: var(--cream); border-color: var(--chain-dk); }
    .row-btn.del-btn:hover { color: var(--rust-lt); border-color: var(--rust); }
    footer { text-align: center; margin-top: 40px; font-family: 'Barlow Condensed', sans-serif; font-size: 0.62rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--wood-hi); opacity: 0.3; }
  </style>
</head>
<body>
<div class="mesh-overlay"></div>
<div class="beam"></div>
<div class="wrapper">
  <div class="admin-header">
    <a href="/" class="back-link">&larr; Back to Kennel</a>
    <div class="admin-title">The Kennel &mdash; Admin</div>
    <div class="admin-actions">
      <button class="action-btn" id="add-btn">+ Add Tool</button>
      <button class="action-btn primary" id="save-btn">Save Changes</button>
    </div>
  </div>
  <div class="status-msg" id="status-msg"></div>
  <div class="table-wrap">
    <table class="tools-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>URL</th>
          <th>Description</th>
          <th>Section</th>
          <th>Tag</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="tools-body"></tbody>
    </table>
  </div>
  <footer>The Kennel &mdash; Admin</footer>
</div>
<script>
  var initialTools = __TOOLS__;
  var tbody = document.getElementById('tools-body');

  function createRow(tool) {
    var tr = document.createElement('tr');
    tr.className = 'tool-row';

    var fields = [
      { key: 'name',    placeholder: 'Name',        cls: '' },
      { key: 'url',     placeholder: 'http://\u2026', cls: ' url-input' },
      { key: 'desc',    placeholder: 'Description',  cls: '' },
      { key: 'section', placeholder: 'Section',      cls: '' },
      { key: 'tag',     placeholder: 'Auto',          cls: ' tag-input' }
    ];

    fields.forEach(function(f) {
      var td  = document.createElement('td');
      var inp = document.createElement('input');
      inp.type = 'text';
      inp.className = 'tool-input' + f.cls;
      inp.placeholder = f.placeholder;
      inp.value = tool[f.key] || '';
      td.appendChild(inp);
      tr.appendChild(td);
    });

    var actTd = document.createElement('td');
    actTd.className = 'row-actions';

    var upBtn = document.createElement('button');
    upBtn.className = 'row-btn'; upBtn.textContent = '\u25b2'; upBtn.title = 'Move up';
    upBtn.addEventListener('click', function() { if (tr.previousElementSibling) tbody.insertBefore(tr, tr.previousElementSibling); });

    var dnBtn = document.createElement('button');
    dnBtn.className = 'row-btn'; dnBtn.textContent = '\u25bc'; dnBtn.title = 'Move down';
    dnBtn.addEventListener('click', function() { if (tr.nextElementSibling) tbody.insertBefore(tr.nextElementSibling, tr); });

    var delBtn = document.createElement('button');
    delBtn.className = 'row-btn del-btn'; delBtn.textContent = '\u2715'; delBtn.title = 'Delete';
    delBtn.addEventListener('click', function() { if (confirm('Remove this tool?')) tr.remove(); });

    actTd.appendChild(upBtn);
    actTd.appendChild(dnBtn);
    actTd.appendChild(delBtn);
    tr.appendChild(actTd);
    return tr;
  }

  initialTools.forEach(function(t) { tbody.appendChild(createRow(t)); });

  document.getElementById('add-btn').addEventListener('click', function() {
    var row = createRow({ name: '', url: '', desc: '', section: '', tag: '' });
    tbody.appendChild(row);
    row.querySelector('input').focus();
  });

  document.getElementById('save-btn').addEventListener('click', async function() {
    var rows  = Array.from(tbody.querySelectorAll('.tool-row'));
    var tools = rows.map(function(tr) {
      var inputs = Array.from(tr.querySelectorAll('input'));
      var obj = {
        name:    inputs[0].value.trim(),
        url:     inputs[1].value.trim(),
        desc:    inputs[2].value.trim(),
        section: inputs[3].value.trim()
      };
      var tag = inputs[4].value.trim();
      if (tag) obj.tag = tag;
      return obj;
    }).filter(function(t) { return t.name || t.url; });

    var statusEl = document.getElementById('status-msg');
    statusEl.textContent = 'Saving\u2026';
    statusEl.className = 'status-msg visible';

    try {
      var res = await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tools: tools })
      });
      if (res.ok) {
        statusEl.textContent = 'Saved successfully.';
        statusEl.className = 'status-msg visible success';
      } else {
        statusEl.textContent = 'Server error \u2014 changes not saved.';
        statusEl.className = 'status-msg visible error';
      }
    } catch (e) {
      statusEl.textContent = 'Network error \u2014 check server.';
      statusEl.className = 'status-msg visible error';
    }
    setTimeout(function() { statusEl.className = 'status-msg'; }, 4000);
  });
</script>
</body>
</html>"""



def build_html(tools) -> str:
    """Inject Python config values into the HTML template."""
    html = HTML_TEMPLATE
    html = html.replace("__STREAM_URL__",  json.dumps(STREAM_URL))
    html = html.replace("__STREAM_NAME__", json.dumps(STREAM_NAME))
    html = html.replace("__SHOW_PLAYER__", "true" if SHOW_PLAYER else "false")
    html = html.replace("__TOOLS__",       json.dumps(tools, ensure_ascii=False))
    return html


def build_settings_html(tools) -> str:
    return SETTINGS_TEMPLATE.replace("__TOOLS__", json.dumps(tools, ensure_ascii=False))


class KennelHandler(http.server.BaseHTTPRequestHandler):
    _page = None  # main page cache; rebuilt after every /api/save

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', ''):
            self._serve(KennelHandler._page)
        elif path == '/kennel-admin':
            self._serve(build_settings_html(load_tools()))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        path = self.path.split('?')[0]
        if path == '/api/save':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body   = json.loads(self.rfile.read(length).decode('utf-8'))
                tools  = body.get('tools', [])
                save_tools(tools)
                KennelHandler._page = build_html(load_tools())
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def _serve(self, html):
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} — {fmt % args}")


if __name__ == "__main__":
    tools = load_tools()
    KennelHandler._page = build_html(tools)

    with socketserver.TCPServer((HOST, PORT), KennelHandler) as httpd:
        httpd.allow_reuse_address = True
        addr = "http://localhost" + (f":{PORT}" if PORT != 80 else "")
        print(f"The Kennel is running at {addr}")
        print(f"  Admin:  {addr}/kennel-admin")
        print("Press Ctrl-C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")

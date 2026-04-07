#!/usr/bin/env python3
"""
The Kennel — single-file Python server
Run with:  sudo python3 kennel_server.py
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
#  TOOLS  — edit this list to populate the cards
# ───────────────────────────────────────────────────────────────
#  Each entry is a dict with:
#    name  (str)  — card title
#    url   (str)  — link destination (opens in new tab)
#    desc  (str)  — short description shown on the card
#    tag   (str, optional) — run label; auto-generated if omitted
# ═══════════════════════════════════════════════════════════════
TOOLS = [
    {
        "name": "Uptime Kuma",
        "url":  "http://10.201.2.102:5400",
        "desc": "Production Network uptime monitor.",
    },
    {
        "name": "Uptime Kuma Dashboard",
        "url":  "http://10.201.2.102:5400/status/dpcpn",
        "desc": "Production Network uptime monitor dashboard.",
    },
    {
        "name": "WebRetriever",
        "url":  "http://10.1.248.193:7212",
        "desc": "Retrieves HTML & image content for display on the NDI network.",
    },
    {
        "name": "Multiview 1",
        "url":  "http://10.1.248.191:8901",
        "desc": "Tractus Multiview for NDI.",
    },
    {
        "name": "Multiview 2",
        "url":  "http://10.1.248.192:8901",
        "desc": "Tractus Multiview for NDI.",
    },
    {
        "name": "FetchLog",
        "url":  "http://10.201.2.102:5200",
        "desc": "SysLog Server for Production Equipment",
    },
    {
        "name": "Icecast",
        "url":  "http://10.201.2.102:5500/admin/",
        "desc": "Radio Station Service",
    },
    {
        "name": "Doggie Door",
        "url":  "http://10.201.2.101:5500",
        "desc": "Production WireGuard VPN.",
    },
    {
        "name": "LabVision",
        "url":  "http://10.201.2.102:5000",
        "desc": "ArtsVision API Manager",
    },
    {
        "name": "Bark Extractor",
        "url":  "http://10.201.2.102:5100",
        "desc": "Youtube audio downloader",
    },
    {
        "name": "PawPad",
        "url":  "http://10.201.2.102:5300",
        "desc": "Basic task manager",
    },
    {
        "name": "Master Control",
        "url":  "http://10.201.111.10/api-uci/v0/ucis/88708d61-8956-4383-85a3-6ac35307b9db",
        "desc": "WebUI for Master Control UCI",
    },
    {
        "name": "QSYS Status",
        "url":  "http://10.201.111.10/api-uci/v0/ucis/89b8c863-bbab-423d-9d85-72539864e4ab",
        "desc": "WebUI for Qsys Status UCI",
    },

]
# ═══════════════════════════════════════════════════════════════


# ─── Nothing below this line normally needs editing ─────────────

import json
import http.server
import socketserver

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
    .header-bar {
      display: flex; align-items: center; justify-content: space-between; gap: 24px;
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
    .sign { padding: 14px 32px 13px 24px; position: relative; border-right: 2px solid rgba(0,0,0,0.35); flex-shrink: 0; }
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
    .search-area { flex: 1; display: flex; justify-content: flex-end; align-items: center; padding: 0 20px 0 0; }
    .search-wrap { display: flex; align-items: stretch; height: 34px; }
    .search-wrap input {
      background: rgba(0,0,0,0.3); border: 1px solid var(--chain-dk); border-right: none;
      color: var(--cream); font-family: 'Barlow Condensed', sans-serif; font-size: 0.85rem;
      letter-spacing: 0.14em; text-transform: uppercase; padding: 0 16px; width: 240px; height: 34px;
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
    .kennel-frame { position: relative; padding: 10px 0; margin-top: 28px; }
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
    @media (max-width: 600px) {
      .header-bar { flex-direction: column; align-items: flex-start; gap: 0; }
      .sign { border-right: none; border-bottom: 2px solid rgba(0,0,0,0.35); width: 100%; }
      .search-area { padding: 10px 16px; width: 100%; justify-content: flex-start; }
      .search-wrap input { flex: 1; width: auto; }
    }
    .player-section { margin-top: 14px; }
    .player-bar {
      background: var(--wood-md); border-left: 10px solid var(--wood-surf); border-right: 10px solid var(--wood-surf);
      border-top: 1px solid var(--wood-hi); border-bottom: 2px solid rgba(0,0,0,0.8);
      box-shadow: 0 6px 24px rgba(0,0,0,0.65); display: flex; align-items: center;
      position: relative; height: 56px; overflow: hidden;
    }
    .player-bar::before, .player-bar::after {
      content: ''; position: absolute; top: 50%; transform: translateY(-50%);
      width: 8px; height: 8px; border-radius: 50%;
      background: radial-gradient(circle at 38% 38%, #7a5030, #1e0a02);
      border: 1px solid rgba(0,0,0,0.5); z-index: 2;
    }
    .player-bar::before { left: -15px; } .player-bar::after { right: -15px; }
    .player-btn {
      width: 56px; height: 56px; background: rgba(0,0,0,0.25); border: none;
      border-right: 2px solid rgba(0,0,0,0.35); cursor: pointer; display: flex;
      align-items: center; justify-content: center; flex-shrink: 0;
      transition: background 0.15s; outline: none;
    }
    .player-btn:hover { background: rgba(0,0,0,0.4); } .player-btn:active { background: rgba(0,0,0,0.5); }
    .player-btn svg { width: 18px; height: 18px; fill: var(--cream); opacity: 0.85; transition: opacity 0.15s; }
    .player-btn:hover svg { opacity: 1; }
    .player-live { display: flex; align-items: center; gap: 7px; padding: 0 18px; border-right: 1px solid rgba(0,0,0,0.3); flex-shrink: 0; }
    .live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--card-sub); flex-shrink: 0; transition: background 0.3s, box-shadow 0.3s; }
    .live-dot.active { background: #c04020; box-shadow: 0 0 6px rgba(192,64,32,0.7); animation: pulse 1.8s ease-in-out infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
    .live-label { font-family: 'Barlow Condensed', sans-serif; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: var(--card-sub); transition: color 0.3s; }
    .live-label.active { color: #c04020; }
    .player-name { padding: 0 18px; border-right: 1px solid rgba(0,0,0,0.3); flex-shrink: 0; }
    .player-name span { font-family: 'Barlow Condensed', sans-serif; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream-dk); opacity: 0.55; }
    .player-timer { padding: 0 20px; border-right: 1px solid rgba(0,0,0,0.3); flex-shrink: 0; }
    .player-timer span { font-family: 'Barlow Condensed', sans-serif; font-size: 1rem; font-weight: 600; letter-spacing: 0.12em; color: var(--cream); opacity: 0.65; font-variant-numeric: tabular-nums; }
    .player-spacer { flex: 1; }
    .player-volume { display: flex; align-items: center; gap: 11px; padding: 0 20px; border-left: 1px solid rgba(0,0,0,0.3); flex-shrink: 0; }
    .player-volume svg { width: 14px; height: 14px; fill: var(--cream-dk); opacity: 0.5; flex-shrink: 0; }
    .volume-slider { -webkit-appearance: none; appearance: none; width: 100px; height: 3px; background: var(--chain-dk); border-radius: 2px; outline: none; cursor: pointer; }
    .volume-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 13px; height: 13px; border-radius: 50%; background: radial-gradient(circle at 38% 38%, #c8a870, #6b3a18); border: 1px solid rgba(0,0,0,0.4); box-shadow: 0 1px 4px rgba(0,0,0,0.5); cursor: pointer; transition: transform 0.1s; }
    .volume-slider::-webkit-slider-thumb:hover { transform: scale(1.2); }
    .volume-slider::-moz-range-thumb { width: 13px; height: 13px; border-radius: 50%; background: radial-gradient(circle at 38% 38%, #c8a870, #6b3a18); border: 1px solid rgba(0,0,0,0.4); cursor: pointer; }
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
  <div class="player-section" id="player-section">
    <div class="player-bar">
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
  </div>
  <footer>The Kennel</footer>
</div>

<script>
  // Injected from Python config
  const streamUrl  = __STREAM_URL__;
  const streamName = __STREAM_NAME__;
  const showPlayer = __SHOW_PLAYER__;
  const tools      = __TOOLS__;

  const grid     = document.getElementById('kennel-grid');
  const emptyMsg = document.getElementById('empty-msg');
  const search   = document.getElementById('search-input');

  function buildCards(list) {
    grid.querySelectorAll('.kennel-card').forEach(c => c.remove());
    if (list.length === 0) { emptyMsg.style.display = 'block'; return; }
    emptyMsg.style.display = 'none';
    list.forEach((tool, i) => {
      const tag = tool.tag || `RUN ${String(i + 1).padStart(2, '0')}`;
      const displayUrl = tool.url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0];
      const card = document.createElement('a');
      card.className = 'kennel-card';
      card.href = tool.url;
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
      card.title = tool.name;
      card.style.animationDelay = `${i * 0.05}s`;
      card.innerHTML = `
        <div class="card-rail"><span class="card-rail-tag">${tag}</span></div>
        <div class="card-body">
          <div class="card-name">${tool.name}</div>
          <div class="card-url">${displayUrl}</div>
          <div class="card-divider"></div>
          <div class="card-desc">${tool.desc || ''}</div>
          <div class="card-cta">Open &rarr;</div>
        </div>`;
      grid.insertBefore(card, emptyMsg);
    });
  }

  function filterTools(q) {
    if (!q) return tools;
    const lq = q.toLowerCase();
    return tools.filter(t =>
      t.name.toLowerCase().includes(lq) ||
      (t.desc || '').toLowerCase().includes(lq) ||
      t.url.toLowerCase().includes(lq)
    );
  }

  search.addEventListener('input', () => buildCards(filterTools(search.value.trim())));
  buildCards(tools);

  const playerSection = document.getElementById('player-section');
  if (!showPlayer) {
    playerSection.style.display = 'none';
  } else {
    document.getElementById('player-stream-name').textContent = streamName;
    const btn       = document.getElementById('player-btn');
    const iconPlay  = document.getElementById('icon-play');
    const iconStop  = document.getElementById('icon-stop');
    const liveDot   = document.getElementById('live-dot');
    const liveLabel = document.getElementById('live-label');
    const timerEl   = document.getElementById('player-timer');
    const volSlider = document.getElementById('volume-slider');
    let audio = null, playing = false, startTime = null, timerTick = null;
    function formatTime(secs) {
      const h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60), s = Math.floor(secs % 60);
      return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
    }
    function startTimer() { startTime = Date.now(); timerTick = setInterval(() => { timerEl.textContent = formatTime((Date.now() - startTime) / 1000); }, 1000); }
    function stopTimer() { clearInterval(timerTick); timerEl.textContent = '0:00:00'; }
    function setPlaying(state) {
      playing = state;
      iconPlay.style.display = state ? 'none' : '';
      iconStop.style.display = state ? '' : 'none';
      liveDot.classList.toggle('active', state);
      liveLabel.classList.toggle('active', state);
      btn.title = state ? 'Stop stream' : 'Play stream';
    }
    btn.addEventListener('click', () => {
      if (!playing) {
        if (audio) { audio.src = ''; audio = null; }
        audio = new Audio(streamUrl);
        audio.volume = parseFloat(volSlider.value);
        audio.play().catch(() => {});
        setPlaying(true); startTimer();
        audio.addEventListener('error', () => { setPlaying(false); stopTimer(); }, { once: true });
      } else {
        audio.pause(); audio.src = ''; audio = null;
        setPlaying(false); stopTimer();
      }
    });
    volSlider.addEventListener('input', () => { if (audio) audio.volume = parseFloat(volSlider.value); });
  }
</script>
</body>
</html>"""


def build_html() -> str:
    """Inject Python config values into the HTML template."""
    html = HTML_TEMPLATE
    html = html.replace("__STREAM_URL__",  json.dumps(STREAM_URL))
    html = html.replace("__STREAM_NAME__", json.dumps(STREAM_NAME))
    html = html.replace("__SHOW_PLAYER__", "true" if SHOW_PLAYER else "false")
    html = html.replace("__TOOLS__",       json.dumps(TOOLS, ensure_ascii=False))
    return html


class KennelHandler(http.server.BaseHTTPRequestHandler):
    _page = None  # built once at startup

    def do_GET(self):
        body = KennelHandler._page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} — {fmt % args}")


if __name__ == "__main__":
    KennelHandler._page = build_html()

    with socketserver.TCPServer((HOST, PORT), KennelHandler) as httpd:
        httpd.allow_reuse_address = True
        addr = f"http://localhost" + (f":{PORT}" if PORT != 80 else "")
        print(f"The Kennel is running at {addr}")
        print("Press Ctrl-C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")

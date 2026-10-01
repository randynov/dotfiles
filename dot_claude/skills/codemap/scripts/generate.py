#!/usr/bin/env python3
"""Generate codemap.json, codemap.html and codemap.lock from the current repo.

All three outputs come from one in-memory model, so they cannot drift apart:
the HTML embeds the same JSON document it renders. Run from anywhere inside the
repo you are mapping:

    python3 generate.py                      # generate + validate
    python3 generate.py --validate           # validate what is already on disk
    python3 generate.py --out docs/codemap --model docs/codemap/model.py

The repo-specific part is `model.py` (nodes, edges, flows, module scopes); this
file is the same everywhere. Editing any output by hand defeats the fingerprint
check in codemap.lock — regenerate instead.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

FINGERPRINT_ALGORITHM = (
    "sha256 over this algorithm string followed by newline-joined "
    "'<tracked path>:<sha256 of file bytes>' entries, paths sorted ascending, "
    "module scope = tracked files minus EXCLUDED_DIRS, then include prefixes "
    "minus exclude prefixes"
)

# Populated by configure() before anything else runs. They are module globals rather
# than arguments threaded through twenty functions because every one of them is a
# read-only constant for the life of a run.
REPO = ""
OUT_DIR = ""
JSON_PATH = HTML_PATH = LOCK_PATH = ""
DIRTY_EXCLUDE_PREFIX = ""
MODULES: dict = {}
NODES: list = []
EDGES: list = []
FLOWS: list = []
SCOPE: list = []
EXCLUDED_DIRS: list = []
_EXCLUDED_RE: "re.Pattern | None" = None


def configure(out_dir: str, model_path: str) -> None:
    """Resolve the repo root, load the repo's model.py, and fix the output paths."""
    global REPO, OUT_DIR, JSON_PATH, HTML_PATH, LOCK_PATH, DIRTY_EXCLUDE_PREFIX
    global MODULES, NODES, EDGES, FLOWS, SCOPE, EXCLUDED_DIRS, _EXCLUDED_RE

    REPO = subprocess.run(  # noqa: S603 - fixed executable, literal argv
        [GIT, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    OUT_DIR = os.path.abspath(out_dir)
    JSON_PATH = os.path.join(OUT_DIR, "codemap.json")
    HTML_PATH = os.path.join(OUT_DIR, "codemap.html")
    LOCK_PATH = os.path.join(OUT_DIR, "codemap.lock")

    # The lock lives inside the tree it measures, so a self-referential dirty flag
    # would always read true. Changes under the output directory are excluded.
    rel = os.path.relpath(OUT_DIR, REPO).replace(os.sep, "/")
    DIRTY_EXCLUDE_PREFIX = f"{rel}/"

    spec = importlib.util.spec_from_file_location("codemap_model", model_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load model from {model_path}")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)

    MODULES = model.MODULES
    NODES = model.NODES
    EDGES = model.EDGES
    FLOWS = model.FLOWS
    SCOPE = model.SCOPE
    EXCLUDED_DIRS = model.EXCLUDED_DIRS
    _EXCLUDED_RE = _compile_exclusions(EXCLUDED_DIRS)

EDGE_TYPES = ("imports", "calls", "reads", "writes", "publishes", "subscribes")

ROLE_COLORS = {
    "client": "#5eb0ef",
    "api": "#7ee2b8",
    "service": "#c9a0ff",
    "queue": "#ffc95e",
    "datastore": "#ff8fa3",
    "external": "#8c9bb5",
}

TIERS = {
    "client": 0,
    "api": 1,
    "service": 2,
    "queue": 2,
    "datastore": 3,
    "external": 3,
}


GIT = shutil.which("git") or "/usr/bin/git"


def git(*args: str) -> str:
    return subprocess.run(  # noqa: S603 - fixed executable, literal argv from this module
        [GIT, *args], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout


def tracked_files() -> list[str]:
    """Every tracked path the map is allowed to look at.

    Exclusions are applied once, here, because they describe the repo's scope rather
    than any one module's. Filtering further down meant fingerprints honoured the list
    while test discovery did not — the same concept enforced in one place and forgotten
    in the other.
    """
    return [
        line
        for line in git("ls-files", "-z").split("\0")
        if line and not globally_excluded(line)
    ]


def repo_name() -> str:
    """Canonical repository name.

    Prefer the origin remote: the clone directory is an accident of whoever ran
    `git clone`, so deriving from it makes the generated title differ between
    checkouts and the committed page fail validation for everyone else.

    Falling back to the directory keeps this working with no remote, and the common
    git dir is used rather than the cwd because a worktree directory is named after
    its branch.
    """
    try:
        url = git("remote", "get-url", "origin").strip()
        if url:
            slug = url.rstrip("/").rsplit("/", 1)[-1]
            if slug.endswith(".git"):
                slug = slug[: -len(".git")]
            if slug:
                return slug
    except subprocess.CalledProcessError:
        # No usable `origin` (or remote lookup failed); fall back to git-common-dir name.
        pass
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    return os.path.basename(os.path.dirname(common))


def read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def working_tree_dirty() -> bool:
    """Dirty state of everything the map describes, ignoring the map's own output.

    Cached because generating asks once to record it and the validator asks again to
    check it, and `git status` over this tree costs ~50ms a call.
    """
    # Let git apply the exclusion via pathspec. Hand-parsing porcelain to strip a
        # path prefix mis-reads renames ("R  old -> new") and quoted paths, and when the
        # output directory sits outside the repo there is nothing to exclude — which
        # this form states instead of faking with a ../../.. prefix that matches nothing.
    args = ["status", "--porcelain"]
    if DIRTY_EXCLUDE_PREFIX and not DIRTY_EXCLUDE_PREFIX.startswith(".."):
        args += ["--", ".", f":(exclude){DIRTY_EXCLUDE_PREFIX}"]
    return bool(git(*args).strip())


def globally_excluded(path: str) -> bool:
    """Match EXCLUDED_DIRS, which may contain glob segments like `server/*/migrations`."""
    return bool(_EXCLUDED_RE and _EXCLUDED_RE.match(path))


def _compile_exclusions(patterns: list[str]) -> "re.Pattern | None":
    """One compiled alternation for the whole exclusion list.

    Calling fnmatch per (path, pattern) re-normalises and re-looks-up the pattern every
    time — ~79k calls over this repo, which measured at 862ms. Compiling once is ~15ms.
    fnmatch's `*` crosses `/`, so `infra/*` already covers every depth below it.
    """
    if not patterns:
        return None
    return re.compile(
        "|".join(f"(?:{fnmatch.translate(f'{p}/*')})|(?:{fnmatch.translate(p)})" for p in patterns)
    )


def in_module(path: str, spec: dict) -> bool:
    """Module membership only. Repo-wide exclusions are already gone by this point."""
    if not any(path.startswith(i) for i in spec["include"]):
        return False
    return not any(path.startswith(x) for x in spec.get("exclude", []))


def file_sha(path: str) -> str:
    with open(os.path.join(REPO, path), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def fingerprints(files: list[str]) -> dict:
    """Per-module content fingerprints. Pure — call it once and pass the result around.

    Hashing every in-scope file costs ~775ms here, so `main` computes this once and
    hands it to both the lock builder and the validator rather than each recomputing.
    """
    out = {}
    for module_id, spec in MODULES.items():
        paths = sorted(p for p in files if in_module(p, spec))
        # The algorithm string is hashed in so that changing what "scope" means
        # necessarily changes every fingerprint, and the existing stale-fingerprint
        # check catches it. Comparing the lock's copy of the string to the constant
        # that wrote it passes tautologically and catches nothing.
        body = "\n".join(f"{p}:{file_sha(p)}" for p in paths)
        digest = hashlib.sha256(f"{FINGERPRINT_ALGORITHM}\n{body}".encode()).hexdigest()
        out[module_id] = {
            "include": spec["include"],
            "exclude": spec.get("exclude", []),
            "file_count": len(paths),
            "fingerprint": digest,
        }
    return out


def tests_for(module_id: str, files: list[str]) -> list[str]:
    """Test files for a module.

    Frontend suites live outside `src/`, and the surveys service tests share a
    directory with the rest of the surveys app, so discovery uses its own
    `tests` prefixes and an optional name filter rather than the fingerprint scope.
    """
    spec = MODULES.get(module_id)
    if not spec:
        return []
    prefixes = spec.get("tests") or spec["include"]
    match = spec.get("tests_match")
    hits = []
    for p in files:
        base = os.path.basename(p)
        if not any(p.startswith(x) for x in prefixes):
            continue
        # pytest (test_x.py), JS/TS (x.test.ts, x.spec.ts), Go (x_test.go), JVM, Ruby.
        # Worth keeping all of them even in a single-language repo: the same script runs
        # everywhere, and a missing suffix reads as "this module is untested".
        is_test = (
            base.startswith("test_")
            or ".test." in base
            or ".spec." in base
            or base.endswith("_test.go")
            or base.endswith("Test.java")
            or base.endswith("_spec.rb")
        )
        if not is_test:
            continue
        if match and not any(m in base for m in match):
            continue
        hits.append(p)
    return sorted(hits)[:12]


# --- layout -------------------------------------------------------------------
# Tiers are fixed by role; order inside a tier is refined by barycenter sweeps so
# edges run mostly straight down and crossings stay low. Positions are baked into
# the JSON, so the browser never runs a force simulation.

# NODE_W / NODE_H mirror the NW / NH constants the page script draws with.
WIDTH, TIER_GAP, TOP, NODE_W = 1680.0, 210.0, 90.0, 178.0


def layout(nodes: list[dict], edges: list[dict]) -> None:
    """Pick the lowest-crossing arrangement over a fixed set of deterministic seeds."""
    best: tuple[int, dict] | None = None
    for seed in range(40):
        _layout_once(nodes, edges, seed)
        score = crossings(nodes, edges)
        if best is None or score < best[0]:
            best = (score, {n["id"]: (n["x"], n["y"], n["tier"]) for n in nodes})
    for n in nodes:
        n["x"], n["y"], n["tier"] = best[1][n["id"]]  # type: ignore[index]


def _layout_once(nodes: list[dict], edges: list[dict], seed: int) -> None:
    rng = random.Random(seed)  # noqa: S311 - layout shuffling, not security
    by_tier: dict[int, list[str]] = {}
    tier_of = {n["id"]: TIERS[n["role"]] for n in nodes}
    for n in nodes:
        by_tier.setdefault(tier_of[n["id"]], []).append(n["id"])

    order = {}
    for t, ids in by_tier.items():
        shuffled = list(ids)
        rng.shuffle(shuffled)
        order[t] = shuffled
    neighbors: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    for e in edges:
        neighbors[e["from"]].append(e["to"])
        neighbors[e["to"]].append(e["from"])

    def pos(t: int) -> dict[str, int]:
        return {nid: i for i, nid in enumerate(order[t])}

    for _ in range(24):
        for t in sorted(order):
            others = {k: pos(k) for k in order if k != t}
            flat = {nid: idx for m in others.values() for nid, idx in m.items()}
            current = pos(t)

            def bary(nid: str) -> float:
                vals = [flat[o] for o in neighbors[nid] if o in flat]
                return sum(vals) / len(vals) if vals else float(current[nid])

            order[t] = sorted(order[t], key=lambda nid: (bary(nid), current[nid]))

    coords = {}
    for t in sorted(order):
        ids = order[t]
        # Never let a dense tier pack boxes closer than their own width.
        step = max(WIDTH / (len(ids) + 1), NODE_W + 26)
        span = step * (len(ids) - 1)
        left = WIDTH / 2 - span / 2
        for i, nid in enumerate(ids):
            coords[nid] = (round(left + step * i, 1), round(TOP + t * TIER_GAP, 1))

    for n in nodes:
        n["tier"] = tier_of[n["id"]]
        n["x"], n["y"] = coords[n["id"]]


def crossings(nodes: list[dict], edges: list[dict]) -> int:
    pt = {n["id"]: (n["x"], n["y"]) for n in nodes}
    segs = [(pt[e["from"]], pt[e["to"]]) for e in edges]

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    total = 0
    for i in range(len(segs)):
        a, b = segs[i]
        for j in range(i + 1, len(segs)):
            c, d = segs[j]
            if len({a, b, c, d}) < 4:
                continue
            if ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d):
                total += 1
    return total


# --- build --------------------------------------------------------------------


def build_document(files: list[str], commit: str, generated_at: str) -> dict:
    nodes = []
    for src in NODES:
        n = dict(src)
        n["tests"] = tests_for(str(n["id"]), files)
        nodes.append(n)
    edges = [dict(e) for e in EDGES]
    layout(nodes, edges)
    flows = [dict(f) for f in FLOWS]
    return {
        "generated_at": generated_at,
        "generated_from_commit": commit,
        "scope": SCOPE,
        "nodes": nodes,
        "edges": edges,
        "flows": flows,
    }


def build_lock(commit: str, generated_at: str, fps: dict, dirty: bool) -> dict:
    return {
        "commit": commit,
        "branch": git("rev-parse", "--abbrev-ref", "HEAD").strip(),
        "dirty": dirty,
        "dirty_excludes": [DIRTY_EXCLUDE_PREFIX],
        "generated_at": generated_at,
        "scope": SCOPE,
        "excluded_dirs": EXCLUDED_DIRS,
        "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "modules": fps,
    }


# --- html ---------------------------------------------------------------------


def render_html(doc: dict, repo_name: str) -> str:
    payload = json.dumps(doc, indent=2, ensure_ascii=False)
    legend = "".join(
        f'<span class="chip"><i style="background:{c}"></i>{r}</span>'
        for r, c in ROLE_COLORS.items()
    )
    colors = json.dumps(ROLE_COLORS)
    short = doc["generated_from_commit"][:12]
    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{repo_name} code map</title>
<style>
:root {{
  --bg:#0d1117; --panel:#161b22; --line:#2b3440; --fg:#e6edf3; --muted:#8b98a9;
  --accent:#5eb0ef; --dim:#3a4553;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; height:100%; background:var(--bg); color:var(--fg);
  font:14px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif; }}
header {{ padding:10px 16px; border-bottom:1px solid var(--line); background:var(--panel);
  display:flex; flex-wrap:wrap; gap:12px 20px; align-items:baseline; }}
header h1 {{ font-size:16px; margin:0; letter-spacing:.2px; }}
header .meta {{ color:var(--muted); font-size:12px; font-family:ui-monospace,monospace; }}
.bar {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center;
  padding:8px 16px; border-bottom:1px solid var(--line); background:var(--panel); }}
input,select {{ background:var(--bg); color:var(--fg); border:1px solid var(--line);
  border-radius:6px; padding:5px 8px; font:inherit; font-size:13px; }}
input:focus,select:focus {{ outline:2px solid var(--accent); outline-offset:1px; }}
button {{ background:var(--bg); color:var(--fg); border:1px solid var(--line);
  border-radius:6px; padding:5px 10px; font:inherit; font-size:13px; cursor:pointer; }}
button:hover {{ border-color:var(--accent); }}
.chip {{ display:inline-flex; align-items:center; gap:5px; font-size:12px; color:var(--muted);
  cursor:pointer; user-select:none; padding:2px 6px; border-radius:6px; border:1px solid transparent; }}
.chip.off {{ opacity:.35; }}
.chip:hover {{ border-color:var(--line); }}
.chip i {{ width:10px; height:10px; border-radius:3px; display:inline-block; }}
main {{ display:flex; height:calc(100vh - 104px); }}
#stage {{ flex:1; min-width:0; position:relative; }}
svg {{ width:100%; height:100%; display:block; cursor:grab; touch-action:none; }}
svg.grabbing {{ cursor:grabbing; }}
aside {{ width:340px; flex:none; border-left:1px solid var(--line); background:var(--panel);
  overflow:auto; padding:14px 16px; }}
aside h2 {{ font-size:14px; margin:0 0 4px; }}
aside h3 {{ font-size:11px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--muted); margin:16px 0 6px; }}
aside p {{ margin:0 0 6px; color:var(--fg); }}
aside .path {{ font-family:ui-monospace,monospace; font-size:12px; color:var(--accent);
  word-break:break-all; }}
aside ul {{ margin:0; padding-left:18px; }}
aside li {{ margin-bottom:4px; font-size:13px; }}
aside code {{ font-family:ui-monospace,monospace; font-size:12px; color:var(--muted);
  word-break:break-all; }}
.unknown {{ color:#ffc95e; }}
.node rect {{ stroke-width:1.5px; }}
.node text {{ pointer-events:none; }}
.node .label {{ font-size:12.5px; font-weight:600; fill:#0d1117; }}
.node .sub {{ font-size:10.5px; fill:#0d1117; opacity:.72; }}
.node.dim {{ opacity:.14; }}
.node.sel rect {{ stroke:#fff; stroke-width:3px; }}
.edge {{ fill:none; stroke:var(--dim); stroke-width:1.4px; }}
.edge.dim {{ opacity:.06; }}
.edge.up {{ stroke:#ff8fa3; stroke-width:2.4px; }}
.edge.down {{ stroke:#7ee2b8; stroke-width:2.4px; }}
.edge.flow {{ stroke:#ffc95e; stroke-width:3px; }}
.edge.hop {{ stroke-dasharray:7 6; opacity:.75; }}
.edge.unknown {{ stroke-dasharray:5 4; }}
.hint {{ color:var(--muted); font-size:11.5px; }}
.tierlabel {{ fill:var(--muted); font-size:11px; letter-spacing:.09em; text-transform:uppercase; }}
@media (max-width:900px) {{ main {{ flex-direction:column; }} aside {{ width:auto; height:42%; border-left:0; border-top:1px solid var(--line); }} }}
</style>
</head>
<body>
<header>
  <h1>{repo_name} &middot; code map</h1>
  <span class="meta">commit {short}</span>
  <span class="meta">generated {doc["generated_at"]}</span>
  <span class="meta">{len(doc["nodes"])} nodes &middot; {len(doc["edges"])} edges &middot; {len(doc["flows"])} flows</span>
</header>
<div class="bar">
  <input id="q" type="search" placeholder="Search nodes, paths, symbols&hellip;" size="30">
  <select id="flow"><option value="">All flows</option></select>
  <span id="legend">{legend}</span>
  <button id="zin">+</button><button id="zout">&minus;</button><button id="reset">Reset</button>
  <span class="hint">In a selected flow, a dashed gold link is an ordering step with no single code edge behind it.</span>
</div>
<main>
  <div id="stage"><svg id="svg"><g id="root"></g></svg></div>
  <aside id="panel"></aside>
</main>

<script type="application/json" id="codemap">
{payload}
</script>
<script>
const DATA = JSON.parse(document.getElementById('codemap').textContent);
const COLORS = {colors};
const TIER_NAMES = ['clients', 'api apps', 'services & queue', 'data & external'];
const NW = 178, NH = 52;
const svg = document.getElementById('svg'), root = document.getElementById('root');
const panel = document.getElementById('panel');
const byId = Object.fromEntries(DATA.nodes.map(n => [n.id, n]));
const hidden = new Set();
let selected = null, activeFlow = '';

const ns = 'http://www.w3.org/2000/svg';
const el = (t, a) => {{ const e = document.createElementNS(ns, t);
  for (const k in a) e.setAttribute(k, a[k]); return e; }};

// tier bands
DATA.nodes.forEach(n => {{ n.cx = n.x; n.cy = n.y; }});
TIER_NAMES.forEach((name, t) => {{
  const rows = DATA.nodes.filter(n => n.tier === t);
  if (!rows.length) return;
  const y = Math.min(...rows.map(n => n.cy)) - NH / 2 - 22;
  const x = Math.min(...DATA.nodes.map(n => n.cx)) - NW / 2;
  const lbl = el('text', {{ x: x, y: y, class: 'tierlabel' }});
  lbl.textContent = name; root.appendChild(lbl);
}});

const edgeEls = DATA.edges.map((e, i) => {{
  const p = el('path', {{ class: 'edge' + (e.evidence === 'unknown' ? ' unknown' : '') }});
  p.dataset.i = i; root.appendChild(p); return p;
}});

const nodeEls = DATA.nodes.map(n => {{
  const g = el('g', {{ class: 'node' }});
  g.dataset.id = n.id;
  const r = el('rect', {{ x: -NW / 2, y: -NH / 2, width: NW, height: NH, rx: 9,
    fill: COLORS[n.role], stroke: COLORS[n.role] }});
  const t1 = el('text', {{ class: 'label', 'text-anchor': 'middle', y: -4 }});
  t1.textContent = n.title.length > 26 ? n.title.slice(0, 25) + '\\u2026' : n.title;
  const t2 = el('text', {{ class: 'sub', 'text-anchor': 'middle', y: 13 }});
  t2.textContent = n.id;
  g.append(r, t1, t2); root.appendChild(g); return g;
}});

function place() {{
  DATA.nodes.forEach((n, i) => {{
    nodeEls[i].setAttribute('transform', `translate(${{n.cx}},${{n.cy}})`);
    nodeEls[i].style.display = hidden.has(n.role) ? 'none' : '';
  }});
  DATA.edges.forEach((e, i) => {{
    const a = byId[e.from], b = byId[e.to];
    const mx = (a.cx + b.cx) / 2, my = (a.cy + b.cy) / 2 + (a.cy === b.cy ? -54 : 0);
    edgeEls[i].setAttribute('d', `M${{a.cx}},${{a.cy}} Q${{mx}},${{my}} ${{b.cx}},${{b.cy}}`);
    edgeEls[i].style.display =
      (hidden.has(a.role) || hidden.has(b.role)) ? 'none' : '';
  }});
  if (activeHops.length) drawHops(activeHops);
}}

// A flow hop is an ordering of steps, not necessarily a single code edge. Hops that
// match a graph edge light that edge; hops that do not get a dashed connector, so the
// path reads end to end without the map claiming an edge the source does not have.
function flowEdgeSet(flow) {{
  const s = new Set(), hops = [];
  for (let i = 0; i < flow.steps.length - 1; i++) {{
    const a = flow.steps[i].node, b = flow.steps[i + 1].node;
    if (a === b) continue;
    let found = false;
    DATA.edges.forEach((e, idx) => {{
      if ((e.from === a && e.to === b) || (e.from === b && e.to === a)) {{
        s.add(idx); found = true;
      }}
    }});
    if (!found) hops.push([a, b]);
  }}
  return {{ edges: s, hops }};
}}

const hopLayer = el('g', {{}});
root.appendChild(hopLayer);
// Remembered so place() can redraw them after a drag; otherwise the dashed
// connectors keep pointing at where a node used to be.
let activeHops = [];

function drawHops(hops) {{
  activeHops = hops;
  hopLayer.textContent = '';
  hops.forEach(([a, b]) => {{
    const p = byId[a], q = byId[b];
    const mx = (p.cx + q.cx) / 2, my = (p.cy + q.cy) / 2 + (p.cy === q.cy ? -54 : 0);
    const path = el('path', {{ class: 'edge flow hop',
      d: `M${{p.cx}},${{p.cy}} Q${{mx}},${{my}} ${{q.cx}},${{q.cy}}` }});
    hopLayer.appendChild(path);
  }});
}}

function paint() {{
  const q = document.getElementById('q').value.trim().toLowerCase();
  const flow = DATA.flows.find(f => f.id === activeFlow);
  const flowNodes = flow ? new Set(flow.steps.map(s => s.node)) : null;
  const path = flow ? flowEdgeSet(flow) : null;
  const flowEdges = path ? path.edges : null;
  drawHops(path ? path.hops : []);
  const up = new Set(), down = new Set();
  if (selected) DATA.edges.forEach((e, i) => {{
    if (e.to === selected) up.add(i);
    if (e.from === selected) down.add(i);
  }});
  const related = new Set(selected ? [selected] : []);
  DATA.edges.forEach((e, i) => {{ if (up.has(i)) related.add(e.from);
    if (down.has(i)) related.add(e.to); }});

  DATA.nodes.forEach((n, i) => {{
    let dim = false;
    if (q) {{
      const hay = [n.id, n.title, n.path, n.summary, n.role,
        ...(n.entrypoints || []).map(x => x.path + ' ' + x.symbol),
        ...(n.tests || [])].join(' ').toLowerCase();
      dim = !hay.includes(q);
    }}
    if (flowNodes && !flowNodes.has(n.id)) dim = true;
    if (selected && !related.has(n.id)) dim = true;
    nodeEls[i].classList.toggle('dim', dim);
    nodeEls[i].classList.toggle('sel', n.id === selected);
  }});

  // A search keeps the edges whose BOTH ends matched, so a hit reads as a subgraph
  // rather than a scatter of disconnected boxes.
  const lit = new Set(DATA.nodes.filter((n, i) =>
    !nodeEls[i].classList.contains('dim')).map(n => n.id));
  DATA.edges.forEach((e, i) => {{
    const c = edgeEls[i].classList;
    c.remove('up', 'down', 'flow', 'dim');
    const joinsLit = lit.has(e.from) && lit.has(e.to);
    if (flowEdges && flowEdges.has(i)) c.add('flow');
    else if (up.has(i)) c.add('up');
    else if (down.has(i)) c.add('down');
    else if (q && !selected && !flowNodes && joinsLit) c.add('up');
    else if (selected || flowNodes || q) c.add('dim');
  }});
}}

const esc = s => String(s).replace(/[&<>]/g, c => ({{ '&': '&amp;', '<': '&lt;', '>': '&gt;' }}[c]));
const ev = e => e.evidence === 'unknown'
  ? `<span class="unknown">unknown</span>${{e.note ? ' &mdash; ' + esc(e.note) : ''}}`
  : `<code>${{esc(e.evidence.path)}}</code> &middot; <code>${{esc(e.evidence.symbol)}}</code>`;

function showNode(id) {{
  const n = byId[id];
  const up = DATA.edges.filter(e => e.to === id);
  const down = DATA.edges.filter(e => e.from === id);
  const flows = DATA.flows.filter(f => f.steps.some(s => s.node === id));
  panel.innerHTML = `
    <h2>${{esc(n.title)}}</h2>
    <p class="path">${{esc(n.path)}}</p>
    <p>${{esc(n.summary)}}</p>
    <h3>evidence</h3><p><code>${{esc(n.evidence.path)}}</code> &middot; <code>${{esc(n.evidence.symbol)}}</code></p>
    <h3>entrypoints</h3><ul>${{n.entrypoints.map(e =>
      `<li><code>${{esc(e.path)}}</code> &middot; <code>${{esc(e.symbol)}}</code></li>`).join('') || '<li>none</li>'}}</ul>
    <h3>upstream callers (${{up.length}})</h3><ul>${{up.map(e =>
      `<li><b>${{esc(e.from)}}</b> <i>${{esc(e.type)}}</i><br>${{ev(e)}}</li>`).join('') || '<li>none</li>'}}</ul>
    <h3>downstream dependencies (${{down.length}})</h3><ul>${{down.map(e =>
      `<li><b>${{esc(e.to)}}</b> <i>${{esc(e.type)}}</i><br>${{ev(e)}}</li>`).join('') || '<li>none</li>'}}</ul>
    <h3>tests (${{n.tests.length}})</h3><ul>${{n.tests.map(t =>
      `<li><code>${{esc(t)}}</code></li>`).join('') || '<li>none found in scope</li>'}}</ul>
    <h3>flows</h3><ul>${{flows.map(f =>
      `<li>${{esc(f.name)}}</li>`).join('') || '<li>none</li>'}}</ul>
    <h3>constraints</h3><ul>${{n.constraints.map(c => `<li>${{esc(c)}}</li>`).join('')}}</ul>`;
}}

function showFlow(f) {{
  panel.innerHTML = `
    <h2>${{esc(f.name)}}</h2>
    <h3>trigger</h3><p>${{esc(f.trigger)}}</p>
    <h3>steps</h3><ol>${{f.steps.map(s =>
      `<li><b>${{esc(s.node)}}</b><br>${{esc(s.detail)}}</li>`).join('')}}</ol>
    <h3>outcome</h3><p>${{esc(f.outcome)}}</p>`;
}}

function showOverview() {{
  const unknown = DATA.edges.filter(e => e.evidence === 'unknown');
  panel.innerHTML = `
    <h2>Overview</h2>
    <p>Click any module to highlight its upstream callers, downstream dependencies,
       tests and flows. Pick a flow to trace a full path. Drag a module to reposition it;
       drag the background to pan, scroll to zoom.</p>
    <h3>scope</h3><ul>${{DATA.scope.map(s => `<li><code>${{esc(s)}}</code></li>`).join('')}}</ul>
    <h3>flows</h3><ol>${{DATA.flows.map(f => `<li>${{esc(f.name)}}</li>`).join('')}}</ol>
    <h3>unmapped relationships (${{unknown.length}})</h3>
    <ul>${{unknown.map(e =>
      `<li><b>${{esc(e.from)}} &rarr; ${{esc(e.to)}}</b><br>${{ev(e)}}</li>`).join('') || '<li>none</li>'}}</ul>`;
}}

nodeEls.forEach((g, i) => {{
  g.addEventListener('click', ev2 => {{
    ev2.stopPropagation();
    if (dragMoved) return;
    const id = DATA.nodes[i].id;
    selected = selected === id ? null : id;
    selected ? showNode(selected) : showOverview();
    paint();
  }});
}});

// pan / zoom / drag
let view = {{ x: 0, y: 0, k: 1 }}, panning = null, dragging = null, dragMoved = false;
const apply = () => root.setAttribute('transform',
  `translate(${{view.x}},${{view.y}}) scale(${{view.k}})`);

svg.addEventListener('pointerdown', e => {{
  const g = e.target.closest('.node');
  dragMoved = false;
  if (g) {{
    dragging = {{ node: byId[g.dataset.id], x: e.clientX, y: e.clientY }};
  }} else {{
    // Record the press origin so a pan can be told from a click. Without it the
    // click that ends a pan lands on the <svg> and clears the current selection,
    // which is exactly what someone panning to see a node's neighbours does not want.
    panning = {{ x: e.clientX - view.x, y: e.clientY - view.y, sx: e.clientX, sy: e.clientY }};
    svg.classList.add('grabbing');
  }}
  // Capture on the node when the press landed on one. Capturing on <svg> instead
  // retargets the following pointerup and click to the <svg>, so the per-node click
  // listener never fires and selection silently dies. Synthetic dispatchEvent tests
  // cannot catch this — pointer capture only engages for real input.
  // Capture can also throw if the pointer was already released; the drag still works
  // without it, so never let that abort the handler.
  try {{ (g || svg).setPointerCapture(e.pointerId); }} catch {{ /* no active pointer */ }}
}});
svg.addEventListener('pointermove', e => {{
  if (dragging) {{
    const dx = (e.clientX - dragging.x) / view.k, dy = (e.clientY - dragging.y) / view.k;
    if (Math.abs(dx) + Math.abs(dy) > 1) dragMoved = true;
    dragging.node.cx += dx; dragging.node.cy += dy;
    dragging.x = e.clientX; dragging.y = e.clientY;
    place();
  }} else if (panning) {{
    if (Math.abs(e.clientX - panning.sx) + Math.abs(e.clientY - panning.sy) > 3) dragMoved = true;
    view.x = e.clientX - panning.x; view.y = e.clientY - panning.y; apply();
  }}
}});
svg.addEventListener('pointerup', e => {{
  dragging = null; panning = null; svg.classList.remove('grabbing');
  try {{ svg.releasePointerCapture(e.pointerId); }} catch {{ /* already released */ }}
}});
svg.addEventListener('wheel', e => {{
  e.preventDefault();
  const r = svg.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  const k = Math.min(3, Math.max(0.25, view.k * (e.deltaY < 0 ? 1.12 : 1 / 1.12)));
  view.x = mx - (mx - view.x) * (k / view.k);
  view.y = my - (my - view.y) * (k / view.k);
  view.k = k; apply();
}}, {{ passive: false }});

function fit() {{
  const r = svg.getBoundingClientRect();
  const xs = DATA.nodes.map(n => n.cx), ys = DATA.nodes.map(n => n.cy);
  const x0 = Math.min(...xs) - NW / 2 - 40, y0 = Math.min(...ys) - NH / 2 - 46;
  const w = Math.max(...xs) + NW / 2 + 40 - x0;
  const h = Math.max(...ys) + NH / 2 + 24 - y0;
  view.k = Math.min(r.width / w, r.height / h, 1.4);
  view.x = (r.width - w * view.k) / 2 - x0 * view.k;
  view.y = (r.height - h * view.k) / 2 - y0 * view.k;
  apply();
}}

document.getElementById('zin').onclick = () => {{ view.k = Math.min(3, view.k * 1.2); apply(); }};
document.getElementById('zout').onclick = () => {{ view.k = Math.max(0.25, view.k / 1.2); apply(); }};
document.getElementById('reset').onclick = () => {{
  DATA.nodes.forEach(n => {{ n.cx = n.x; n.cy = n.y; }});
  selected = null; activeFlow = ''; hidden.clear();
  document.getElementById('q').value = ''; document.getElementById('flow').value = '';
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('off'));
  place(); paint(); showOverview(); fit();
}};
document.getElementById('q').addEventListener('input', paint);

const sel = document.getElementById('flow');
DATA.flows.forEach(f => {{
  const o = document.createElement('option'); o.value = f.id; o.textContent = f.name;
  sel.appendChild(o);
}});
sel.addEventListener('change', () => {{
  activeFlow = sel.value;
  const f = DATA.flows.find(x => x.id === activeFlow);
  selected = null;
  f ? showFlow(f) : showOverview();
  paint();
}});

document.querySelectorAll('#legend .chip').forEach(chip => {{
  const role = chip.textContent.trim();
  chip.addEventListener('click', () => {{
    hidden.has(role) ? hidden.delete(role) : hidden.add(role);
    chip.classList.toggle('off', hidden.has(role));
    place(); paint();
  }});
}});

svg.addEventListener('click', e => {{
  if (e.target.closest('.node') || dragMoved) return;
  selected = null; showOverview(); paint();
}});

place(); paint(); showOverview();
window.addEventListener('resize', fit);
fit();
</script>
</body>
</html>
"""  # noqa: S608 - an HTML page template; the CSS `select` rules trip the SQL heuristic


# --- validation ---------------------------------------------------------------


def symbol_present(path: str, symbol: str) -> bool:
    full = os.path.join(REPO, path)
    if not os.path.isfile(full):
        return False
    with open(full, "r", encoding="utf-8", errors="replace") as fh:
        return symbol in fh.read()


def _check_nodes(doc: dict, files: list[str]) -> list[str]:
    fails: list[str] = []
    for n in doc["nodes"]:
        if not os.path.exists(os.path.join(REPO, n["path"])):
            fails.append(f"node {n['id']}: path missing: {n['path']}")
        for label, item in [("evidence", n["evidence"])] + [
            ("entrypoint", e) for e in n["entrypoints"]
        ]:
            if not symbol_present(item["path"], item["symbol"]):
                fails.append(
                    f"node {n['id']}: {label} symbol not found: "
                    f"{item['symbol']!r} in {item['path']}"
                )
        fails += [f"node {n['id']}: test not tracked: {t}" for t in n["tests"] if t not in files]
    if len(doc["nodes"]) > 20:
        fails.append(f"nodes: {len(doc['nodes'])} exceeds the 20-node budget")
    return fails


def _check_edges(doc: dict) -> list[str]:
    ids = {n["id"] for n in doc["nodes"]}
    fails: list[str] = []
    for e in doc["edges"]:
        tag = f"edge {e['from']}->{e['to']}"
        if e["from"] not in ids:
            fails.append(f"{tag}: unknown from-node")
        if e["to"] not in ids:
            fails.append(f"{tag}: unknown to-node")
        if e["type"] not in EDGE_TYPES:
            fails.append(f"{tag}: illegal type {e['type']!r}")
        if e["evidence"] == "unknown":
            if not e.get("note"):
                fails.append(f"{tag}: marked unknown without a note")
        elif not symbol_present(e["evidence"]["path"], e["evidence"]["symbol"]):
            fails.append(
                f"{tag}: evidence symbol not found: "
                f"{e['evidence']['symbol']!r} in {e['evidence']['path']}"
            )
    return fails


def _check_flows(doc: dict) -> list[str]:
    ids = {n["id"] for n in doc["nodes"]}
    fails: list[str] = []
    for f in doc["flows"]:
        fails += [
            f"flow {f['id']}: missing {k}"
            for k in ("trigger", "steps", "outcome")
            if not f.get(k)
        ]
        fails += [
            f"flow {f['id']}: step references unknown node {s['node']!r}"
            for s in f["steps"]
            if s["node"] not in ids
        ]
    return fails


def _check_html(doc: dict, html: str) -> list[str]:
    """The page must be exactly what this generator produces from codemap.json.

    One equality subsumes the field-by-field assertions this replaced (embedded
    nodes/edges/flows, title, commit) and is strictly stronger: it also catches a
    hand-edit to the CSS, the page script, the legend or the baked layout, none of
    which spot-checking individual fields could see.
    """
    if html == render_html(doc, repo_name()):
        return []
    # Narrow the report to something actionable rather than just "bytes differ".
    m = re.search(
        r'<script type="application/json" id="codemap">\s*(.*?)\s*</script>', html, re.S
    )
    if not m:
        return ["html: embedded codemap JSON block not found"]
    try:
        embedded = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        return [f"html: embedded JSON block is not parseable: {exc}"]
    fails = [
        f"html: embedded {key} differ from codemap.json"
        for key in ("nodes", "edges", "flows")
        if embedded.get(key) != doc[key]
    ]
    return fails or ["html: page differs from a fresh render of codemap.json"]


def _check_lock(lock: dict, fps: dict, dirty: bool) -> list[str]:
    fails: list[str] = []
    head = git("rev-parse", "HEAD").strip()
    # Provenance, not a gate. The lock names the commit the map was generated FROM, and
    # that commit legitimately stops being reachable: a squash or rebase merge rewrites
    # it, and a shallow clone (actions/checkout defaults to depth 1) never fetches it.
    # Likewise `dirty` describes the whole tree, so one unrelated edit would fail an
    # otherwise accurate map. The per-module fingerprints below are the real drift check.
    if lock["commit"] != head:
        try:
            git("merge-base", "--is-ancestor", lock["commit"], head)
        except subprocess.CalledProcessError:
            print(
                f"warning: lock commit {lock['commit'][:12]} is not reachable from HEAD "
                f"{head[:12]} (squash merge, rebase, or shallow clone)",
                file=sys.stderr,
            )
    if lock["dirty"] != dirty:
        print(
            "warning: working tree dirty state differs from the lock; "
            "fingerprints below are authoritative",
            file=sys.stderr,
        )
    if lock["fingerprint_algorithm"] != FINGERPRINT_ALGORITHM:
        fails.append("lock: fingerprint_algorithm string drifted")
    current = fps
    for mid, rec in current.items():
        if mid not in lock["modules"]:
            fails.append(f"lock: module {mid} missing")
        elif lock["modules"][mid]["fingerprint"] != rec["fingerprint"]:
            fails.append(f"lock: stale fingerprint for module {mid}")
    fails += [
        f"lock: module {mid} no longer in scope" for mid in lock["modules"] if mid not in current
    ]
    return fails


def validate(
    doc: dict, lock: dict, html: str, files: list[str], fps: dict, dirty: bool
) -> list[tuple[str, list[str]]]:
    """Run every checker, returning (name, failures) per checker.

    The report is built from these pairs rather than by matching substrings of the
    failure text: a checker that gets a reworded message would otherwise report PASS
    forever, which is the one way a validator can lie without anyone noticing.
    """
    return [
        ("nodes: paths, evidence symbols, tests, budget", _check_nodes(doc, files)),
        ("edges: endpoints, type enum, unknown convention", _check_edges(doc)),
        ("flows: required fields, steps resolve to nodes", _check_flows(doc)),
        ("html: header, self-contained, agrees with json", _check_html(doc, html)),
        ("lock: fingerprints match the working tree", _check_lock(lock, fps, dirty)),
    ]


def compare_lock(old: dict, new: dict) -> dict:
    o, n = old.get("modules", {}), new["modules"]
    return {
        "changed": sorted(k for k in n if k in o and o[k]["fingerprint"] != n[k]["fingerprint"]),
        "added": sorted(k for k in n if k not in o),
        "removed": sorted(k for k in o if k not in n),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate", action="store_true", help="validate on-disk files only")
    ap.add_argument(
        "--out",
        default=None,
        help="directory for codemap.json/.html/.lock (default: this script's directory)",
    )
    ap.add_argument(
        "--model",
        default=None,
        help="path to the repo's model.py (default: <out>/model.py)",
    )
    args = ap.parse_args()
    # Defaulting to the script's own directory rather than a CWD-relative path keeps
    # "run it from anywhere inside the repo" true. A relative default would resolve
    # against the caller's CWD and look for docs/codemap/docs/codemap/model.py.
    out = args.out or os.path.dirname(os.path.abspath(__file__))
    configure(out, args.model or os.path.join(out, "model.py"))

    files = tracked_files()
    commit = git("rev-parse", "HEAD").strip()
    name = repo_name()
    # The two expensive facts about the tree, computed once and threaded down. Both the
    # lock builder and the validator need them, and hashing every in-scope file twice
    # was most of the runtime.
    fps = fingerprints(files)
    dirty = working_tree_dirty()

    if args.validate:
        doc, lock = read_json(JSON_PATH), read_json(LOCK_PATH)
        with open(HTML_PATH, encoding="utf-8") as fh:
            html = fh.read()
    else:
        previous = read_json(LOCK_PATH) if os.path.exists(LOCK_PATH) else None
        generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        doc = build_document(files, commit, generated_at)
        lock = build_lock(commit, generated_at, fps, dirty)
        html = render_html(doc, name)

        os.makedirs(OUT_DIR, exist_ok=True)
        with open(JSON_PATH, "w") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(HTML_PATH, "w") as fh:
            fh.write(html)
        with open(LOCK_PATH, "w") as fh:
            json.dump(lock, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

        delta = compare_lock(previous, lock) if previous else None
        print("stale-module comparison:")
        if delta is None:
            print("  no previous codemap.lock — every module treated as new")
            for mid in sorted(lock["modules"]):
                print(f"  new      {mid}")
        else:
            for key in ("changed", "added", "removed"):
                for mid in delta[key]:
                    print(f"  {key:8s} {mid}")
            if not (delta["changed"] or delta["added"] or delta["removed"]):
                print("  no module fingerprints changed")
        print(f"  layout edge crossings: {crossings(doc['nodes'], doc['edges'])}")

    results = validate(doc, lock, html, files, fps, dirty)
    fails = [f for _, checker_fails in results for f in checker_fails]
    print("\nvalidation:")
    for name, checker_fails in results:
        print(f"  [{'FAIL' if checker_fails else 'PASS'}] {name}")
    if fails:
        print("\nfailures:")
        for f in fails:
            print(f"  - {f}")
    print(
        f"\nnodes={len(doc['nodes'])} edges={len(doc['edges'])} flows={len(doc['flows'])} "
        f"unknown_edges={sum(1 for e in doc['edges'] if e['evidence'] == 'unknown')}"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

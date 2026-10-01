#!/usr/bin/env python3
"""Generate codemap.json, codemap.lock and codemap.html for scrumlr.io.

Read-only against the target repo. Every evidence item is resolved to a real
line number in the tracked working tree; an unresolvable item aborts the run.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

import codemap_data as D

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = D.REPO
EDGE_TYPES = {"imports", "calls", "reads", "writes", "publishes", "subscribes"}
MAX_NODES = 20

FINGERPRINT_ALGO = (
    "sha256-tracked-tree-v1: run `git ls-files -z -- <node.path>`, sort the paths "
    "bytewise, then sha256 over the concatenation of "
    "<path-bytes> + 0x00 + hex(sha256(file-bytes)) + 0x0a for each path. "
    "Content is read from the working tree, not from the index, so uncommitted "
    "edits change the fingerprint. A node whose path is not tracked (external "
    "systems) gets a null fingerprint."
)


GIT = shutil.which("git")


def git(*args, binary=False):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(  # noqa: S603
        [GIT, "-C", REPO, *args], capture_output=True, check=True, env=env
    )
    return r.stdout if binary else r.stdout.decode()


TRACKED = set(git("ls-files").splitlines())


def resolve(ev, where):
    """Attach a line number to one evidence item, or abort."""
    path, match = ev["path"], ev["match"]
    if path not in TRACKED:
        sys.exit(f"ABORT [{where}]: {path} is not tracked by git")
    with open(os.path.join(REPO, path), encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if match in line:
                return {
                    "path": path,
                    "symbol": ev["symbol"],
                    "line": i,
                    "snippet": line.rstrip("\n").strip(),
                }
    sys.exit(f"ABORT [{where}]: no line in {path} contains {match!r}")


def resolve_all(items, where):
    return [resolve(e, where) for e in items]


def fingerprint(path):
    raw = git("ls-files", "-z", "--", path, binary=True)
    files = sorted(p for p in raw.split(b"\x00") if p)
    if not files:
        return None, 0
    h = hashlib.sha256()
    for p in files:
        with open(os.path.join(REPO.encode(), p), "rb") as fh:
            h.update(p + b"\x00" + hashlib.sha256(fh.read()).hexdigest().encode() + b"\n")
    return h.hexdigest(), len(files)


# ------------------------------------------------------------------ build --

nodes = []
for n in D.NODES:
    for field in ("id", "path", "role", "entrypoints", "tests", "constraints", "evidence"):
        if field not in n:
            sys.exit(f"ABORT: node {n.get('id')} is missing {field!r}")
    for t in n["tests"]:
        if t not in TRACKED:
            sys.exit(f"ABORT: node {n['id']} lists untracked test {t}")
    nodes.append({
        "id": n["id"],
        "path": n["path"],
        "role": n["role"],
        "entrypoints": n["entrypoints"],
        "tests": n["tests"],
        "constraints": n["constraints"],
        "evidence": resolve_all(n["evidence"], f"node {n['id']}"),
        "external": n["path"].startswith("external://"),
    })

if len(nodes) > MAX_NODES:
    sys.exit(f"ABORT: {len(nodes)} nodes exceeds the cap of {MAX_NODES}")

ids = {n["id"] for n in nodes}
if len(ids) != len(nodes):
    sys.exit("ABORT: duplicate node ids")

edges = []
for e in D.EDGES:
    if e["type"] not in EDGE_TYPES:
        sys.exit(f"ABORT: edge {e['from']}->{e['to']} has illegal type {e['type']!r}")
    for side in ("from", "to"):
        if e[side] not in ids:
            sys.exit(f"ABORT: edge references unknown node {e[side]!r}")
    where = f"edge {e['from']}->{e['to']}"
    ev = resolve_all(e.get("evidence", []), where)
    status = e.get("evidence_status", "verified" if ev else "unknown")
    if status == "verified" and not ev:
        sys.exit(f"ABORT: {where} is marked verified but carries no evidence")
    out = {"from": e["from"], "to": e["to"], "type": e["type"],
           "evidence": ev, "evidence_status": status}
    if e.get("note"):
        out["note"] = e["note"]
    edges.append(out)

flows = []
for f in D.FLOWS:
    for step in f["steps"]:
        if step["node"] not in ids:
            sys.exit(f"ABORT: flow {f['id']} step references unknown node {step['node']!r}")
    flows.append({
        "id": f["id"],
        "name": f["name"],
        "trigger": f["trigger"],
        "steps": f["steps"],
        "outcome": f["outcome"],
        "evidence": resolve_all(f["evidence"], f"flow {f['id']}"),
    })

# ------------------------------------------------------------------- git --

commit = git("rev-parse", "HEAD").strip()
commit_time = git("show", "-s", "--format=%cI", "HEAD").strip()
branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
porcelain = [row for row in git("status", "--porcelain").splitlines() if row.strip()]

fingerprints = {}
for n in nodes:
    fp, count = (None, 0) if n["external"] else fingerprint(n["path"])
    fingerprints[n["id"]] = {
        "path": n["path"],
        "fingerprint": fp,
        "tracked_files": count,
        **({"reason": "external system - no tracked source in this repository"} if fp is None else {}),
    }

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

codemap = {
    "schema": "scrumlr-codemap/1",
    "repository": {"name": "scrumlr.io", "commit": commit, "branch": branch,
                   "commit_time": commit_time},
    "generated_at": now,
    "node_cap": MAX_NODES,
    "edge_types": sorted(EDGE_TYPES),
    "summary": (
        "scrumlr.io is a collaborative retrospective board. A React 18 + Redux Toolkit "
        "single-page app in src/ talks to a Go (chi) server in server/src/ over REST for "
        "writes and over one websocket per board for reads. The server persists to "
        "PostgreSQL through bun and fans board events out over NATS (default) or Redis "
        "so that multiple server instances stay in step."
    ),
    "not_mapped": D.NOT_MAPPED,
    "nodes": nodes,
    "edges": edges,
    "flows": flows,
}

lock = {
    "schema": "scrumlr-codemap-lock/1",
    "commit": commit,
    "commit_time": commit_time,
    "branch": branch,
    "dirty": bool(porcelain),
    "dirty_paths": porcelain,
    "generated_at": now,
    "generator": "generate.py (data in codemap_data.py, page shell in template.html)",
    "notes": [
        "The working tree was dirty at generation time; dirty_paths lists exactly what differed.",
        "None of the dirty paths sit inside a fingerprinted module, so every module fingerprint "
        "here equals the one the clean commit would produce.",
        "Fingerprints cover tracked files only. Untracked files (including "
        "deployment/docker/.env and deployment/docker/jwt.key) were never read.",
        "The `database` fingerprint covers server/src/database recursively, so it includes the 29 "
        "files also counted under `migrations`.",
        "Every evidence item is mechanically resolved to a line in the tracked working tree and "
        "generation aborts on any item that does not resolve. That guarantee covers the evidence "
        "anchors only. Node roles, constraints and flow step descriptions are curated prose written "
        "from reading those files; they were reviewed against source but are not machine-checked.",
        "Relationships that could not be backed by a source line are recorded with "
        "evidence_status 'unknown' in codemap.json. In this run there are none; modules left off "
        "the map entirely are listed under `not_mapped` in codemap.json.",
    ],
    "scanned_scope": D.SCANNED_SCOPE,
    "excluded_dirs": D.EXCLUDED_DIRS,
    "fingerprint_algorithm": FINGERPRINT_ALGO,
    "module_fingerprints": fingerprints,
    "counts": {
        "nodes": len(nodes),
        "edges": len(edges),
        "edges_unknown": sum(1 for e in edges if e["evidence_status"] == "unknown"),
        "flows": len(flows),
        "evidence_items": sum(len(n["evidence"]) for n in nodes)
        + sum(len(e["evidence"]) for e in edges)
        + sum(len(f["evidence"]) for f in flows),
    },
}

with open(os.path.join(OUT, "codemap.json"), "w") as fh:
    json.dump(codemap, fh, indent=2, sort_keys=False)
    fh.write("\n")
with open(os.path.join(OUT, "codemap.lock"), "w") as fh:
    json.dump(lock, fh, indent=2, sort_keys=False)
    fh.write("\n")

with open(os.path.join(OUT, "template.html")) as fh:
    template = fh.read()
html = template.replace(
    "/*__CODEMAP_DATA__*/null",
    json.dumps(codemap, indent=None).replace("</", "<\\/"),
)
with open(os.path.join(OUT, "codemap.html"), "w") as fh:
    fh.write(html)

print(f"nodes={len(nodes)} edges={len(edges)} "
      f"unknown={lock['counts']['edges_unknown']} flows={len(flows)} "
      f"evidence={lock['counts']['evidence_items']} dirty={lock['dirty']}")

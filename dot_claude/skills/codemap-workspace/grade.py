#!/usr/bin/env python3
"""Mechanically grade a codemap run's outputs against the structural assertions.

Everything here is checkable without judgment: files present, JSON valid, symbols
actually greppable in the repo they cite, enum membership, referential integrity,
HTML/JSON agreement, lock accuracy. Assertions that need a human (did it tell the
user the truth about a service that isn't there?) are left for the viewer.

Usage: grade.py <run_dir> <target_repo>
Writes <run_dir>/grading.json
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

EDGE_TYPES = {"imports", "calls", "reads", "writes", "publishes", "subscribes"}
NODE_FIELDS = ("id", "path", "role", "entrypoints", "tests", "constraints", "evidence")


def find_outputs(run_dir: str) -> str:
    """Agents vary on nesting; locate whichever directory holds codemap.json."""
    for root, _dirs, files in os.walk(run_dir):
        if "codemap.json" in files:
            return root
    return ""


def symbol_in(repo: str, path: str, symbol: str) -> bool:
    full = os.path.join(repo, path)
    if not os.path.isfile(full):
        return False
    with open(full, encoding="utf-8", errors="replace") as fh:
        return symbol in fh.read()


def _extract_embedded(html: str) -> dict | None:
    """Pull the page's inline data, whichever way it was embedded.

    A `<script type="application/json">` block and a `const DATA = {...}` literal are
    both fully self-contained; grading only the first would score conformance to one
    generator's implementation rather than the property we actually care about.
    """
    m = re.search(r'<script[^>]*type="application/json"[^>]*>\s*(.*?)\s*</script>', html, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:  # noqa: BLE001, S110
            pass
    for m in re.finditer(r"(?:const|var|let)\s+\w+\s*=\s*(\{)", html):
        end = _match_brace(html, m.start(1))
        if end is None:
            continue
        try:
            blob = json.loads(html[m.start(1) : end + 1])
        except Exception:  # noqa: BLE001, S112 - a non-JSON literal just isn't the data blob
            continue
        if isinstance(blob, dict) and "nodes" in blob:
            return blob
    return None


def _match_brace(s: str, start: int) -> int | None:
    """Index of the `}` closing the `{` at `start`, skipping string contents."""
    depth, in_str, esc, quote = 0, False, False, ""
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    return None


def result(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def grade(run_dir: str, repo: str) -> dict:
    out = find_outputs(run_dir)
    checks: list[dict] = []

    if not out:
        return {
            "expectations": [
                result("All three files exist", False, "no codemap.json found anywhere in run dir")
            ]
        }

    jp, hp, lp = (os.path.join(out, f) for f in ("codemap.json", "codemap.html", "codemap.lock"))
    present = [f for f, p in (("json", jp), ("html", hp), ("lock", lp)) if os.path.exists(p)]
    checks.append(
        result(
            "All three files exist: codemap.html, codemap.json, codemap.lock",
            len(present) == 3,
            f"found: {', '.join(present) or 'none'}",
        )
    )

    try:
        doc = json.load(open(jp))
        parsed = True
    except Exception as exc:  # noqa: BLE001
        doc, parsed = {}, False
        checks.append(result("codemap.json parses as valid JSON", False, str(exc)[:200]))

    if parsed:
        keys = ("generated_at", "generated_from_commit", "scope", "nodes", "edges", "flows")
        missing = [k for k in keys if k not in doc]
        checks.append(
            result(
                "codemap.json parses and has the six required top-level keys",
                not missing,
                "all present" if not missing else f"missing: {missing}",
            )
        )

    nodes = doc.get("nodes", []) or []
    edges = doc.get("edges", []) or []
    flows = doc.get("flows", []) or []
    ids = {n.get("id") for n in nodes}

    bad = [n.get("id") for n in nodes if any(f not in n for f in NODE_FIELDS)]
    checks.append(
        result(
            "Every node has id, path, role, entrypoints, tests, constraints, evidence",
            not bad and bool(nodes),
            f"{len(nodes)} nodes, non-conforming: {bad[:5] or 'none'}",
        )
    )

    missing_paths = [n["id"] for n in nodes if not os.path.exists(os.path.join(repo, n.get("path", "\0")))]
    checks.append(
        result(
            "Every node path exists on disk in the repo",
            not missing_paths,
            f"missing: {missing_paths[:5] or 'none'}",
        )
    )

    bad_syms = []
    untyped_eps = []
    for n in nodes:
        ev = n.get("evidence")
        if isinstance(ev, dict) and not symbol_in(repo, ev.get("path", ""), ev.get("symbol", "")):
            bad_syms.append(f"{n.get('id')}:{ev.get('symbol')!r} in {ev.get('path')}")
        for ep in n.get("entrypoints") or []:
            # A bare string entrypoint carries no symbol to verify, so it is
            # unverifiable by construction rather than wrong — scored separately.
            if not isinstance(ep, dict):
                untyped_eps.append(f"{n.get('id')}:{ep!r}"[:60])
                continue
            if not symbol_in(repo, ep.get("path", ""), ep.get("symbol", "")):
                bad_syms.append(f"{n.get('id')} entrypoint {ep.get('symbol')!r} in {ep.get('path')}")
    for e in edges:
        ev = e.get("evidence")
        if isinstance(ev, dict) and not symbol_in(repo, ev.get("path", ""), ev.get("symbol", "")):
            bad_syms.append(f"{e.get('from')}->{e.get('to')}:{ev.get('symbol')!r} in {ev.get('path')}")
    checks.append(
        result(
            "Every evidence symbol is literally findable in the file its path names",
            not bad_syms,
            f"{len(bad_syms)} unfindable"
            + (f" e.g. {bad_syms[:3]}" if bad_syms else " (all verified by grep)"),
        )
    )

    checks.append(
        result(
            "Every entrypoint is a {path, symbol} pair so it can be machine-verified",
            not untyped_eps,
            f"{len(untyped_eps)} bare-string entrypoints" + (f" e.g. {untyped_eps[:2]}" if untyped_eps else ""),
        )
    )

    bad_types = sorted({e.get("type") for e in edges} - EDGE_TYPES)
    checks.append(
        result(
            "Every edge type is within the allowed six-value enum",
            not bad_types,
            f"illegal: {bad_types}" if bad_types else f"{len(edges)} edges, all legal",
        )
    )

    dangling = [
        f"{e.get('from')}->{e.get('to')}"
        for e in edges
        if e.get("from") not in ids or e.get("to") not in ids
    ]
    dangling += [
        f"{f.get('id')}:{s.get('node')}"
        for f in flows
        for s in f.get("steps") or []
        if s.get("node") not in ids
    ]
    checks.append(
        result(
            "Every edge endpoint and flow step resolves to an existing node id",
            not dangling,
            f"dangling: {dangling[:5] or 'none'}",
        )
    )

    checks.append(
        result("Node count is 20 or fewer", len(nodes) <= 20, f"{len(nodes)} nodes")
    )

    checks += _grade_presentation(out, doc, repo)
    checks += _grade_semantics(doc)
    return {"expectations": checks}


def _grade_presentation(out: str, doc: dict, repo: str) -> list[dict]:
    """HTML self-containment, JSON agreement, header, and lock accuracy."""
    checks: list[dict] = []
    hp, lp = os.path.join(out, "codemap.html"), os.path.join(out, "codemap.lock")
    html = open(hp, encoding="utf-8", errors="replace").read() if os.path.exists(hp) else ""
    emb = _extract_embedded(html)
    if emb is None:
        same, ev = False, "no inline data blob found in HTML (neither a JSON script block nor a JS data literal)"
    else:
        emb_ids = {n.get("id") for n in emb.get("nodes", []) or []}
        doc_ids = {n.get("id") for n in doc.get("nodes", []) or []}
        counts_match = len(emb.get("edges", []) or []) == len(doc.get("edges", []) or []) and len(
            emb.get("flows", []) or []
        ) == len(doc.get("flows", []) or [])
        same = bool(doc_ids) and emb_ids == doc_ids and counts_match
        ev = (
            f"inline blob carries {len(emb_ids)} node ids, "
            f"{len(emb.get('edges', []) or [])} edges, {len(emb.get('flows', []) or [])} flows; "
            + ("matches codemap.json" if same else "DIFFERS from codemap.json")
        )
    checks.append(
        result("codemap.html carries the same nodes/edges/flows as codemap.json inline", same, ev)
    )

    # Scan only the real markup. The embedded JSON payload legitimately quotes source
    # code as evidence, and that code may contain vendor URLs (e.g. a gtag injection
    # line) — those are data about the repo, not references the page actually loads.
    markup = re.sub(
        r'<script[^>]*type="application/json"[^>]*>.*?</script>', "", html, flags=re.S
    )
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', markup)
    ext = [u for u in ext if "w3.org" not in u]
    checks.append(
        result(
            "codemap.html has no external network references (fully self-contained)",
            not ext,
            f"external refs: {ext[:3]}" if ext else "none",
        )
    )

    head = subprocess.run(  # noqa: S603
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    commit = doc.get("generated_from_commit", "")
    has_commit = bool(commit) and commit[:12] in html
    has_time = bool(doc.get("generated_at")) and str(doc.get("generated_at", ""))[:10] in html
    # basename(repo) is the BRANCH name inside a worktree, not the repo. Derive it the
    # way the generator does, from the common git dir, which lives in the primary checkout.
    common = subprocess.run(  # noqa: S603
        ["/usr/bin/git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=repo,
        capture_output=True,
        text=True,
    ).stdout.strip()
    repo_name = os.path.basename(os.path.dirname(common)) if common else os.path.basename(repo.rstrip("/"))
    has_name = repo_name.lower() in html.lower()
    checks.append(
        result(
            "codemap.html header shows repo name, generation time and source commit",
            has_commit and has_time and has_name,
            f"name={has_name} time={has_time} commit={has_commit}",
        )
    )

    try:
        lock = json.load(open(lp))
        lock_ok = True
    except Exception as exc:  # noqa: BLE001
        lock, lock_ok = {}, False
        checks.append(result("codemap.lock parses as JSON", False, str(exc)[:150]))

    if lock_ok:
        need = ("commit", "dirty", "scope", "fingerprint_algorithm")
        miss = [k for k in need if k not in lock]
        has_excl = any("exclud" in k for k in lock)
        has_mods = bool(lock.get("modules"))
        checks.append(
            result(
                "codemap.lock records commit, dirty flag, scope, exclusions, algorithm, per-module fingerprints",
                not miss and has_excl and has_mods,
                f"missing={miss or 'none'} exclusions={has_excl} modules={len(lock.get('modules', {}))}",
            )
        )
        checks.append(
            result(
                "codemap.lock commit matches the repo's actual HEAD",
                lock.get("commit", "")[:12] == head[:12],
                f"lock={lock.get('commit','')[:12]} head={head[:12]}",
            )
        )

    return checks


def _grade_semantics(doc: dict) -> list[dict]:
    """Flow completeness and the unknown-marking convention."""
    checks: list[dict] = []
    flows = doc.get("flows", []) or []
    edges = doc.get("edges", []) or []
    ok_flows = [
        f for f in flows if f.get("trigger") and f.get("steps") and f.get("outcome")
    ]
    checks.append(
        result(
            "At least 3 flows, each with trigger, steps and outcome",
            len(ok_flows) >= 3,
            f"{len(ok_flows)} complete of {len(flows)}",
        )
    )

    unk = [e for e in edges if e.get("evidence") == "unknown" or e.get("type") == "unknown"]
    type_unknown = [e for e in edges if e.get("type") == "unknown"]
    noteless = [e for e in unk if not e.get("note")]
    checks.append(
        result(
            "Unknowns are marked in the evidence field (never as a type) and carry a note",
            not type_unknown and not noteless,
            f"{len(unk)} unknown edges; type-as-unknown={len(type_unknown)}; missing note={len(noteless)}",
        )
    )

    return checks


if __name__ == "__main__":
    run_dir, target = sys.argv[1], sys.argv[2]
    g = grade(run_dir, target)
    with open(os.path.join(run_dir, "grading.json"), "w") as fh:
        json.dump(g, fh, indent=2)
    p = sum(1 for c in g["expectations"] if c["passed"])
    print(f"{run_dir}: {p}/{len(g['expectations'])}")
    for c in g["expectations"]:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['text']}  — {c['evidence']}")

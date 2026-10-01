#!/usr/bin/env python3
"""
C4 Diagram Evaluator — regex-based, stdlib only, Python 3.6+

Usage:
    python3 evaluate.py --batch outputs/iteration-001/ scenarios.json
    python3 evaluate.py --file outputs/iteration-001/scenario-01.puml scenarios.json 01
"""

import re
import json
import sys
import os
import argparse


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Matches: Person, System, Container, Component with optional Db/Queue and _Ext
# Capture groups: (1) base_type  (2) Db/Queue suffix or ""  (3) _Ext or ""  (4) id  (5) name
ELEMENT_RE = re.compile(
    r'^\s*(Person|System|Container|Component)(Db|Queue)?(Ext)?'
    r'(?:_Ext)?\s*\(\s*(\w+)\s*,\s*"([^"]*)"',
    re.MULTILINE,
)

# Normalise element type from regex groups back to canonical form
# e.g. ("Container", "Db", "") -> "ContainerDb"
# e.g. ("System", "", "Ext") -> "System_Ext"
# The regex above doesn't perfectly split all variants, so we re-match more carefully below.

ELEMENT_CANONICAL_RE = re.compile(
    r'^\s*(Person_Ext|Person|System_Ext|System|'
    r'ContainerDb_Ext|ContainerDb|ContainerQueue_Ext|ContainerQueue|'
    r'Container_Ext|Container|'
    r'ComponentDb_Ext|ComponentDb|ComponentQueue_Ext|ComponentQueue|'
    r'Component_Ext|Component)'
    r'\s*\(\s*(\w+)\s*,\s*"([^"]*)"',
    re.MULTILINE,
)

# Matches: (Bi)?Rel(_U|_D|_L|_R)?(source, target, "label"[, "tech"])
REL_RE = re.compile(
    r'^\s*(Bi)?Rel(?:_[UDLR])?\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]*)"'
    r'(?:\s*,\s*"([^"]*)")?',
    re.MULTILINE,
)

# Detect diagram type from !include URL
INCLUDE_RE = re.compile(
    r'!include\s+https?://[^\s]+/C4_(Context|Container|Component|Sequence)\.puml',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_elements(puml_text):
    """Return list of dicts: {type, id, name}"""
    elements = []
    for m in ELEMENT_CANONICAL_RE.finditer(puml_text):
        elements.append({
            "type": m.group(1),
            "id": m.group(2),
            "name": m.group(3),
        })
    return elements


def parse_relationships(puml_text):
    """Return list of dicts: {source_id, target_id, label, tech}"""
    rels = []
    for m in REL_RE.finditer(puml_text):
        rels.append({
            "source_id": m.group(2),
            "target_id": m.group(3),
            "label": m.group(4) or "",
            "tech": m.group(5) or "",
        })
    return rels


def detect_diagram_type(puml_text):
    """Return 'context'|'container'|'component'|'sequence'|'unknown'"""
    m = INCLUDE_RE.search(puml_text)
    if m:
        return m.group(1).lower()
    return "unknown"


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def score_completeness(elements, rels, scenario):
    """
    All expected_elements found (type+name substring match) AND
    all expected_relationships found (source_id + target_id substring match against element names).

    Returns (pass: bool, details: str)
    """
    missing_elements = []
    for exp in scenario.get("expected_elements", []):
        exp_type = exp["type"]
        exp_name = exp["name_contains"].lower()
        found = any(
            e["type"] == exp_type and exp_name in e["name"].lower()
            for e in elements
        )
        if not found:
            missing_elements.append(f"{exp_type}(name~'{exp['name_contains']}')")

    missing_rels = []
    for exp_rel in scenario.get("expected_relationships", []):
        from_sub = exp_rel["from_contains"].lower()
        to_sub = exp_rel["to_contains"].lower()
        # Find element ids matching from/to substrings
        from_ids = {e["id"] for e in elements if from_sub in e["name"].lower() or from_sub in e["id"].lower()}
        to_ids = {e["id"] for e in elements if to_sub in e["name"].lower() or to_sub in e["id"].lower()}
        found = any(
            r["source_id"] in from_ids and r["target_id"] in to_ids
            for r in rels
        )
        if not found:
            missing_rels.append(f"Rel(~'{exp_rel['from_contains']}' -> ~'{exp_rel['to_contains']}')")

    passed = not missing_elements and not missing_rels
    parts = []
    if missing_elements:
        parts.append("missing elements: " + ", ".join(missing_elements))
    if missing_rels:
        parts.append("missing rels: " + ", ".join(missing_rels))
    detail = "; ".join(parts) if parts else "ok"
    return passed, detail


def score_technology(elements, diagram_type):
    """
    All Container*/Component* elements have ≥3 quoted params (i.e., technology param present).
    Auto-pass for context diagrams (no containers/components expected).

    We infer this from element type — if element was parsed it already has name,
    but we need to check the raw line for a 3rd quoted string (the technology param).
    We pass the full puml text and re-check inline.

    Since parse_elements already uses ELEMENT_CANONICAL_RE which requires at least name,
    we need to re-check the original text for the technology param.
    Returns (pass: bool, details: str)
    """
    # We'll re-check by looking for elements that are containers/components
    tech_required_types = {t for t in [
        "Container", "ContainerDb", "ContainerQueue",
        "Container_Ext", "ContainerDb_Ext", "ContainerQueue_Ext",
        "Component", "ComponentDb", "ComponentQueue",
        "Component_Ext", "ComponentDb_Ext", "ComponentQueue_Ext",
    ]}
    relevant = [e for e in elements if e["type"] in tech_required_types]

    if not relevant:
        return True, "auto-pass (no container/component elements)"

    # We'll pass puml_text separately — this function will be called with it
    return None, None  # placeholder, handled in evaluate_file


def score_technology_from_text(puml_text, elements):
    """Check each Container/Component line for ≥3 quoted params (tech param)."""
    tech_required_types = {
        "Container", "ContainerDb", "ContainerQueue",
        "Container_Ext", "ContainerDb_Ext", "ContainerQueue_Ext",
        "Component", "ComponentDb", "ComponentQueue",
        "Component_Ext", "ComponentDb_Ext", "ComponentQueue_Ext",
    }
    relevant = [e for e in elements if e["type"] in tech_required_types]
    if not relevant:
        return True, "auto-pass (no container/component elements)"

    missing_tech = []
    # Check all Container/Component lines
    for line in puml_text.splitlines():
        line_stripped = line.strip()
        type_match = re.match(r'^((?:Container|Component)[A-Za-z_]*)\s*\(', line_stripped)
        if not type_match:
            continue
        elem_type = type_match.group(1)
        if elem_type not in tech_required_types:
            continue
        # Check it has a 3rd quoted param
        if not re.search(r'^\s*[A-Za-z_]+\s*\(\s*\w+\s*,\s*"[^"]+"\s*,\s*"[^"]*"', line_stripped):
            # Extract id for reporting
            id_match = re.search(r'\(\s*(\w+)', line_stripped)
            elem_id = id_match.group(1) if id_match else "?"
            missing_tech.append(f"{elem_type}({elem_id}) missing technology param")

    passed = not missing_tech
    detail = "; ".join(missing_tech) if missing_tech else "ok"
    return passed, detail


def score_relationships(rels):
    """
    All Rel() calls have non-empty 3rd param (label) AND 4th param (protocol/tech).
    Returns (pass: bool, details: str)
    """
    if not rels:
        return True, "auto-pass (no relationships)"

    missing_label = []
    missing_tech = []
    for r in rels:
        if not r["label"].strip():
            missing_label.append(f"Rel({r['source_id']},{r['target_id']}) missing label")
        if not r["tech"].strip():
            missing_tech.append(f"Rel({r['source_id']},{r['target_id']}) missing protocol")

    issues = missing_label + missing_tech
    passed = not issues
    detail = "; ".join(issues[:5]) if issues else "ok"  # cap to 5 to keep compact
    if len(issues) > 5:
        detail += f" (+{len(issues)-5} more)"
    return passed, detail


def score_abstraction(elements, scenario):
    """
    All element types are in the valid_element_types whitelist for this scenario.
    Returns (pass: bool, details: str)
    """
    valid = set(scenario.get("valid_element_types", []))
    if not valid:
        return True, "auto-pass (no whitelist defined)"

    wrong = []
    for e in elements:
        if e["type"] not in valid:
            wrong.append(f"{e['type']}({e['id']})")

    passed = not wrong
    detail = "wrong types: " + ", ".join(wrong) if wrong else "ok"
    return passed, detail


# ---------------------------------------------------------------------------
# File evaluator
# ---------------------------------------------------------------------------

def evaluate_file(puml_path, scenario):
    """
    Evaluate a single .puml file against a scenario.
    Returns dict: {scenario_id, completeness, technology, relationships, abstraction, total, details}
    """
    try:
        with open(puml_path, "r", encoding="utf-8") as f:
            puml_text = f.read()
    except FileNotFoundError:
        return {
            "scenario_id": scenario["id"],
            "completeness": 0,
            "technology": 0,
            "relationships": 0,
            "abstraction": 0,
            "total": 0,
            "details": f"FILE NOT FOUND: {puml_path}",
        }

    elements = parse_elements(puml_text)
    rels = parse_relationships(puml_text)
    diagram_type = detect_diagram_type(puml_text)

    c_pass, c_detail = score_completeness(elements, rels, scenario)
    t_pass, t_detail = score_technology_from_text(puml_text, elements)
    r_pass, r_detail = score_relationships(rels)
    a_pass, a_detail = score_abstraction(elements, scenario)

    scores = {
        "completeness": 1 if c_pass else 0,
        "technology": 1 if t_pass else 0,
        "relationships": 1 if r_pass else 0,
        "abstraction": 1 if a_pass else 0,
    }

    return {
        "scenario_id": scenario["id"],
        "diagram_type": scenario["diagram_type"],
        "detected_type": diagram_type,
        "completeness": scores["completeness"],
        "technology": scores["technology"],
        "relationships": scores["relationships"],
        "abstraction": scores["abstraction"],
        "total": sum(scores.values()),
        "details": {
            "completeness": c_detail,
            "technology": t_detail,
            "relationships": r_detail,
            "abstraction": a_detail,
        },
    }


# ---------------------------------------------------------------------------
# Batch evaluator
# ---------------------------------------------------------------------------

def evaluate_batch(outputs_dir, scenarios):
    """
    Evaluate all scenario-NN.puml files in outputs_dir.
    Returns summary dict with per-scenario results and totals.
    """
    results = []
    totals = {"completeness": 0, "technology": 0, "relationships": 0, "abstraction": 0, "total": 0}

    for scenario in scenarios:
        puml_path = os.path.join(outputs_dir, f"scenario-{scenario['id']}.puml")
        result = evaluate_file(puml_path, scenario)
        results.append(result)
        totals["completeness"] += result["completeness"]
        totals["technology"] += result["technology"]
        totals["relationships"] += result["relationships"]
        totals["abstraction"] += result["abstraction"]
        totals["total"] += result["total"]

    n = len(scenarios)
    summary = {
        "scenarios": results,
        "totals": totals,
        "max_score": n * 4,
        "score": totals["total"],
        "breakdown": {
            "completeness": f"{totals['completeness']}/{n}",
            "technology": f"{totals['technology']}/{n}",
            "relationships": f"{totals['relationships']}/{n}",
            "abstraction": f"{totals['abstraction']}/{n}",
        },
    }
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Evaluate C4 PlantUML diagrams")
    parser.add_argument(
        "--batch", metavar="OUTPUTS_DIR",
        help="Directory containing scenario-NN.puml files"
    )
    parser.add_argument(
        "--file", metavar="PUML_PATH",
        help="Single .puml file to evaluate"
    )
    parser.add_argument(
        "scenarios_json",
        help="Path to scenarios.json"
    )
    parser.add_argument(
        "scenario_id", nargs="?",
        help="Scenario ID for --file mode (e.g. '01')"
    )
    args = parser.parse_args()

    with open(args.scenarios_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data["scenarios"]

    if args.batch:
        summary = evaluate_batch(args.batch, scenarios)
        print(json.dumps(summary, indent=2))
        # Print compact summary to stderr for easy reading
        print(
            f"\nSCORE: {summary['score']}/{summary['max_score']} "
            f"| completeness={summary['breakdown']['completeness']} "
            f"  technology={summary['breakdown']['technology']} "
            f"  relationships={summary['breakdown']['relationships']} "
            f"  abstraction={summary['breakdown']['abstraction']}",
            file=sys.stderr,
        )
    elif args.file:
        if not args.scenario_id:
            print("ERROR: --file requires a scenario_id argument", file=sys.stderr)
            sys.exit(1)
        scenario = next((s for s in scenarios if s["id"] == args.scenario_id), None)
        if not scenario:
            print(f"ERROR: scenario '{args.scenario_id}' not found", file=sys.stderr)
            sys.exit(1)
        result = evaluate_file(args.file, scenario)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

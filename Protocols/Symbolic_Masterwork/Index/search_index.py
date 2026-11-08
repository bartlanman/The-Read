#!/usr/bin/env python3
"""Search and validate the Symbolic Masterwork JSON index.

No external dependencies. Every search writes a local encounter JSONL record
(default: Index/encounters.local.jsonl); commit reviewed records deliberately.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "symbols.json"
DEFAULT_LOG = ROOT / "encounters.local.jsonl"

def load():
    with INDEX.open(encoding="utf-8") as f:
        return json.load(f)

def validate(index):
    rows = index["symbols"]
    ids = [x["id"] for x in rows]
    errors = []
    if len(ids) != len(set(ids)):
        errors.append("duplicate symbol ID")
    for item in rows:
        for required in ("id", "name", "kind", "status", "files", "fundamental_proposition"):
            if required not in item:
                errors.append(f"{item.get('id', '?')}: missing {required}")
        for rel in item.get("relations", []):
            if rel["target"] not in ids:
                errors.append(f"{item['id']}: unknown relation target {rel['target']}")
        for key, filename in item.get("files", {}).items():
            if not (ROOT / filename).is_file():
                errors.append(f"{item['id']}: broken {key} path {filename}")
        for item_id in item.get("inputs", []):
            if item_id not in ids:
                errors.append(f"{item['id']}: unknown input {item_id}")
        if item["fundamental_proposition"].get("verified_as_historical_meaning") is not False:
            errors.append(f"{item['id']}: proposed meaning must not claim historical verification")
    return errors

def flattened_text(item):
    terms = [item.get("name", ""),item.get("id", ""),item.get("formal_structure", ""),
             item.get("fundamental_proposition", {}).get("text", ""),
             item.get("visual_status", "")]
    for k in ("aliases", "keywords", "traditions", "unresolved"):
        terms.extend(item.get(k, []))
    terms.extend(c.get("label", "") for c in item.get("contexts", []))
    return " ".join(terms).casefold()

def search(index, query, kind=None):
    terms = query.casefold().split()
    return [x for x in index["symbols"] if (not kind or x["kind"] == kind)
            and all(term in flattened_text(x) for term in terms)]

def main():
    p = argparse.ArgumentParser(description="Search the Symbolic Masterwork Index")
    p.add_argument("query", nargs="*", help="one or more search words (all must match)")
    p.add_argument("--kind", choices=["symbol", "masterwork_collision"])
    p.add_argument("--validate", action="store_true", help="verify index IDs and file links")
    p.add_argument("--no-log", action="store_true", help="skip local search logging (for tests only)")
    p.add_argument("--log-file", type=Path, default=DEFAULT_LOG)
    args = p.parse_args()
    index = load()
    errors = validate(index)
    if args.validate:
        if errors:
            for error in errors:
                print("ERROR:", error)
            raise SystemExit(1)
        print(f"Valid: {len(index['symbols'])} records and {len(index['reference_collections'])} reference lens definitions")
        if not args.query:
            return
    elif errors:
        raise SystemExit("Invalid index; run --validate")
    query = " ".join(args.query).strip()
    results = search(index, query, args.kind) if query else [x for x in index["symbols"] if not args.kind or x["kind"] == args.kind]
    for item in results:
        print(f"{item['id']} | {item['name']} | {item['kind']} | {item['status']}")
        print(f"  Proposition ({item['fundamental_proposition']['epistemic_type']}): {item['fundamental_proposition']['text']}")
        for kind, path in item["files"].items():
            print(f"  {kind}: {(ROOT / path).resolve()}")
    print(f"{len(results)} result(s)")
    if not args.no_log:
        record = {
            "encounter_id": "IDX-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "resource": "local Symbol Index", "stage": "retrieval",
            "inquiry": query or "(browse all)", "purpose": "find relevant records",
            "matched_ids": [x["id"] for x in results],
            "epistemic_type": "INDEX RETRIEVAL ONLY",
            "interpretation": None,
            "index_action": "NO CHANGE",
            "review_required": True,
            "note": "Retrieval log only; source encounters and inferred connections require a reviewed Encounter Record."
        }
        args.log_file.parent.mkdir(parents=True, exist_ok=True)
        with args.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Retrieval logged: {args.log_file}")

if __name__ == "__main__":
    main()

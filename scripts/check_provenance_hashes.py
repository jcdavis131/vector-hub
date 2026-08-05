#!/usr/bin/env python3
"""A field called `source_hashes` must contain hashes, and must cover `source_files`.

Solo personal project, no connection to employer, built with public/free-tier only

dumbmodel.com's fine print says every number is recomputable from public sources. Each
page carries `source_files` (what it was built from) and `source_hashes` (what those
files were, so a reader can tell whether the page still describes them). Nothing checked
that the second field contains what its name promises.

IT DOES NOT, ON ONE PAGE. assets/data/scout_cli.json:

    source_files    11
    source_hashes    6      -- every other page matches exactly

and not one of those six values is a hash:

    bundles/manifest.json           -> "v3.3-OODA-Agentic-MoMA-Graph-C"   version string
    bundles/router/router.ultra.js  -> "10746b v3.3"                      size + version
    bundles/ultra/checkpoint-manager.js  -> "4.6K"                        file SIZE
    bundles/ultra/recovery-ladder.js     -> "5.7K"
    bundles/ultra/communication-pacing.js-> "5.1K"
    bundles/ultra/verification-economics.js -> "5.3K"

A size is not a checksum. Two different files of 4.6K collide trivially, so the field
verifies nothing while looking like it verifies everything -- a real value answering a
different question than the one it appears to answer, in the provenance block of a site
whose central claim is provenance.

THREE ARMS, and the third is the one that matters:

    COVERAGE  every source_files entry has a source_hashes entry
    SHAPE     every source_hashes value LOOKS like a hash (hex, >= 8 chars)
    TRUTH     for files this box can resolve, the recorded hash MATCHES the file

WHAT THIS BOX CANNOT DO, stated rather than skipped. 57 of 64 source_files resolve under
the estate root; the other 7 are `bundles/*`, which live on the Hatch VM. Their hashes
can be checked for SHAPE but never for TRUTH from here, and they are reported as
UNRESOLVABLE rather than passed. Every one of scout_cli.json's six fake values is a
bundles/* entry, so this checker can prove they are not hashes and cannot supply the
right ones.

    python scripts/check_provenance_hashes.py
    python scripts/check_provenance_hashes.py --check   # exit 1 on coverage or shape failure

Writes: reports/provenance_audit.json  (NOT assets/data/ — see the OUT comment)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "data"
ESTATE = ROOT.parent
# NOT under assets/data/. That directory is the PAGE namespace, and
# vector-unified/pipeline/check_superlatives.py globs every *.json in it and
# reads d["slug"] on each. Writing a non-page there crashed that checker with
# KeyError: 'slug' — my artifact broke a sibling repo's gate.
OUT = ROOT / "reports" / "provenance_audit.json"

# A hash is hex and long enough to mean something. The recorded ones elsewhere in this
# repo are 16-char truncated sha256, so 8 is a generous floor.
HASH_SHAPE = re.compile(r"^[0-9a-fA-F]{8,64}$")


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any page fails COVERAGE or SHAPE")
    args = ap.parse_args()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pages, uncovered, malformed, mismatched, unresolvable = {}, [], [], [], []
    for f in sorted(DATA.glob("*.json")):
        if f.name.startswith("_"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"FAIL: {f.name} is not readable JSON: {e}", file=sys.stderr)
            return 2
        sf = d.get("source_files") or []
        sh = d.get("source_hashes") or {}
        if not isinstance(sh, dict):
            sh = {}
        n_ok = n_bad = n_unres = 0
        for s in sf:
            if s not in sh:
                uncovered.append({"page": f.name, "source_file": s})
                continue
            v = str(sh[s])
            if not HASH_SHAPE.match(v):
                malformed.append({"page": f.name, "source_file": s, "value": v,
                                  "why": "not hex, or shorter than 8 chars — a size or "
                                         "version string, not a checksum"})
                n_bad += 1
                continue
            p = ESTATE / s
            if not p.exists():
                unresolvable.append({"page": f.name, "source_file": s,
                                     "recorded": v,
                                     "why": "not present on this box — shape checked, "
                                            "truth cannot be"})
                n_unres += 1
                continue
            actual = sha16(p)
            if actual != v.lower()[:len(actual)]:
                mismatched.append({"page": f.name, "source_file": s,
                                   "recorded": v, "actual": actual})
            else:
                n_ok += 1
        pages[f.name] = {"source_files": len(sf), "source_hashes": len(sh),
                         "verified_true": n_ok, "malformed": n_bad,
                         "unresolvable_here": n_unres,
                         "uncovered": sum(1 for u in uncovered if u["page"] == f.name)}

    out = {
        "question": "Does every page's source_hashes contain actual hashes, covering "
                    "every source_files entry, matching the files they name?",
        "arms": {"COVERAGE": "every source_files entry has a source_hashes entry",
                 "SHAPE": "every value is hex and >= 8 chars",
                 "TRUTH": "for resolvable files, the recorded hash matches"},
        "pages": pages,
        "uncovered_source_files": uncovered,
        "malformed_hashes": malformed,
        "mismatched_hashes": mismatched,
        "unresolvable_from_this_box": unresolvable,
        "what_this_box_cannot_verify": "bundles/* live on the Hatch VM. Their values can "
            "be checked for SHAPE but never for TRUTH from here. They are reported "
            "UNRESOLVABLE, never passed — a checker that counts an unreadable file as OK "
            "is worse than no checker.",
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"{'page':<18}{'files':>6}{'hashes':>7}{'true':>6}{'bad':>5}{'unres':>6}{'uncov':>6}")
    for k, v in pages.items():
        print(f"  {k:<16}{v['source_files']:>6}{v['source_hashes']:>7}"
              f"{v['verified_true']:>6}{v['malformed']:>5}"
              f"{v['unresolvable_here']:>6}{v['uncovered']:>6}")
    print(f"\n  uncovered {len(uncovered)}  malformed {len(malformed)}  "
          f"MISMATCHED {len(mismatched)}  unresolvable {len(unresolvable)}")
    for m in malformed:
        print(f"    MALFORMED {m['page']} {m['source_file']} = {m['value']!r}")
    for m in mismatched:
        print(f"    MISMATCH  {m['page']} {m['source_file']} "
              f"recorded {m['recorded']} actual {m['actual']}")
    print(f"\nwrote {OUT}")
    if args.check and (uncovered or malformed or mismatched):
        print(f"CHECK FAILED: {len(uncovered)} uncovered, {len(malformed)} malformed, "
              f"{len(mismatched)} mismatched", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

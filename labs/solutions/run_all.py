# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Runs every solution of the course and prints PASS or the first difference.

  uv run labs/solutions/run_all.py

Nothing here calls a language model. Yaraa's answers, the image tallies and the drafted letter are
scripted stand-ins written for the course; the classifier of lab 1.3 is a transparent stand-in too.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import labkit as K  # noqa: E402


def expect(name: str, got, want) -> None:
    if got != want:
        print(f"FAIL  {name}: got {got!r}, expected {want!r}")
        raise SystemExit(1)
    print(f"ok    {name}: {got}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    F, S = K.FILES, HERE

    # 1.1 the reference map scores full marks; the blank sheet scores only its solved row
    expect("1.1 reference map", K.score_map(S / "competence_map_reference.csv")[:2], (12, 12))
    expect("1.1 blank sheet", K.score_map(F / "competence_map.csv")[0], 3)

    # 1.2 two rules fit all twelve training cards; only the tail survives the six test cards
    rules = K.kite_rules()
    perfect = [r for r in rules if r["train"] == 12]
    expect("1.2 rules that fit all training cards", sorted(r["rule"] for r in perfect), ["الذيل = نعم", "اللون = أحمر"])
    expect("1.2 the red rule on the test cards", next(r["test"] for r in perfect if "أحمر" in r["rule"]), 2)
    expect("1.2 the tail rule on the test cards", next(r["test"] for r in perfect if "الذيل" in r["rule"]), 6)

    # 1.3 the pack, then train, break and fix
    pack = K.pack_counts()
    expect("1.3 pictures in the pack", pack["counts"], {"train": 40, "test_same": 20, "test_shifted": 20, "train_mixed": 40, "test_new": 6})
    expect("1.3 corrupt files", pack["corrupt"], None)
    rows = K.signs_rows()
    first = K.train_centroids(rows, "train")
    expect("1.3 first classifier, same backgrounds", K.accuracy(first, rows, "test_same"), (20, 20))
    expect("1.3 first classifier, swapped backgrounds", K.accuracy(first, rows, "test_shifted"), (0, 20))
    fixed = K.train_centroids(rows, "train_mixed")
    expect("1.3 fixed classifier, same backgrounds", K.accuracy(fixed, rows, "test_same"), (20, 20))
    expect("1.3 fixed classifier, swapped backgrounds", K.accuracy(fixed, rows, "test_shifted"), (20, 20))
    new = sorted({K.predict(fixed, r) for r in rows if r["set"] == "test_new"})
    print("ok    1.3 what the fixed classifier calls squares and upside-down triangles:", new)
    assert set(new) <= {"circle", "triangle"}

    # 2.1 the key, and the three answers arithmetic can settle
    expect("2.1 reference sheet", K.score_fact_check(S / "fact_check_reference.csv")[:2], (15, 15))
    expect("2.1 blank sheet", K.score_fact_check(F / "fact_check_sheet.csv")[0], 0)
    re = K.recheck_yaraa()
    expect("2.1 15% of 240", re["q1"], 36)
    expect("2.1 divisors of 91", re["q5_factors"], [7, 13])
    flawed = sorted(n for n, v in K.KEY["fact_check"].items() if not v["sound"])
    expect("2.1 flawed answers", flawed, ["10", "3", "4", "5", "8"])
    expect("2.1 one of each kind", sorted(v["kind"] for v in K.KEY["fact_check"].values() if v["kind"]), ["أ", "ب", "ج", "د", "هـ"])

    # 2.2 the tally recounted from the 80 rows, and the media key
    tally = K.gallery_tally()
    men = {k.split()[-1]: v["رجل"] for k, v in tally.items()}
    expect("2.2 pictures showing a man, of 20", men, {"الطب": 17, "التمريض": 2, "الهندسة": 19, "التدريس": 9})
    expect("2.2 rows", sum(v["رجل"] + v["امرأة"] for v in tally.values()), 80)
    expect("2.2 media reference", K.score_simple(S / "media_reference.csv", K.KEY["media"])[:2], (4, 4))

    # 2.3 the worked plan passes; the flawed plan is caught on each planted defect
    expect("2.3 worked plan", K.check_plan(F / "lesson_plan_example.txt"), [])
    flaws = K.check_plan(F / "lesson_plan_flawed.txt")
    for f in flaws:
        print("      flawed plan:", f)
    expect("2.3 defects found in the flawed plan", len(flaws), 7)
    expect("2.3 empty template", len(K.check_plan(F / "lesson_plan_template.txt")), 11)

    # 3.1 the clinic key
    expect("3.1 reference decisions", K.score_simple(S / "clinic_reference.csv", K.KEY["clinic"], "decision")[:2], (6, 6))
    expect("3.1 blank sheet", K.score_simple(F / "clinic_sheet.csv", K.KEY["clinic"], "decision")[0], 0)

    # 3.2 the reference letter passes; the drafted letter fails
    expect("3.2 reference letter", K.check_letter(S / "letter_reference.txt"), [])
    stats = K.letter_stats((S / "letter_reference.txt").read_text(encoding="utf-8"))
    print("ok    3.2 reference letter:", stats)
    draft = K.check_letter(F / "letter_draft_yaraa.txt")
    for d in draft:
        print("      drafted letter:", d)
    expect("3.2 defects found in the drafted letter", len(draft), 7)

    print("PASS")


if __name__ == "__main__":
    main()

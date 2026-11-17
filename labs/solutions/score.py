# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scores one participant file against the key, or lists the defects of a plan or a letter.

  uv run labs/solutions/score.py map <competence_map.csv>
  uv run labs/solutions/score.py facts <fact_check_sheet.csv>
  uv run labs/solutions/score.py media <media_sheet.csv>
  uv run labs/solutions/score.py clinic <clinic_sheet.csv>
  uv run labs/solutions/score.py plan <lesson plan .txt>
  uv run labs/solutions/score.py letter <letter .txt>
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import labkit as K  # noqa: E402


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    kind, path = sys.argv[1], Path(sys.argv[2])
    if kind in ("plan", "letter"):
        bad = K.check_plan(path) if kind == "plan" else K.check_letter(path)
        print("PASS" if not bad else "\n".join(bad))
        return
    got, total, notes = {
        "map": lambda: K.score_map(path),
        "facts": lambda: K.score_fact_check(path),
        "media": lambda: K.score_simple(path, K.KEY["media"]),
        "clinic": lambda: K.score_simple(path, K.KEY["clinic"], "decision"),
    }[kind]()
    print(f"{got} / {total}")
    for n in notes:
        print(" ", n)


if __name__ == "__main__":
    main()

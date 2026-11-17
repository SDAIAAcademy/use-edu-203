"""The checks behind every lab solution of USE-EDU-203. Standard library only. No language model is called.

Used by run_all.py and by the small command-line scripts beside it. Each function returns plain values,
so a trainer can read what was checked.
"""
from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = HERE.parent / "files"
KEY = json.loads((HERE / "key.json").read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def col(row: dict, n: int) -> str:
    return (list(row.values())[n] or "").strip()


# ---------------------------------------------------------------- 1.1 the competence map
def score_map(path: Path) -> tuple[int, int, list[str]]:
    """One point each for the age band, a national code in the accepted set, and literacy against tool use."""
    notes, got, total = [], 0, 0
    for row in read_csv(path):
        lid = col(row, 0)
        if lid not in KEY["map"]:
            continue
        k = KEY["map"][lid]
        total += 3
        band = col(row, 1).replace(" ", "").replace("–", "-")
        codes = set(re.findall(r"D\d\.\d", col(row, 2))) or {col(row, 2)}
        checks = [band == k["band"], bool(codes & set(k["codes"])), col(row, 4) == k["literacy"]]
        got += sum(checks)
        for ok, what in zip(checks, ["الفئة العمرية", "الكفاية", "إلمام أم استخدام أداة"]):
            if not ok:
                notes.append(f"{lid}: {what}")
    return got, total, notes


# ---------------------------------------------------------------- 1.2 the kite cards
def kite_rules() -> list[dict]:
    """Every rule of the form 'a kite flies when <attribute> is <value>', with its score on both sets."""
    rows = read_csv(FILES / "kite_cards.csv")
    train = [r for r in rows if col(r, 1) == "تدريب"]
    test = [r for r in rows if col(r, 1) == "اختبار"]
    truth = KEY["kites"]["test"]
    names = list(rows[0].keys())
    out = []
    for a in (2, 3, 4, 5):
        for value in sorted({col(r, a) for r in rows}):
            fit = sum((col(r, a) == value) == (col(r, 6) == "تطير") for r in train)
            hit = sum((col(r, a) == value) == (truth[col(r, 0)] == "تطير") for r in test)
            out.append({"rule": f"{names[a]} = {value}", "train": fit, "test": hit})
    return sorted(out, key=lambda r: (-r["train"], -r["test"], r["rule"]))


# ---------------------------------------------------------------- 1.3 the signs pack
FEATURES = ["mean_r", "mean_g", "mean_b", "top_to_bottom_width"]


def signs_rows() -> list[dict]:
    return read_csv(FILES / "signs_features.csv")


def train_centroids(rows: list[dict], train_set: str) -> dict:
    """A nearest-centroid classifier on standardised features: small enough to follow by hand.
    It is a stand-in written for this course, not the classifier of any browser tool."""
    tr = [r for r in rows if r["set"] == train_set]
    mean = {f: sum(float(r[f]) for r in tr) / len(tr) for f in FEATURES}
    std = {f: (sum((float(r[f]) - mean[f]) ** 2 for r in tr) / len(tr)) ** 0.5 or 1.0 for f in FEATURES}
    cents = {}
    for label in sorted({r["label"] for r in tr}):
        mine = [r for r in tr if r["label"] == label]
        cents[label] = {f: sum((float(r[f]) - mean[f]) / std[f] for r in mine) / len(mine) for f in FEATURES}
    return {"mean": mean, "std": std, "centroids": cents}


def predict(model: dict, row: dict) -> str:
    z = {f: (float(row[f]) - model["mean"][f]) / model["std"][f] for f in FEATURES}
    return min(model["centroids"], key=lambda lab: sum((z[f] - model["centroids"][lab][f]) ** 2 for f in FEATURES))


def accuracy(model: dict, rows: list[dict], test_set: str) -> tuple[int, int]:
    te = [r for r in rows if r["set"] == test_set]
    return sum(predict(model, r) == r["label"] for r in te), len(te)


def pack_counts() -> dict:
    with zipfile.ZipFile(FILES / "signs_pack.zip") as z:
        names = [n for n in z.namelist() if n.endswith(".png")]
        bad = z.testzip()
    counts: dict[str, int] = {}
    for n in names:
        counts[n.split("/")[0]] = counts.get(n.split("/")[0], 0) + 1
    return {"counts": counts, "corrupt": bad}


# ---------------------------------------------------------------- 2.1 the ten answers
def score_fact_check(path: Path) -> tuple[int, int, list[str]]:
    """A point for each verdict (10) and a point for the kind of each flawed answer (5)."""
    got, notes = 0, []
    for row in read_csv(path):
        n = col(row, 0)
        if n not in KEY["fact_check"]:
            continue
        k = KEY["fact_check"][n]
        verdict = col(row, 1)
        if (verdict == "سليمة") == k["sound"] and verdict in ("سليمة", "معيبة"):
            got += 1
        else:
            notes.append(f"السؤال {n}: الحكم")
        if not k["sound"]:
            if col(row, 2).replace("ـ", "") == k["kind"].replace("ـ", ""):
                got += 1
            else:
                notes.append(f"السؤال {n}: نوع الخطأ")
    return got, 15, notes


def recheck_siraj() -> dict:
    """Recomputes, independently of the key, the three answers that arithmetic can settle."""
    return {"q1": round(240 * 15 / 100), "q5_factors": [d for d in range(2, 91) if 91 % d == 0], "q7": 13}


# ---------------------------------------------------------------- 2.2 bias and media
def gallery_tally() -> dict:
    out: dict[str, dict] = {}
    for r in read_csv(FILES / "image_gallery_tally.csv"):
        t = out.setdefault(col(r, 1), {"رجل": 0, "امرأة": 0})
        t[col(r, 2)] += 1
    return out


def score_simple(path: Path, key: dict, field: str | None = None) -> tuple[int, int, list[str]]:
    got, notes = 0, []
    for row in read_csv(path):
        k = key.get(col(row, 0))
        if k is None:
            continue
        want = k[field] if field else k
        if col(row, 1) == want:
            got += 1
        else:
            notes.append(f"{col(row, 0)}: المرجع «{want}»")
    return got, len(key), notes


# ---------------------------------------------------------------- 2.3 the lesson plan
PLAN_FIELDS = ["المادة", "الصف", "الفئة العمرية", "هدف المادة", "هدف الإلمام بالذكاء الاصطناعي", "الكفاءة",
               "النشاط", "فئة الاستخدام", "اختبار الفهم دون ذكاء اصطناعي", "حماية الطلاب", "الإفصاح للأسر"]
VAGUE = ("تفهم", "يفهم", "تعرف", "يعرف", "تدرك", "يدرك", "تلمّ", "يلمّ", "تعي", "يعي")
STARTS = {"D1.1": 3, "D1.2": 3, "D1.3": 3, "D1.4": 9, "D1.5": 9, "D2.1": 6, "D2.2": 9, "D2.3": 9, "D2.4": 12,
          "D3.1": 12, "D3.2": 9, "D3.3": 15, "D3.4": 9, "D4.1": 9, "D4.2": 3, "D4.3": 6, "D4.4": 15,
          "D5.1": 9, "D5.2": 3, "D5.3": 12, "D5.4": 9, "D5.5": 9}


def check_plan(path: Path) -> list[str]:
    """Returns the defects of a lesson plan written on the template. An empty list is a pass.
    It reads form, not teaching quality: the cross-subject peer review does that."""
    values = {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        for f in PLAN_FIELDS:
            if line.startswith(f + ":"):
                values[f] = line[len(f) + 1:].strip()
    bad = [f"حقل فارغ: {f}" for f in PLAN_FIELDS if not values.get(f)]
    band = values.get("الفئة العمرية", "")
    if band and band not in ("6-8", "9-11", "12-14", "15-18"):
        bad.append("الفئة العمرية ليست بإحدى الصيغ الأربع")
    code = re.search(r"D\d\.\d", values.get("الكفاءة", ""))
    if values.get("الكفاءة") and not code:
        bad.append("الكفاءة بلا رمز من الإطار الوطني")
    use = re.findall(r"AI-[0-4]", values.get("فئة الاستخدام", ""))
    if values.get("فئة الاستخدام") and not use:
        bad.append("فئة الاستخدام بلا رمز من AI-0 إلى AI-4")
    if band == "6-8" and any(u != "AI-0" for u in use):
        bad.append("من 6 إلى 8 سنوات يبقى عمل الطالب المقيَّم AI-0")
    goal = values.get("هدف الإلمام بالذكاء الاصطناعي", "")
    if goal and goal.split()[0] in VAGUE:
        bad.append("هدف الإلمام يبدأ بفعل لا يُلاحَظ")
    if code and band in ("6-8", "9-11", "12-14", "15-18"):
        # the first age at which the national framework states a descriptor for the competency
        if STARTS.get(code.group(), 3) > int(band.split("-")[1]):
            bad.append(f"الكفاية {code.group()} لا تبدأ في هذه الفئة العمرية")
    check = values.get("اختبار الفهم دون ذكاء اصطناعي", "")
    if check and len(check.split()) < 8:
        bad.append("اختبار الفهم أقصر من أن يُنفَّذ")
    whole = " ".join(values.values())
    if re.search(r"\d{9,}", whole) or "@" in whole:
        bad.append("في الخطة رقم أو عنوان قد يدل على شخص")
    if re.search(r"الطالبة? [^\s،.]+ ال[^\s،.]+ \d", whole):
        bad.append("في الخطة اسم طالب")
    return bad


# ---------------------------------------------------------------- 3.2 the letter
JARGON = ["خوارزمي", "نموذج لغوي", "النماذج اللغوية", "تعلم الآلة", "بيانات التدريب", "مصنِّف", "التحول الرقمي"]
FALSE_PROMISES = ["لا تخطئ", "آمنة تمامًا", "آمن تمامًا", "تنشئ كل طالبة حسابًا", "ينشئ كل طالب حسابًا",
                  "تصحيح أعمال الطالبات ووضع", "تسأل الطالبة أي روبوت", "يسأل الطالب أي روبوت"]


def letter_stats(text: str) -> dict:
    body = [ln for ln in text.splitlines() if ln.strip()]
    sentences = [s.strip() for ln in body for s in re.split(r"[.؟!:]", ln) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    return {"words": sum(lengths), "longest": max(lengths), "sentences": len(sentences)}


def check_letter(path: Path) -> list[str]:
    """Returns the defects of a letter to families. An empty list is a pass. Readability is counted;
    accuracy is checked only against the promises this course knows to be wrong: a person reads the rest."""
    text = Path(path).read_text(encoding="utf-8-sig")
    if text.startswith("مسودة كتبها"):
        text = text.split("\n", 2)[2]
    s = letter_stats(text)
    bad = []
    if s["words"] > 200:
        bad.append(f"طويلة: {s['words']} كلمة")
    if s["longest"] > 25:
        bad.append(f"فيها جملة من {s['longest']} كلمة")
    found = [j for j in JARGON if j in text]
    if found:
        bad.append("مصطلحات بلا شرح: " + "، ".join(found))
    wrong = [p for p in FALSE_PROMISES if p in text]
    if wrong:
        bad.append("وعود تخالف القواعد أو الخطة: " + "، ".join(wrong))
    if not re.search(r"لا (تفتح|يفتح|يدخل|تدخل|يصحح|نستخدم)|لن ", text):
        bad.append("لا تذكر ما لا يُستخدم فيه الذكاء الاصطناعي")
    if not re.search(r"لا يشترط|دون (أداة|إنترنت)|بالقلم", text):
        bad.append("الواجب بلا مسار دون أداة")
    if "الموجهة الطلابية" not in text and "الموجه الطلابي" not in text:
        bad.append("لا تذكر لمن تتوجه الأسرة بما يقلقها")
    if "بمساعدة" in text and not re.search(r"راجعت|مسؤول", text):
        bad.append("تفصح عن المساعدة ولا تقول من راجع ومن المسؤول")
    if "بمساعدة" not in text:
        bad.append("لا تفصح عن صياغتها بمساعدة ذكاء اصطناعي (احذف هذا البند إن كتبتها وحدك)")
    return bad

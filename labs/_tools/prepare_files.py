# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Writes the synthetic file pack of USE-EDU-203 (Al-Sana Schools Complex, the assistant Yaraa).

Run from the course root:  uv run labs/_tools/prepare_files.py
Standard library only, a fixed seed, the same output on every run. Everything is invented.
It writes labs/files/ (what a participant starts from) and the reference files of labs/solutions/.
"""
from __future__ import annotations

import csv
import io
import json
import random
import struct
import sys
import zipfile
import zlib
from pathlib import Path

SEED = 203
LABS = Path(__file__).resolve().parent.parent
FILES = LABS / "files"
SOL = LABS / "solutions"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import pack_text as T  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def write_csv(path: Path, rows: list[list]) -> None:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("﻿" + buf.getvalue()).encode("utf-8"))


# ------------------------------------------------------------------ lab 1.1: the map

def lessons_and_map() -> dict:
    lines = ["دروس مجمّع مدارس السَّنا لأسبوع الإلمام بالذكاء الاصطناعي",
             "أربعة دروس اقترحتها المعلمات. اربط كل درس في ورقة الخريطة. الدرس د1 محلول.", ""]
    for le in T.LESSONS:
        lines += [f"{le['id']} · {le['grade']} · {le['subject']} · {le['teacher']}", f"   {le['text']}", ""]
    write(FILES / "sana_lessons.txt", "\n".join(lines))
    head = ["الدرس", "الفئة العمرية", "كفاية من الإطار الوطني (الرمز)", "مجال AILit", "إلمام أم استخدام أداة", "السبب في جملة"]
    first = T.LESSONS[0]
    blank = [head, [first["id"], first["band"], first["codes"][0], first["ailit"], first["literacy"], first["why"]]]
    blank += [[le["id"], "", "", "", "", ""] for le in T.LESSONS[1:]]
    blank += [["درسي", "", "", "", "", ""]]
    write_csv(FILES / "competence_map.csv", blank)
    ref = [head] + [[le["id"], le["band"], " أو ".join(le["codes"]), le["ailit"], le["literacy"], le["why"]] for le in T.LESSONS]
    write_csv(SOL / "competence_map_reference.csv", ref)
    return {le["id"]: {"band": le["band"], "codes": le["codes"], "literacy": le["literacy"], "ailit": le["ailit"]}
            for le in T.LESSONS}


# ------------------------------------------------------------------ lab 1.2: kite cards

COLOURS = {"أحمر": "#d64545", "أزرق": "#2f6fd0", "أصفر": "#e8b923"}


def kite_cards() -> dict:
    """The true rule: a kite flies when it has a tail. In the training cards every kite with a tail is red."""
    rng = random.Random(SEED)
    train = []
    for i in range(6):   # fly: red with a tail
        train.append(dict(colour="أحمر", shape=["معيّن", "مثلث"][i % 2], tail="نعم", stripes=["نعم", "لا"][(i // 2) % 2], flies="تطير"))
    for i in range(6):   # do not fly: blue or yellow, no tail
        train.append(dict(colour=["أزرق", "أصفر"][i % 2], shape=["معيّن", "مثلث"][(i // 2) % 2], tail="لا", stripes=["نعم", "لا"][i % 2 if i < 4 else 1 - i % 2], flies="لا تطير"))
    rng.shuffle(train)
    test = [dict(colour="أحمر", shape="معيّن", tail="نعم", stripes="لا", flies="تطير"),
            dict(colour="أزرق", shape="مثلث", tail="نعم", stripes="نعم", flies="تطير"),
            dict(colour="أحمر", shape="مثلث", tail="لا", stripes="نعم", flies="لا تطير"),
            dict(colour="أصفر", shape="معيّن", tail="نعم", stripes="لا", flies="تطير"),
            dict(colour="أحمر", shape="معيّن", tail="لا", stripes="لا", flies="لا تطير"),
            dict(colour="أزرق", shape="معيّن", tail="لا", stripes="نعم", flies="لا تطير")]
    for n, c in enumerate(train, 1):
        c["id"] = f"ت{n}"
    for n, c in enumerate(test, 1):
        c["id"] = f"خ{n}"
    head = ["البطاقة", "المجموعة", "اللون", "الشكل", "الذيل", "الخطوط", "النتيجة"]
    rows = [head] + [[c["id"], "تدريب", c["colour"], c["shape"], c["tail"], c["stripes"], c["flies"]] for c in train]
    rows += [[c["id"], "اختبار", c["colour"], c["shape"], c["tail"], c["stripes"], ""] for c in test]
    write_csv(FILES / "kite_cards.csv", rows)
    write(FILES / "kite_cards_train.svg", kite_sheet(train, True, "بطاقات التدريب"))
    write(FILES / "kite_cards_test.svg", kite_sheet(test, False, "بطاقات الاختبار"))
    write(FILES / "kite_game_script.txt", T.KITE_SCRIPT)
    write(FILES / "observation_notes.txt", T.OBSERVATION_NOTES)
    return {"train": train, "test": test}


def kite_sheet(cards: list[dict], labelled: bool, title: str) -> str:
    cols = 4 if len(cards) > 6 else 3
    rows = (len(cards) + cols - 1) // cols
    cw, ch = 250, 330
    w, h = cols * cw + 40, rows * ch + 90
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="sans-serif">',
           f'<title>{title}: {len(cards)} بطاقة طائرات ورقية</title>',
           f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
           f'<text x="{w / 2}" y="44" text-anchor="middle" font-size="30" font-weight="bold" fill="#1b2a41">{title}</text>']
    for i, c in enumerate(cards):
        x = 20 + (cols - 1 - i % cols) * cw      # right to left
        y = 70 + (i // cols) * ch
        cx, top = x + cw / 2, y + 50
        fill = COLOURS[c["colour"]]
        out.append(f'<rect x="{x + 8}" y="{y + 8}" width="{cw - 16}" height="{ch - 16}" rx="14" fill="#f7f5ef" stroke="#1b2a41" stroke-width="2"/>')
        out.append(f'<text x="{x + cw - 28}" y="{y + 42}" text-anchor="end" font-size="24" font-weight="bold" fill="#1b2a41">{c["id"]}</text>')
        if c["shape"] == "معيّن":
            pts = [(cx, top), (cx + 62, top + 75), (cx, top + 150), (cx - 62, top + 75)]
            stripes = [((cx - 31, top + 37), (cx + 31, top + 37)), ((cx - 62, top + 75), (cx + 62, top + 75)), ((cx - 31, top + 112), (cx + 31, top + 112))]
        else:
            pts = [(cx, top), (cx + 70, top + 150), (cx - 70, top + 150)]
            stripes = [((cx - 23, top + 50), (cx + 23, top + 50)), ((cx - 47, top + 100), (cx + 47, top + 100))]
        out.append('<polygon points="' + " ".join(f"{px:.0f},{py:.0f}" for px, py in pts) + f'" fill="{fill}" stroke="#1b2a41" stroke-width="3"/>')
        if c["stripes"] == "نعم":
            for (a, b), (d, e) in stripes:
                out.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{d:.0f}" y2="{e:.0f}" stroke="#ffffff" stroke-width="7"/>')
        if c["tail"] == "نعم":
            ty = top + 150
            out.append(f'<path d="M {cx:.0f} {ty} q 22 18 0 36 q -22 18 0 36" fill="none" stroke="#1b2a41" stroke-width="3"/>')
            for k in (18, 54):
                out.append(f'<polygon points="{cx - 12:.0f},{ty + k - 7} {cx + 12:.0f},{ty + k + 7} {cx + 12:.0f},{ty + k - 7} {cx - 12:.0f},{ty + k + 7}" fill="#1b2a41"/>')
        if labelled:
            good = c["flies"] == "تطير"
            out.append(f'<text x="{cx:.0f}" y="{y + ch - 30}" text-anchor="middle" font-size="26" font-weight="bold" fill="{"#0f7b6c" if good else "#b23a3a"}">{c["flies"]}</text>')
        else:
            out.append(f'<text x="{cx:.0f}" y="{y + ch - 30}" text-anchor="middle" font-size="26" font-weight="bold" fill="#6b7280">؟</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ lab 1.3: the signs pack

SIZE = 96
SKY, SAND = (135, 190, 235), (235, 205, 130)


def png(pixels: list[list[tuple[int, int, int]]]) -> bytes:
    h, w = len(pixels), len(pixels[0])
    raw = b"".join(b"\x00" + bytes(v for px in row for v in px) for row in pixels)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def sign(rng: random.Random, shape: str, bg: tuple[int, int, int]) -> list[list[tuple[int, int, int]]]:
    """A road-sign drawing: a white shape with a red border on a plain background.
    shape: circle, triangle (point up), square or triangle_down (the last two only in the 'new' set)."""
    d = rng.randint(-10, 10)
    bg = tuple(max(0, min(255, v + d + rng.randint(-4, 4))) for v in bg)
    r = rng.randint(26, 34)
    cx, cy = rng.randint(r + 6, SIZE - r - 6), rng.randint(r + 6, SIZE - r - 6)
    red, white = (200, 40, 40), (250, 250, 250)

    def inside(x: float, y: float, k: float) -> bool:
        rr = r * k
        dx, dy = x - cx, y - cy
        if shape == "circle":
            return dx * dx + dy * dy <= rr * rr
        if shape == "square":
            return abs(dx) <= rr * 0.85 and abs(dy) <= rr * 0.85
        if shape == "triangle_down":
            dy = -dy
        t = (dy + rr) / (2 * rr)            # 0 at the apex, 1 at the base
        return 0 <= t <= 1 and abs(dx) <= rr * t
    rows = []
    for y in range(SIZE):
        row = []
        for x in range(SIZE):
            row.append(white if inside(x, y, 0.72) else red if inside(x, y, 1.0) else bg)
        rows.append(row)
    return rows


def features(pixels: list[list[tuple[int, int, int]]]) -> dict:
    """What the transparent stand-in classifier sees: the mean colour of the whole picture, and how wide the
    sign is near its top compared with near its bottom (about 1 for a circle, well under 1 for a triangle)."""
    n = SIZE * SIZE
    mr = sum(px[0] for row in pixels for px in row) / n
    mg = sum(px[1] for row in pixels for px in row) / n
    mb = sum(px[2] for row in pixels for px in row) / n
    bg = pixels[0][0]

    def is_sign(px: tuple[int, int, int]) -> bool:
        return sum(abs(px[i] - bg[i]) for i in range(3)) > 90
    widths = [sum(1 for px in row if is_sign(px)) for row in pixels]
    ys = [y for y, wd in enumerate(widths) if wd]
    top, bottom = ys[0], ys[-1]
    q1 = widths[top + (bottom - top) // 4]
    q3 = widths[top + 3 * (bottom - top) // 4]
    return {"mean_r": round(mr, 1), "mean_g": round(mg, 1), "mean_b": round(mb, 1), "top_to_bottom_width": round(q1 / q3, 2)}


def signs_pack() -> None:
    rng = random.Random(SEED + 13)
    plan = [("train", "circle", [SKY] * 20), ("train", "triangle", [SAND] * 20),
            ("test_same", "circle", [SKY] * 10), ("test_same", "triangle", [SAND] * 10),
            ("test_shifted", "circle", [SAND] * 10), ("test_shifted", "triangle", [SKY] * 10),
            ("train_mixed", "circle", [SKY, SAND] * 10), ("train_mixed", "triangle", [SKY, SAND] * 10),
            ("test_new", "square", [SKY, SAND, SKY]), ("test_new", "triangle_down", [SAND, SKY, SAND])]
    rows = [["file", "set", "label", "mean_r", "mean_g", "mean_b", "top_to_bottom_width"]]
    buf = io.BytesIO()
    preview: dict[tuple[str, str], list] = {}
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for folder, shape, bgs in plan:
            for i, bg in enumerate(bgs, 1):
                px = sign(rng, shape, bg)
                name = f"{folder}/{shape}/{shape}_{i:02d}.png"
                info = zipfile.ZipInfo(name, date_time=(2027, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, png(px), compresslevel=9)
                f = features(px)
                rows.append([name, folder, shape, f["mean_r"], f["mean_g"], f["mean_b"], f["top_to_bottom_width"]])
                preview.setdefault((folder, shape), []).append(px)
    FILES.mkdir(parents=True, exist_ok=True)
    (FILES / "signs_pack.zip").write_bytes(buf.getvalue())
    write_csv(FILES / "signs_features.csv", rows)
    # A contact sheet: three pictures of each class of the three sets a participant compares
    order = [("train", "circle"), ("train", "triangle"), ("test_same", "circle"), ("test_same", "triangle"),
             ("test_shifted", "circle"), ("test_shifted", "triangle")]
    gap, per = 8, 3
    w = gap + len(order) * per * (SIZE + gap) + 2 * gap * 2
    sheet = [[(255, 255, 255)] * w for _ in range(SIZE + 2 * gap)]
    x0 = gap
    for n, key in enumerate(order):
        for px in preview[key][:per]:
            for y in range(SIZE):
                sheet[gap + y][x0:x0 + SIZE] = px[y]
            x0 += SIZE + gap
        if n % 2 == 1:
            x0 += 2 * gap
    (FILES / "signs_preview.png").write_bytes(png(sheet))


# ------------------------------------------------------------------ lab 2.1: Yaraa's ten answers

def fact_check() -> dict:
    lines = ["إجابات المساعد «يَراع» عن عشرة أسئلة في المواد",
             "سجل مكتوب للمقرر: «يَراع» هنا نموذج بديل مكتوب وليس نموذجًا لغويًّا، وفي إجاباته أخطاء مزروعة عمدًا.",
             "تحقق من كل إجابة ببطاقة المصادر، لا بمساعد آخر.", ""]
    for n, subject, q, a, _ok, _kind, _ev in T.SIRAJ:
        lines += [f"السؤال {n} ({subject})", f"المعلمة: {q}", f"يَراع: {a}", ""]
    write(FILES / "yaraa_answers.txt", "\n".join(lines))
    write(FILES / "source_card.txt", T.SOURCE_CARD)
    write(FILES / "error_kinds.txt", T.FACT_KINDS)
    head = ["السؤال", "الحكم (سليمة أو معيبة)", "نوع الخطأ (أ ب ج د هـ)", "الدليل"]
    write_csv(FILES / "fact_check_sheet.csv", [head] + [[n, "", "", ""] for n in range(1, 11)])
    write_csv(FILES / "own_questions_sheet.csv",
              [["السؤال من مادتي", "إجابة الكتاب والصفحة", "إجابة المساعد في سطر", "الحكم", "نوع الخطأ", "الدليل"]] + [["", "", "", "", "", ""] for _ in range(10)])
    write_csv(SOL / "fact_check_reference.csv",
              [head] + [[n, "سليمة" if ok else "معيبة", kind, ev] for n, _s, _q, _a, ok, kind, ev in T.SIRAJ])
    return {str(n): {"sound": ok, "kind": kind} for n, _s, _q, _a, ok, kind, _ev in T.SIRAJ}


# ------------------------------------------------------------------ lab 2.2: bias and media

GALLERY = [("طبيب", 17), ("تمريض", 2), ("مهندس", 19), ("تدريس", 9)]   # prompt word, pictures that show a man, of 20


def bias_and_media() -> dict:
    rng = random.Random(SEED + 22)
    rows = [["رقم الصورة", "الأمر المكتوب", "من يظهر في الصورة"]]
    n = 0
    tally = {}
    prompts = {"طبيب": "صورة لمن يعمل في الطب", "تمريض": "صورة لمن يعمل في التمريض",
               "مهندس": "صورة لمن يعمل في الهندسة", "تدريس": "صورة لمن يعمل في التدريس"}
    for word, men in GALLERY:
        shown = ["رجل"] * men + ["امرأة"] * (20 - men)
        rng.shuffle(shown)
        for s in shown:
            n += 1
            rows.append([n, prompts[word], s])
        tally[word] = {"men": men, "women": 20 - men, "share_men": men * 5}
    write_csv(FILES / "image_gallery_tally.csv", rows)
    write(FILES / "image_gallery_readme.txt",
          "جدول الصور المولّدة\n"
          "ثمانون صورة: عشرون لكل أمر من أربعة أوامر لا تذكر جنسًا ولا عمرًا. الجدول يصف من يظهر في كل صورة.\n"
          "الجدول مكتوب للمقرر: نموذج بديل لمولّد صور، والانحياز فيه مزروع عمدًا. لا صورة لأي شخص في ملفات المقرر.\n"
          "المطلوب: عُدَّ لكل أمر كم صورة تُظهر رجلًا وكم تُظهر امرأة، واحسب النسبة، وقارنها بنصف ونصف.\n")
    lines = ["حالات الوسائط الأربع", "كل الحالات موصوفة نصًّا ومن مجمّع مدارس السَّنا الافتراضي.",
             "لكل حالة اختر: «المصدر الرسمي» أو «المصدر والإفصاح» أو «حماية: بلّغ»، واكتب خطوتك الأولى.", ""]
    for cid, text, _d, _w in T.MEDIA_CASES:
        lines += [f"الحالة {cid}", f"   {text}", ""]
    write(FILES / "media_cases.txt", "\n".join(lines))
    write_csv(FILES / "media_sheet.csv", [["الحالة", "القرار", "الخطوة الأولى"]] + [[c[0], "", ""] for c in T.MEDIA_CASES])
    write_csv(SOL / "media_reference.csv", [["الحالة", "القرار", "السبب"]] + [[c[0], c[2], c[3]] for c in T.MEDIA_CASES])
    return {"tally": tally, "media": {c[0]: c[2] for c in T.MEDIA_CASES}}


# ------------------------------------------------------------------ lab 2.3: the lesson plan

def plan_text(values: dict, title: str) -> str:
    return title + "\n" + "\n".join(f"{k}: {values.get(k, '')}".rstrip() for k in T.PLAN_FIELDS) + "\n"


def lesson_plan() -> None:
    write(FILES / "lesson_plan_template.txt", T.PLAN_TEMPLATE_HEAD + "\n" + "\n".join(f"{k}:" for k in T.PLAN_FIELDS) + "\n")
    write(FILES / "lesson_plan_example.txt", plan_text(T.PLAN_EXAMPLE, "خطة محلولة · ميمونة الخضيري · مجمّع مدارس السَّنا"))
    write(FILES / "lesson_plan_flawed.txt", plan_text(T.PLAN_FLAWED, "خطة معيبة للتدرب على المراجعة · كل ما فيها مخترع، والاسم والرقم مزروعان عمدًا"))
    write(FILES / "peer_review_form.txt", T.PEER_REVIEW)


# ------------------------------------------------------------------ lab 3.1: the clinic

def clinic() -> dict:
    write(FILES / "sana_ai_rules.txt", T.RULES)
    write_csv(FILES / "approved_tools.csv",
              [["الأداة", "النوع", "من يستخدمها", "الصفوف", "الحسابات", "البيانات"]] + [list(t) for t in T.TOOLS])
    lines = ["عيادة حماية الطلاب · ستة مواقف من مجمّع مدارس السَّنا",
             "لكل موقف قرار واحد من أربعة: " + " · ".join(T.DECISIONS) + ".",
             "اكتب القاعدة التي استندت إليها (ق1 إلى ق8). تؤدَّى دون ذكاء اصطناعي.", ""]
    for sid, text, _d, _r, _w in T.SCENARIOS:
        lines += [sid, f"   {text}", ""]
    write(FILES / "clinic_scenarios.txt", "\n".join(lines))
    write_csv(FILES / "clinic_sheet.csv", [["الموقف", "القرار", "القاعدة", "الشرط أو البديل"]] + [[s[0], "", "", ""] for s in T.SCENARIOS])
    write_csv(SOL / "clinic_reference.csv", [["الموقف", "القرار", "القاعدة", "السبب والبديل"]] + [[s[0], s[2], s[3], s[4]] for s in T.SCENARIOS])
    return {s[0]: {"decision": s[2], "rules": s[3]} for s in T.SCENARIOS}


# ------------------------------------------------------------------ lab 3.2 and the trial lesson

def letter_and_trial() -> None:
    write(FILES / "letter_brief.txt", T.LETTER_BRIEF)
    write(FILES / "letter_draft_yaraa.txt",
          "مسودة كتبها «يَراع» (نموذج بديل مكتوب للمقرر، وفيها خمسة أخطاء مزروعة). لا تُرسل كما هي.\n\n" + T.LETTER_DRAFT)
    write(FILES / "letter_checklist.txt", T.LETTER_CHECKLIST)
    write(SOL / "letter_reference.txt", T.LETTER_REFERENCE)
    write(FILES / "trial_lesson_notes_template.txt", T.TRIAL_NOTES)
    write(FILES / "revised_plan_template.txt", T.REVISED_PLAN)
    write(FILES / "prework_guide.txt", T.PREWORK)
    write(FILES / "framework_cards.txt", T.FRAMEWORK_CARDS)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    key = {"seed": SEED, "map": lessons_and_map()}
    kites = kite_cards()
    key["kites"] = {"true_rule": "الذيل", "trap_rule": "اللون الأحمر",
                    "test": {c["id"]: c["flies"] for c in kites["test"]}}
    signs_pack()
    key["fact_check"] = fact_check()
    key.update(bias_and_media())
    lesson_plan()
    key["clinic"] = clinic()
    letter_and_trial()
    write(SOL / "key.json", json.dumps(key, ensure_ascii=False, indent=1) + "\n")
    print("files:", len([p for p in FILES.rglob("*") if p.is_file()]), "in labs/files")


if __name__ == "__main__":
    main()

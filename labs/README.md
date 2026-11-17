# الإلمام بالذكاء الاصطناعي لمعلمي المدارس: المختبرات

ثمانية مختبرات لمقرر أكاديمية سدايا **USE-EDU-203**. المختبرات صفحات إرشادية بالعربية: الهدف، والملفات، وخطوات
بدقائقها، وأسئلة تحقق، ومهمة إضافية ✱، وملاحظات للمدرب. لا كود يكتبه المشارك.

كل المختبرات في جهة واحدة: **مجمّع مدارس السَّنا**، مجمّع افتراضي، ومساعده «يَراع». كل الأسماء والدروس والبطاقات
والصور والمواقف مخترعة. «يَراع» في الملفات نموذج بديل مكتوب، وليس نموذجًا لغويًّا.

## ما يحتاجه المشارك

- متصفح. وللمختبر 1.3 أداة لتدريب مصنِّف صور تعمل في المتصفح دون حسابات، أو Orange Data Mining.
- للمختبرات 2.1 و2.3 و3.2: مساعد ذكاء اصطناعي معتمد من جهته التعليمية. من لا مساعد لديه يعمل على السجلات الجاهزة.
- ما أعده في العمل التحضيري (`files/prework_guide.txt`): درس من مادته، وعشرة أسئلة بإجابات الكتاب، وقواعد مدرسته.
- ورق وأقلام، وبطاقات المختبر 1.2 مطبوعة إن أمكن.
- لا يُنزَّل أي نموذج على الجهاز. ولا يدخل أي أداة اسم طالب ولا بيان عنه.

## سياسة الذكاء الاصطناعي

| المستوى | أين |
|---|---|
| دون ذكاء اصطناعي | المختبرات 1.1 و1.2 و2.2 و3.1 كلها، والخطوتان 1 و2 من المختبر 2.1 |
| ذكاء اصطناعي مرشد | الخطوة 2 من المختبر 2.3: المساعد يسأل ويقترح، والمعلم يكتب |
| استخدام مفتوح | الخطوة 3 من المختبر 2.1 (طرح الأسئلة)، والمختبر 3.2 (الرسالة، ويتحقق منها المعلم ويتحمل مسؤوليتها) |

المختبر 1.3 تدريب مصنِّف: الأداة فيه موضوع النشاط نفسه.

## نقطة البداية والحل

كل مختبر يبدأ من ملفات جاهزة ولا يعتمد على مختبر آخر. المختبر 2.3 يبدأ من صف «درسي» في خريطة 1.1، وبديله
الخطة المحلولة. والمختبر 3.2 يبدأ من خطة 2.3، وبديله خطة المجمّع ومسودة «يَراع».

| المختبر | الصفحة | المدة | يبدأ من | الحل المرجعي |
|---|---|---|---|---|
| 1.1 | `D1_1_competence_map.html` | 25 دقيقة | `files/framework_cards.txt`، `files/sana_lessons.txt`، `files/competence_map.csv` | `solutions/competence_map_reference.csv` |
| 1.2 | `D1_2_unplugged_sorting.html` | 30 دقيقة | `files/kite_cards_train.svg`، `files/kite_cards_test.svg`، `files/kite_game_script.txt`، `files/observation_notes.txt` | `solutions/answer_key.md` |
| 1.3 | `D1_3_train_break_classifier.html` | 35 دقيقة | `files/signs_pack.zip`، `files/signs_preview.png`، `files/signs_features.csv` | `solutions/labkit.py` (المصنِّف البديل)، `solutions/answer_key.md` |
| 2.1 | `D2_1_fact_check_chatbot.html` | 35 دقيقة | `files/yaraa_answers.txt`، `files/source_card.txt`، `files/error_kinds.txt`، `files/fact_check_sheet.csv` | `solutions/fact_check_reference.csv` |
| 2.2 | `D2_2_bias_synthetic_media.html` | 25 دقيقة | `files/image_gallery_tally.csv`، `files/media_cases.txt`، `files/media_sheet.csv` | `solutions/media_reference.csv`، `solutions/answer_key.md` |
| 2.3 | `D2_3_lesson_plan.html` | 35 دقيقة | `files/lesson_plan_template.txt`، `files/lesson_plan_example.txt`، `files/lesson_plan_flawed.txt`، `files/peer_review_form.txt` | `files/lesson_plan_example.txt` (تجتاز الفاحص) |
| 3.1 | `D3_1_safeguarding_clinic.html` | 30 دقيقة | `files/sana_ai_rules.txt`، `files/approved_tools.csv`، `files/clinic_scenarios.txt`، `files/clinic_sheet.csv` | `solutions/clinic_reference.csv` |
| 3.2 | `D3_2_family_letter.html` | 25 دقيقة | `files/letter_brief.txt`، `files/letter_draft_yaraa.txt`، `files/letter_checklist.txt` | `solutions/letter_reference.txt` |

للدرس التجريبي بعد الورشة: `files/trial_lesson_notes_template.txt` و`files/revised_plan_template.txt`.

## للمدرب: المفتاح والأدوات

- `solutions/answer_key.md`: كل ما زُرع في الملفات، وأين، وأي مختبر يكشفه، والأرقام المنتظرة.
- `solutions/score.py`: يقيّم ورقة مشارك بالمفتاح (`map` و`facts` و`media` و`clinic`)، أو يطبع عيوب خطة أو رسالة
  (`plan` و`letter`).
- `solutions/labkit.py`: الفحوص نفسها، وفيها المصنِّف البديل الشفاف للمختبر 1.3 (أقرب مركز على أربعة أرقام لكل صورة).
- `solutions/run_all.py`: يشغّل كل ما سبق ويطبع PASS أو أول اختلاف.

الأدوات مكتوبة بمكتبة Python القياسية وحدها، وتُشغَّل بـ`uv` من جذر المستودع:

```
uv run labs/_tools/prepare_files.py
uv run labs/solutions/run_all.py
uv run labs/solutions/score.py clinic labs/solutions/clinic_reference.csv
uv run labs/solutions/score.py plan labs/files/lesson_plan_example.txt
```

الأول يعيد كتابة `files/` وملفات الحل المرجعية ببذرة ثابتة (203): المحتوى نفسه في كل تشغيل.

## ما لم يُشغَّل على نموذج أو أداة حقيقية

- المختبر 1.3: أرقام المرجع (20 من 20، ثم 0 من 20، ثم 20 من 20) من المصنِّف البديل في `labkit.py`، لا من أداة
  متصفح. جرّب حزمة الصور على الأداة التي ستستخدمها القاعة قبل أول دفعة وسجّل أرقامها الثلاثة.
- الخطوة 3 من المختبر 2.1، والخطوة 2 من 2.3، والخطوة 3 من 3.2 تُؤدى مع مساعد حي، وسلوك المساعدات يختلف من
  نموذج لآخر ومن شهر لآخر. إجابات «يَراع» ومسودته مكتوبة للمقرر.
- أعداد جدول الصور في المختبر 2.2 مزروعة، وليست قياسًا لأي مولّد صور.

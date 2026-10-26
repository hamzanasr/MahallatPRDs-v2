# -*- coding: utf-8 -*-
"""الجولة السادسة: توحيد المصطلحات وفق مسرد جلسة 26 أكتوبر 2026.

TERMS: سطر متطلب يُستبدل بنصه الكامل بعد تطبيق قرارات b4_decisions6؛ يفشل البناء إن لم يوجد السطر القديم كما هو.
PAGE_EDITS6: تعديل بيانات الصفحة في ملف المالك قبل دمج مراجعة الصفحات (ux/out وux/out2):
(الصفحة, المفتاح title|purpose|actions|fields|states, القديم, الجديد أو None للحذف).
القوائم مقسّمة على ملفات b4_terms6_*.py بحسب الوحدة أو الواجهة، وتُجمع هنا.
"""
import glob, importlib, os

# (رقم القرار, المتطلب, السطر القديم كاملاً, السطر الجديد)
TERMS = []
PAGE_EDITS6 = []
for _f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'b4_terms6_*.py'))):
    _m = importlib.import_module(os.path.basename(_f)[:-3])
    TERMS.extend(getattr(_m, 'TERMS', []))
    PAGE_EDITS6.extend(getattr(_m, 'PAGE_EDITS6', []))

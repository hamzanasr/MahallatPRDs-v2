# -*- coding: utf-8 -*-
"""آخر الوثيقة: الأسئلة المفتوحة للمالك."""
import os, json
from b4_common import *


def _load(name):
    f = os.path.join(HERE, 'ux', name)
    return json.load(open(f, encoding='utf8')) if os.path.exists(f) else {}


def open_section(num):
    """ما بقي مفتوحاً للمالك."""
    R = _load('notes_review.json')
    opens = R.get('open', [])
    if opens:
        rows = [[str(i), fmt(q['q']), fmt(q.get('proposal', '')), refs_html(q.get('reqs', []))] for i, q in enumerate(opens, 1)]
        top = ('<p>أسئلة تحتاج قرار المالك. حتى يُحسم السؤال يُبنى المقترح.</p>' +
               tbl(['#', 'السؤال', 'المقترح', 'المتطلبات'], rows, 'tbl-notes'))
    else:
        top = '<p>لا يوجد سؤال مفتوح: حسم المالك كل المسائل.</p>'
    return ('<section id="open"><h2><span class="num">%d</span>أسئلة مفتوحة</h2>'
            '<p class="sub">قرارات المالك مكتوبة في المتطلبات نفسها.</p>'
            '<h3>أسئلة مفتوحة للمالك (%d)</h3>%s</section>') % (num, len(opens), top)

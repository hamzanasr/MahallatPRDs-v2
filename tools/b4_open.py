# -*- coding: utf-8 -*-
"""آخر الوثيقة: الأسئلة المفتوحة للمالك، وملاحظات تقنية للمبرمج."""
import os, json
from b4_common import *


def _load(name):
    f = os.path.join(HERE, 'ux', name)
    return json.load(open(f, encoding='utf8')) if os.path.exists(f) else {}


def _pages(ids):
    return ' '.join('<a href="#p-%s"><bdi class="rid">%s</bdi></a>' % (i, i) for i in ids if i in PAGES)


def open_section(num):
    """ما بقي مفتوحاً للمالك، وملاحظات تقنية يقررها المبرمج."""
    R = _load('notes_review.json')
    Q = _load('questions.json')
    opens = R.get('open', [])
    if opens:
        rows = [[str(i), fmt(q['q']), fmt(q.get('proposal', '')), refs_html(q.get('reqs', []))] for i, q in enumerate(opens, 1)]
        top = ('<p>أسئلة تحتاج قرار المالك. حتى يُحسم السؤال يُبنى المقترح.</p>' +
               tbl(['#', 'السؤال', 'المقترح', 'المتطلبات'], rows, 'tbl-notes'))
    else:
        top = '<p>لا يوجد سؤال مفتوح: حسم المالك كل المسائل.</p>'
    dev = [(n['note'], n.get('pages', []), n.get('reqs', [])) for n in Q.get('dev_notes', [])]
    dev += [(n['note'], [], n.get('reqs', [])) for n in R.get('dev', [])]
    dev_html = tbl(['الملاحظة', 'الصفحات والمتطلبات'], [[fmt(a), (_pages(b) + ' ' + refs_html(c)).strip()] for a, b, c in dev], 'tbl-notes') if dev else '<p>لا يوجد.</p>'
    return ('<section id="open"><h2><span class="num">%d</span>أسئلة وملاحظات</h2>'
            '<p class="sub">قرارات المالك مكتوبة في المتطلبات نفسها.</p>'
            '<h3>أسئلة مفتوحة للمالك (%d)</h3>%s<h3>ملاحظات تقنية للمبرمج (%d)</h3>'
            '<p>تفاصيل تقنية لا تحتاج قرار المالك، يقررها المبرمج ويوثّقها.</p>%s</section>') % (num, len(opens), top, len(dev), dev_html)

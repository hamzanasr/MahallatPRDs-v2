# -*- coding: utf-8 -*-
"""الأسئلة المفتوحة: ما بقي غير محسوم (ومن يحسمه وما يتعطل حتى يُحسم)، وما حُسم بتاريخه.

المصدر ux/notes_review.json: «open» (id, q, owner, blocks, reqs) و«settled» (id, decision, date).
يُعرض في آخر الموقع، وفي prd.md بعد «قبل التشغيل».
"""
import os, json
from b4_common import *

INTRO = 'ما بقي غير محسوم. لكل سؤال: ما ينتظره، ومن يحسمه، وما يتعطل حتى يُحسم. لا يُبرمج ما يعتمد على سؤال مفتوح قبل حسمه؛ والمتطلب الذي يحيل إلى هنا يذكر رقم السؤال.'
CLOSE = '**يُغلق السؤال** بتعديل المتطلب المعني ونقله إلى «محسوم» بالتاريخ ومن حسمه.'
OPEN_HEAD = ['الرقم', 'السؤال', 'يحسمه', 'يتعطل حتى يُحسم', 'المتطلبات']
SETTLED_HEAD = ['الرقم', 'القرار', 'بتاريخ']


def _load(name):
    f = os.path.join(HERE, 'ux', name)
    return json.load(open(f, encoding='utf8')) if os.path.exists(f) else {}


R = _load('notes_review.json')
OPEN = R.get('open', [])
SETTLED = R.get('settled', [])


def _bold(t):
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)


def open_section(num):
    """ما بقي مفتوحاً، وما حُسم."""
    if OPEN:
        rows = [['<b>%s</b>' % esc(q['id']), fmt(q['q']), fmt(q['owner']), fmt(q['blocks']), refs_html(q.get('reqs', []))] for q in OPEN]
        top = tbl(OPEN_HEAD, rows, 'tbl-notes')
    else:
        top = '<p>لا يوجد سؤال مفتوح: حسم المالك كل المسائل.</p>'
    done = tbl(SETTLED_HEAD, [['<b>%s</b>' % esc(q['id']), fmt(q['decision']), fmt(q['date'])] for q in SETTLED]) if SETTLED else ''
    return ('<section id="open"><h2><span class="num">%d</span>أسئلة مفتوحة</h2>'
            '<p class="sub">%s</p>'
            '<h3>مفتوح (%d)</h3>%s<h3>محسوم (%d)</h3>%s<p>%s</p></section>') % (
        num, fmt(INTRO), len(OPEN), top, len(SETTLED), done, _bold(fmt(CLOSE)))


def open_md():
    """القسم نفسه لـ prd.md."""
    L = ['## أسئلة مفتوحة', '', INTRO, '', '| ' + ' | '.join(OPEN_HEAD) + ' |', '|' + '---|' * len(OPEN_HEAD)]
    L += ['| %s | %s | %s | %s | %s |' % (q['id'], q['q'], q['owner'], q['blocks'], '، '.join(q.get('reqs', []))) for q in OPEN]
    L += ['', '### محسوم', '', '| ' + ' | '.join(SETTLED_HEAD) + ' |', '|' + '---|' * len(SETTLED_HEAD)]
    L += ['| %s | %s | %s |' % (q['id'], q['decision'], q['date']) for q in SETTLED]
    L += ['', CLOSE, '']
    return L

# -*- coding: utf-8 -*-
"""الواجهات: معاينات الصفحات + مواصفات كل صفحة + المخططات."""
import json, re, os
from bs4 import BeautifulSoup
from b4_common import *

PREV = json.load(open(os.path.join(HERE, 'previews_raw.json'), encoding='utf8'))

# ---------------------------------------------------------------- المعاينات
ICON_RE = re.compile(r'<svg class="([^"]*)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">(.*?)</svg>', re.S)
SPRITE = {}


def sprite_icon(m):
    inner = m.group(2)
    if inner not in SPRITE:
        SPRITE[inner] = 'i%d' % len(SPRITE)
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true"><use href="#%s"/></svg>' % (m.group(1), SPRITE[inner])


def clean_preview(h):
    h = ICON_RE.sub(sprite_icon, h)
    # المعاينة صورة توضيحية: بلا تفاعل ولا وصول لقارئ الشاشة (وصف الصفحة نصٌّ تحتها)
    h = re.sub(r' data-(page|back|diagram)(="[^"]*")?', '', h)
    h = h.replace('role="img" ', '')
    h = re.sub(r' aria-label="معاينة[^"]*"', '', h)
    h = re.sub(r'<input([^>]*?)\s*aria-label="[^"]*"', r'<input\1', h)
    h = re.sub(r' id="[^"]*"', '', h)
    return h


def sprite_defs():
    syms = ''.join('<symbol id="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">%s</symbol>' % (i, inner) for inner, i in SPRITE.items())
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>%s</defs></svg>' % syms


# ---------------------------------------------------------------- صفحة واحدة
def _mock_html(pid, html, cap):
    html = UXM.fix_sidebar(html, pid, D)
    return '<figure class="mock-fig"><div class="mock" aria-hidden="true" inert>%s</div><figcaption class="mock-cap">%s</figcaption></figure>' % (clean_preview(html), esc(cap))


def _block(title, items):
    if not items:
        return ''
    return '<div class="sc2"><h4><i></i>%s</h4><ul>%s</ul></div>' % (title, ''.join('<li>%s</li>' % fmt(x) for x in items))


def page_html(p, with_mock=True):
    pid = p['id']
    reqs = []
    for rid in p['refs']:
        r = REQ[rid]
        reqs.append('<li><a class="rid" href="#%s">%s</a> %s%s</li>' % (rid, rid, esc(r['title']), (' ' + tag(r['priority'])) if r['priority'] != 'launch' else ''))
    nxt = ' · '.join('<a href="#p-%s"><bdi class="rid">%s</bdi> %s</a>' % (l, l, esc(PAGES[l]['title'])) for l in p['links'])
    nxt_html = ('<div class="sc2"><h4><i></i>تنتقل إلى</h4><p>%s</p></div>' % nxt) if nxt else ''
    fields = ''.join('<li>%s</li>' % fmt(x) for x in p['fields'])
    if p.get('acts') and any(a.get('result') for a in p['acts']):
        acts = '<div class="sc2 wide"><h4><i></i>الإجراءات وما يحدث عند كل منها</h4>%s</div>' % tbl(
            ['الإجراء', 'ماذا يحدث'], [['<b>%s</b>' % esc(a['name']), fmt(a.get('result') or '—')] for a in p['acts']], 'tbl-acts')
    else:
        acts = '<div class="sc2"><h4><i></i>الإجراءات</h4><div class="chips">%s</div></div>' % ''.join('<span class="chip">%s</span>' % esc(x) for x in p['actions'])
    own = [s for s in p['states'] if s not in set(STD_STATES)]
    mock = ''
    if with_mock:
        m1 = UX_MOCKS.get(pid) or PREV.get(pid)
        figs = []
        if m1:
            figs.append(_mock_html(pid, m1, 'معاينة توضيحية لترتيب الصفحة؛ الأرقام والأسماء تجريبية.'))
        if pid in UX_MOCKS2:
            figs.append(_mock_html(pid, UX_MOCKS2[pid], p.get('mock2_caption') or 'حالة أخرى للصفحة نفسها.'))
        if figs:
            desk = 'mk desk' in (m1 or '')
            mock = '<div class="mock-wrap%s">%s</div>' % (' pair' if len(figs) > 1 and not desk else '', ''.join(figs))
    new_tag = ' <span class="tag p2">جديدة</span>' if p.get('new') else ''
    pri_tag = (' ' + tag(p['priority'])) if p.get('priority') and p['priority'] != 'launch' else ''
    return ('<details class="page" id="p-%s"><summary><span class="pn"><bdi class="rid">%s</bdi> %s%s%s</span><span class="ps">%s</span></summary>'
            '<div class="pbody">%s<div class="pspec">'
            '<div class="sc2 wide fields"><h4><i></i>عناصر الصفحة</h4><ul>%s</ul></div>'
            '%s%s%s%s%s'
            '<div class="sc2"><h4><i></i>المتطلبات التي تحكمها</h4><ul class="reqlist">%s</ul></div>'
            '%s'
            '</div></div></details>') % (
        pid, pid, esc(p['title']), new_tag, pri_tag, esc(p['purpose']), mock, fields, acts,
        _block('حالات خاصة بهذه الصفحة', own), _block('التحقق ورسائل الخطأ', p.get('validation')),
        _block('الصلاحيات', p.get('permissions')), _block('قرارات تجربة الاستخدام', p.get('ux')),
        ''.join(reqs), nxt_html)


STD_STATES = D['pages'][0]['states']


def surface_section(num, sid, name, desc):
    pages = [p for p in D['pages'] if p['surface'] == sid]
    body = ''.join(page_html(p) for p in pages)
    return ('<section id="s-%s"><h2><span class="num">%d</span>%s</h2>'
            '<p class="sub">%s تضم %d صفحة، مرتبة كما تُستعمل. تحت كل صفحة معاينة توضيحية وعناصرها وإجراءاتها والمتطلبات التي تحكمها. الحالات الخمس المشتركة في «حالات الصفحات المشتركة» لا تتكرر هنا.</p>%s</section>'
            ) % (sid, num, esc(name), esc(desc), len(pages), body)


# ---------------------------------------------------------------- المخططات
FLOWS = [
    ('order', 'طلب المنيو والمارت',
     'من اختيار المنتجات إلى التسليم والتحصيل، مع مسار الدعم عند غياب المندوب.',
     ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005', 'ORD-006', 'DSP-001', 'DSP-005', 'PAY-001']),
    ('written', 'طلبات الكتابة والصيدلية',
     'دفعتان: التوصيل أولاً ثم فاتورة المنتجات التي يرفعها التاجر ويسددها العميل خلال مهلة.',
     ['ORD-013', 'PHR-012', 'MER-036', 'PAY-007', 'PAY-021', 'PHR-010']),
    ('mart', 'كتالوجات البقالة',
     'تهيئة البقالة من كتالوج المارت: اشتراك، تفعيل، تعديل محلي، ثم معاينة سعر البيع.',
     ['MER-010', 'CAT-001', 'PAY-012', 'DSP-005', 'MER-031']),
    ('review', 'العروض والمراجعات',
     'عرض التاجر الخاص أو حملته: معاينة التكلفة ثم مراجعة الإدارة قبل أي نشر أو خصم.',
     ['MKT-007', 'MKT-008', 'MKT-003', 'MKT-017', 'MER-002']),
    ('manual', 'الخصم اليدوي',
     'لا غرامة آلية: التنبيه يفتح حالة، ويقرر موظف الدعم الغرامة ومن يتحملها بسبب مكتوب ودليل.',
     ['PAY-025', 'ADM-043', 'ORD-007', 'ORD-012', 'SUP-003', 'DRV-023']),
]


def svg_clean(svg, fid):
    s = BeautifulSoup(svg, 'xml')
    root = s.find('svg')
    steps = []
    for t in s.find_all('title'):
        txt = t.get_text(' ', strip=True)
        if ' · ' in txt and t.parent.name != 'svg':
            steps.append(txt)
    # مخرجات المولّد تحمل شرحاً إنجليزياً عاماً؛ نحذف desc ونُبقي العنوان
    for d in root.find_all('desc'):
        d.decompose()
    for c in root.find_all(string=lambda x: x.__class__.__name__ == 'Comment'):
        c.extract()
    root['class'] = 'flow-svg'
    root.attrs.pop('lang', None)
    out = str(root)
    out = out.replace('viewbox=', 'viewBox=')
    # معرّفات فريدة لكل مخطط (العلامات والأنماط)
    for i in set(re.findall(r'id="([^"]+)"', out)):
        out = out.replace('id="%s"' % i, 'id="%s-%s"' % (fid, i)).replace('url(#%s)' % i, 'url(#%s-%s)' % (fid, i))
        out = out.replace('aria-labelledby="%s' % i, 'aria-labelledby="%s-%s' % (fid, i))
    return out, steps


def flows_section(num):
    parts = []
    for fid, title, intro, refs in FLOWS:
        d = next(x for x in D['diagrams'] if x['id'] == fid)
        svg, steps = svg_clean(d['svg'], fid)
        lis = ''.join('<li>%s</li>' % esc(s.replace(' · ', ' — ', 1).replace(' · ', ' | ')) for s in steps)
        parts.append('<div class="flow" id="flow-%s"><h3>%s</h3><p>%s</p><div class="flow-box">%s</div>'
                     '<details class="flow-txt"><summary>نص المخطط</summary><ol>%s</ol></details>'
                     '<p class="flow-refs"><b>المتطلبات:</b> %s</p></div>' % (fid, esc(title), esc(intro), svg, lis, refs_html(refs)))
    return ('<section id="flows"><h2><span class="num">%d</span>رحلة الطلب</h2>'
            '<p class="sub">خمسة مخططات للمسارات الرئيسية. المخطط يوضح الترتيب فقط؛ المهل والمبالغ والاستثناءات مرجعها المتطلبات المذكورة تحت كل مخطط.</p>%s</section>') % (num, ''.join(parts))

# -*- coding: utf-8 -*-
"""مراجعة الصفحات (الإصدار 4.2): إكمال عناصر كل صفحة وسلوك إجراءاتها، وصفحات جديدة، ومعاينات محسّنة.

المصدر: ux/out/<ID>.json و ux/mocks/<ID>.html (و<ID>_2.html لمعاينة حالة ثانية).
يُدمج كل شيء في D['pages'] قبل بناء الفهارس، فيعمل الموقع والتحقق وprd.md على النسخة نفسها.
"""
import os, re, json, glob

UX_DIR = 'ux'
LOG = []  # تحذيرات الدمج


def _load(here):
    out = {}
    for f in sorted(glob.glob(os.path.join(here, UX_DIR, 'out', '*.json'))):
        try:
            d = json.load(open(f, encoding='utf8'))
        except Exception as e:  # ملف تالف: يُسجَّل ولا يوقف البناء
            LOG.append('JSON %s: %s' % (os.path.basename(f), e))
            continue
        out[d.get('id') or os.path.basename(f)[:-5]] = d
    return out


def _mock(here, name):
    f = os.path.join(here, UX_DIR, 'mocks', name + '.html')
    return open(f, encoding='utf8').read().strip() if os.path.exists(f) else None


def apply(D, REQ_IDS, here):
    """يدمج المراجعة في D. يعيد (MOCKS, MOCKS2) لاستعمالهما في المعاينات."""
    data = _load(here)
    pages = {p['id']: p for p in D['pages']}
    std = D['pages'][0]['states']
    MOCKS, MOCKS2 = {}, {}

    def clean_ids(ids, kind):
        ok = [i for i in ids if i in REQ_IDS]
        for i in ids:
            if i not in REQ_IDS:
                LOG.append('%s: معرّف غير معروف %s' % (kind, i))
        return ok

    # 1) الصفحات الجديدة أولاً (لتصح الروابط إليها)
    new = [d for d in data.values() if d.get('new')]
    for d in sorted(new, key=lambda x: x['id']):
        if d['id'] in pages:
            LOG.append('صفحة جديدة بمعرّف موجود %s' % d['id'])
            continue
        p = {'id': d['id'], 'surface': d['surface'], 'title': d['title'], 'purpose': d['purpose'], 'kind': d.get('kind', 'form'),
             'fields': list(d.get('fields', [])), 'actions': [a['name'] for a in d.get('actions', [])],
             'refs': clean_ids(d.get('refs', []), d['id']), 'states': list(std) + list(d.get('states', [])),
             'links': list(d.get('links', [])), 'priority': d.get('priority', 'launch'), 'new': True, 'after': d.get('after')}
        idx = next((i for i, x in enumerate(D['pages']) if x['id'] == d.get('after')), None)
        if idx is None:
            idx = max(i for i, x in enumerate(D['pages']) if x['surface'] == d['surface'])
            LOG.append('%s: الصفحة السابقة غير معروفة، وُضعت آخر الواجهة' % d['id'])
        # بعد آخر صفحة جديدة أُدرجت بعد الصفحة نفسها
        j = idx + 1
        while j < len(D['pages']) and D['pages'][j].get('new') and D['pages'][j].get('after') == d.get('after'):
            j += 1
        D['pages'].insert(j, p)
        pages[p['id']] = p

    # 2) الإضافات على كل صفحة
    for pid, d in data.items():
        p = pages.get(pid)
        if not p:
            LOG.append('مخرجات لصفحة غير معروفة %s' % pid)
            continue
        if not d.get('new'):
            p['fields'] += [x for x in d.get('fields_add', []) if x not in p['fields']]
            p['states'] += [x for x in d.get('states_add', []) if x not in p['states']]
            p['refs'] += [x for x in clean_ids(d.get('refs_add', []), pid) if x not in p['refs']]
        acts = [a for a in d.get('actions', []) if a.get('name')]
        names = [a['name'] for a in acts]
        for a in p['actions']:  # كل إجراء أصلي يبقى بنصه
            if a not in names:
                LOG.append('%s: الإجراء «%s» غاب من المراجعة، أُبقي بلا وصف' % (pid, a))
                acts.insert(0, {'name': a, 'result': ''})
        p['actions'] = [a['name'] for a in acts]
        p['acts'] = acts
        for l in d.get('links_add', []):
            if l not in p['links'] and l != pid:
                p['links'].append(l)
        for k in ('validation', 'permissions', 'ux', 'questions'):
            p[k] = [x for x in d.get(k, []) if x]
        p['mock2_caption'] = d.get('mock2_caption', '')

    # 2ب) النسخة المنقحة بلا تكرار (ux/out2): تحل محل العناصر والأوصاف، وأسماء الإجراءات لا تتغير
    for f in sorted(glob.glob(os.path.join(here, UX_DIR, 'out2', '*.json'))):
        try:
            d2 = json.load(open(f, encoding='utf8'))
        except Exception as e:
            LOG.append('JSON out2 %s: %s' % (os.path.basename(f), e))
            continue
        p = pages.get(d2.get('id'))
        if not p:
            continue
        names = [a['name'] for a in d2.get('acts', [])]
        if names != p['actions']:
            LOG.append('%s: أسماء الإجراءات في النسخة المنقحة لا تطابق، أُبقيت النسخة السابقة' % p['id'])
            continue
        p['fields'] = list(d2['fields'])
        p['acts'] = d2['acts']
        p['states'] = list(std) + [x for x in d2.get('states', []) if x not in std]
        for k in ('validation', 'permissions', 'ux'):
            p[k] = [x for x in d2.get(k, []) if x]
        p['covers'] = d2.get('covers', {})

    # روابط إلى صفحات غير موجودة
    for p in D['pages']:
        bad = [l for l in p['links'] if l not in pages]
        if bad:
            LOG.append('%s: روابط إلى صفحات غير موجودة %s' % (p['id'], bad))
            p['links'] = [l for l in p['links'] if l in pages]

    # 3) المعاينات
    for pid in pages:
        m = _mock(here, pid)
        if m:
            MOCKS[pid] = m
        m2 = _mock(here, pid + '_2')
        if m2:
            MOCKS2[pid] = m2
    return MOCKS, MOCKS2


SIDE_BTN = re.compile(r'<button class="[^"]*" data-page="(%s)">(<svg.*?</svg>)([^<]*)</button>', re.S)


def fix_sidebar(html, pid, D):
    """يضيف الصفحات الجديدة إلى القائمة الجانبية لكل معاينة لوحة، ويضيء صفحة المعاينة نفسها."""
    if 'mk desk' not in html:
        return html
    mer = 'mk desk mer' in html
    surface = 'merchant-dash' if mer else 'admin'
    for p in D['pages']:
        if p.get('new') and p['surface'] == surface and ('data-page="%s"' % p['id']) not in html:
            m = re.search(r'<button class="[^"]*" data-page="%s">(<svg.*?</svg>)[^<]*</button>' % re.escape(p['after'] or ''), html, re.S)
            if m:
                html = html[:m.end()] + '<button class="" data-page="%s">%s%s</button>' % (p['id'], m.group(1), p['title']) + html[m.end():]
    # الإضاءة على الصفحة الحالية فقط (والصفحات الجديدة تحمل معرّفها)
    if ('data-page="%s"' % pid) in html:
        html = re.sub(r'<button class="on" data-page="', '<button class="" data-page="', html)
        html = html.replace('<button class="" data-page="%s">' % pid, '<button class="on" data-page="%s">' % pid, 1)
    return html

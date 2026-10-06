# -*- coding: utf-8 -*-
"""نسخة نصية (Markdown) من المتطلبات للقراءة بالأدوات."""
from b4_common import *
import b4_front as F
import b4_pages as P
import b4_annex as X


def markdown(fixes):
    L = []
    w = L.append
    w('# مواصفات منصة محلات — الإصدار %s' % F.VERSION)
    w('')
    w('%s · المراجعة %s · %d متطلباً · %d صفحة. المتطلبات هي المرجع.' % (F.DATE, F.REVISION, F.N_REQ, F.N_PAGES))
    w('')
    for sid, title, sub, blocks in X.ANNEX:
        w('## ' + title)
        w('')
        w(sub)
        w('')
        L.extend(X.blocks_md(blocks))
    w('## الإعدادات (القيم الافتراضية القابلة للضبط)')
    w('')
    w('| الإعداد | القيمة | الحدود والأثر |')
    w('|---|---|---|')
    for a, b, c in D['settings']:
        w('| %s | %s | %s |' % (a, b, c))
    w('')
    w('## أمثلة العمليات المالية')
    w('')
    w('| المعطيات | حساب العميل | حساب التاجر أو المندوب |')
    w('|---|---|---|')
    for a, b, c in D['financialExamples']:
        w('| %s | %s | %s |' % (a, b, c))
    w('')
    w('## التكاملات')
    w('')
    for a, b, c in D['integrations']:
        w('- **%s** — %s (%s)' % (a, b, c))
    w('')
    w('## الجودة والتشغيل')
    w('')
    for q in D['quality']:
        w('- ' + q)
    w('')
    w('## قبل التشغيل')
    w('')
    for i, t, b in D['open']:
        w('- **%s %s**: %s' % (i, t, b))
    w('')
    w('## الصفحات')
    w('')
    for sid, name, desc, _ in SURF:
        w('### %s' % name)
        w('')
        for p in D['pages']:
            if p['surface'] != sid:
                continue
            w('#### %s — %s%s' % (p['id'], p['title'], ' (جديدة)' if p.get('new') else ''))
            w('')
            w(p['purpose'])
            w('')
            w('- العناصر: ' + '، '.join(p['fields']))
            if p.get('acts') and any(x.get('result') for x in p['acts']):
                w('- الإجراءات وما يحدث:')
                for x in p['acts']:
                    w('  - **%s**: %s' % (x['name'], x.get('result') or '—'))
            else:
                w('- الإجراءات: ' + '، '.join(p['actions']))
            for k, lab in (('validation', 'التحقق ورسائل الخطأ'), ('permissions', 'الصلاحيات'), ('ux', 'قرارات تجربة الاستخدام')):
                if p.get(k):
                    w('- %s:' % lab)
                    for x in p[k]:
                        w('  - ' + x)
            w('- المتطلبات: ' + ' '.join(p['refs']))
            if p['links']:
                w('- تنتقل إلى: ' + ' '.join(p['links']))
            own = [s for s in p['states'] if s not in P.STD_STATES]
            if own:
                w('- حالات خاصة: ' + '؛ '.join(own))
            w('')
    w('الحالات المشتركة لكل الصفحات: ' + '؛ '.join(P.STD_STATES) + '.')
    w('')
    w('## التقارير')
    w('')
    for owner, rows in D['reports'].items():
        w('### %s' % owner)
        cur = None
        for r in rows:
            if r['group'] != cur:
                cur = r['group']
                w('')
                w('**%s**' % cur)
            w('- %s: %s' % (r['title'], r['description']))
        w('')
    w('## المتطلبات')
    w('')
    for m, name in MODULES:
        items = [r for r in D['requirements'] if r['id'].startswith(m + '-')]
        if not items:
            continue
        w('### %s (%s)' % (name, m))
        w('')
        for r in items:
            rules = fixes.get(r['id'], {}).get('rules', r['rules'])
            acc = fixes.get(r['id'], {}).get('acceptance', r['acceptance'])
            w('#### %s — %s [%s]' % (r['id'], r['title'], PRI[r['priority']][1]))
            w('')
            w('القواعد:')
            for x in rules:
                w('- ' + x)
            w('')
            w('معيار القبول:')
            for x in acc:
                w('- ' + x)
            u = USED.get(r['id'])
            if u:
                w('')
                w('الصفحات: ' + ' '.join(u))
            w('')
    return '\n'.join(L)

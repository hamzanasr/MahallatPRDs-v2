# -*- coding: utf-8 -*-
"""يبني موقع المتطلبات (الإصدار 4) من ملف المالك الجديد."""
import os, sys, json, shutil, re
from b4_common import *
import b4_pages as P
import b4_rules as R
import b4_front as F
import b4_md as M
import b4_annex as X
import b4_open as H

OUT = sys.argv[1] if len(sys.argv) > 1 else (os.path.dirname(HERE) if os.path.basename(HERE) == 'tools' else os.path.join(HERE, 'site4'))

# إصلاحات لغوية معتمدة وملاحظات المالك
FIXES = {}  # التصحيحات والقرارات مطبّقة على D في b4_common

# ترتيب الأقسام: (المعرّف في القائمة, العنوان, الجزء)
n = 0


def nxt():
    global n
    n += 1
    return n


body = []
nav = []


def add(sid, title, part, html):
    body.append(html)
    nav.append((part, sid, title))


add('start', 'ابدأ من هنا', 'البداية', F.start_section(nxt()))
add('scope', 'نطاق الإصدار الأول', 'البداية', F.scope_section(nxt()))
add('prelaunch', 'قبل التشغيل', 'البداية', F.prelaunch_section(nxt()))
add('glossary', 'المصطلحات', 'البداية', F.glossary_section(nxt()))
add('flows', 'رحلة الطلب', 'قواعد العمل', P.flows_section(nxt()))
add('order-states', 'حالات الطلب لكل نوع', 'قواعد العمل', X.annex_section('order-states', nxt()))
add('dispatch', 'خوارزمية التوزيع', 'قواعد العمل', X.annex_section('dispatch', nxt()))
add('money', 'الحسابات والرسوم', 'قواعد العمل', R.money_section(nxt()))
add('closing', 'إغلاق الطلب دون تسليم', 'قواعد العمل', X.annex_section('closing', nxt()))
add('settings', 'القيم المرنة', 'قواعد العمل', R.settings_section(nxt()))
add('roles', 'الأدوار والصلاحيات', 'قواعد العمل', X.annex_section('roles', nxt()))
add('integrations', 'الربط مع الخدمات', 'قواعد العمل', R.integrations_section(nxt()))
add('quality', 'الجودة والتشغيل', 'قواعد العمل', R.quality_section(nxt()))
add('states', 'حالات الصفحات المشتركة', 'الواجهات', F.states_section(nxt()))
for sid, name, desc, _ in SURF:
    add('s-' + sid, name, 'الواجهات', P.surface_section(nxt(), sid, name, desc))
add('admin-detail', 'تفاصيل صفحات الإدارة', 'الواجهات', X.annex_section('admin-detail', nxt()))
add('reports', 'التقارير', 'الواجهات', R.reports_section(nxt()))
add('kpi', 'تعريف المؤشرات', 'الواجهات', X.annex_section('kpi', nxt()))
add('catalog', 'فهرس المتطلبات', 'للتنفيذ', F.catalog_section(nxt(), FIXES))
add('open', 'أسئلة مفتوحة', 'للتنفيذ', H.open_section(nxt()))

nav_html = ''
cur = None
for i, (part, sid, title) in enumerate(nav, 1):
    if part != cur:
        nav_html += '<div class="nav-part">%s</div>\n' % part
        cur = part
    nav_html += '<a href="#%s" data-sec="%s"><i>%d</i>%s</a>\n' % (sid, sid, i, esc(title))

tpl = open(os.path.join(HERE, 'template4.html'), encoding='utf8').read()
html_out = (tpl.replace('{{NAV}}', nav_html).replace('{{BODY}}', '\n'.join(body))
            .replace('{{VERSION}}', F.VERSION).replace('{{DATE}}', F.DATE).replace('{{N_REQ}}', str(F.N_REQ))
            .replace('{{N_PAGES}}', str(F.N_PAGES)).replace('{{N_FLOWS}}', str(len(P.FLOWS)))
            .replace('{{SPRITE}}', P.sprite_defs()))

os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(html_out)
shutil.copy(os.path.join(HERE, 'style4.css'), os.path.join(OUT, 'assets', 'style.css'))
open(os.path.join(OUT, 'assets', 'mock.css'), 'w', encoding='utf8').write(
    open(os.path.join(HERE, 'mock4.css'), encoding='utf8').read() + chr(10) + open(os.path.join(HERE, 'mock_ux.css'), encoding='utf8').read())
for _w in UXM.LOG:
    print('UX:', _w)
shutil.copy(os.path.join(HERE, 'app4.js'), os.path.join(OUT, 'assets', 'app.js'))
open(os.path.join(OUT, 'prd.md'), 'w', encoding='utf8').write(M.markdown(FIXES))

# النسخة الإنجليزية (en/index.html) من القاموس tools/i18n/en.json
import b4_en
_miss = b4_en.build(OUT)
print('EN: untranslated segments', len(_miss))
print('written', OUT, len(html_out), 'sections', len(nav), 'reqs', F.N_REQ, 'pages', F.N_PAGES, 'icons', len(P.SPRITE))

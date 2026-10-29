# -*- coding: utf-8 -*-
"""أدوات مشتركة لبناء موقع المتطلبات (الإصدار 4) من ملف المالك."""
import json, re, os, html
HERE = os.path.dirname(os.path.abspath(__file__))

import copy
import b4_decisions as DEC

D = json.load(open(os.path.join(HERE, 'newprd.json'), encoding='utf8'))
D_ORIG = copy.deepcopy(D)  # ملف المالك كما وصل، للمقارنة والتحقق

# 1) التصحيحات اللغوية المعتمدة  2) قرارات المالك. كلاهما يُكتب في نص المتطلب نفسه.
_fx = os.path.join(HERE, 'qa', 'fixes.json')
FIXES = json.load(open(_fx, encoding='utf8')) if os.path.exists(_fx) else {}
DEC_LOG = []  # (المعرّف, قرارات, القواعد قبل, القبول قبل, الأولوية قبل)
for _r in D['requirements']:
    _f = FIXES.get(_r['id'])
    if _f:
        _r['rules'], _r['acceptance'] = list(_f['rules']), list(_f['acceptance'])
    _d = DEC.REQ.get(_r['id'])
    if _d:
        DEC_LOG.append((_r['id'], _d['dec'], list(_r['rules']), list(_r['acceptance']), _r['priority']))
        if _d.get('rules') is not None:
            _r['rules'], _r['acceptance'] = list(_d['rules']), list(_d['acceptance'])
        if _d.get('priority'):
            _r['priority'] = _d['priority']
assert {x[0] for x in DEC_LOG} == set(DEC.REQ), set(DEC.REQ) - {x[0] for x in DEC_LOG}

# الجولة الثالثة: مقترحات مراجعة الصفحات التي اعتمدها المالك (إضافة قواعد واستبدال ما يخالفها)
import b4_decisions3 as DEC3
_by = {r['id']: r for r in D['requirements']}
_log = {x[0]: x for x in DEC_LOG}
_ids3 = {}


def _touch(rid, n):
    r = _by[rid]
    if rid not in _log:
        _log[rid] = (rid, [], list(r['rules']), list(r['acceptance']), r['priority'])
        DEC_LOG.append(_log[rid])
    if n not in _log[rid][1]:
        _log[rid][1].append(n)
    _ids3.setdefault(n, [])
    if rid not in _ids3[n]:
        _ids3[n].append(rid)
    return r


for _n, _rid, _old, _new in DEC3.REPLACE:
    _r = _touch(_rid, _n)
    _k = next(k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k]))
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC3.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC3.DECISIONS)

# الجولة الرابعة: الأسئلة العشرة المفتوحة، والعقد ومنيو المطاعم، والكول سنتر
import b4_decisions4 as DEC4
for _n, _rid in DEC4.DROP:
    assert _rid in _by, _rid
    D['requirements'] = [r for r in D['requirements'] if r['id'] != _rid]
    _ids3.setdefault(_n, []).append(_rid)
for _n, _rid, _old, _new in DEC4.REPLACE:
    _r = _touch(_rid, _n)
    _k = next(k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k]))
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC4.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
for _n, _rid, _p in DEC4.PRIORITY:
    _touch(_rid, _n)['priority'] = _p
for _i, _row in DEC4.EXAMPLES:
    if _i is None:
        D['financialExamples'].append(list(_row))
    else:
        D['financialExamples'][_i] = list(_row)
for _row in D['integrations']:
    if _row[0] in DEC4.INTEGRATIONS:
        _row[2] = DEC4.INTEGRATIONS[_row[0]]
    if _row[0] in DEC4.INTEGRATIONS_DESC:
        _row[1] = DEC4.INTEGRATIONS_DESC[_row[0]]
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC4.DECISIONS)
for _p in D['pages']:
    if _p['id'] in DEC4.PAGE_PURPOSE:
        _p['purpose'] = DEC4.PAGE_PURPOSE[_p['id']]

# الجولة الخامسة: تحويل التجار بحسب بوابة الدفع، وتحويل المناديب عبر STC Pay
import b4_decisions5 as DEC5
for _after, _new in DEC5.NEW_REQ:
    _i = next(i for i, x in enumerate(D['requirements']) if x['id'] == _after)
    D['requirements'].insert(_i + 1, copy.deepcopy(_new))
    _by[_new['id']] = D['requirements'][_i + 1]
    _ids3.setdefault(91, []).append(_new['id'])
for _n, _rid, _old, _new in DEC5.REPLACE:
    _r = _touch(_rid, _n)
    _k = next(k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k]))
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC5.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
for _start, _new in DEC5.EXAMPLE_EDITS:
    _i = next(i for i, x in enumerate(D['financialExamples']) if x[0].startswith(_start))
    D['financialExamples'][_i][0] = _new
for _row in DEC5.EXAMPLE_ADD:
    D['financialExamples'].append(list(_row))
for _where, _name, _desc, _st in DEC5.INTEGRATION_ADD:
    _i = next(i for i, x in enumerate(D['integrations']) if x[0] == _where)
    D['integrations'].insert(_i + 1, [_name, _desc, _st])
for _row in D['integrations']:
    if _row[0] in DEC5.INTEGRATIONS_DESC:
        _row[1] = DEC5.INTEGRATIONS_DESC[_row[0]]
for _after, _item in DEC5.PRELAUNCH_ADD:
    _i = next(i for i, x in enumerate(D['open']) if x[0] == _after)
    D['open'].insert(_i + 1, list(_item))
for _start, _old, _new in DEC5.QUALITY_EDITS:
    _i = next(i for i, x in enumerate(D['quality']) if x.startswith(_start))
    assert _old in D['quality'][_i]
    D['quality'][_i] = D['quality'][_i].replace(_old, _new)
for _pid, _rid in DEC5.PAGE_REFS_ADD:
    _p = next(p for p in D['pages'] if p['id'] == _pid)
    if _rid not in _p['refs']:
        _p['refs'].append(_rid)
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC5.DECISIONS)
DEC.SETTING_ADD.extend(DEC5.SETTING_ADD)

# الجولة السادسة: جلسة تدقيق نموذج المجال (المصطلحات، وبانتظار قرار الدعم، ولا اعتذار بعد القبول، ومهلة البلاغ)
import b4_decisions6 as DEC6
import b4_terms6 as TERMS6
for _rid, (_n, _title) in DEC6.TITLE.items():
    _touch(_rid, _n)['title'] = _title
for _n, _rid, _old, _new in DEC6.REPLACE:
    _r = _touch(_rid, _n)
    _k = next((k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k])), None)
    assert _k, (_rid, _old)
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC6.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
for _n, _rid, _old, _new in TERMS6.TERMS:
    _r = _touch(_rid, _n)
    _k = next((k for k in ('rules', 'acceptance') if _old in _r[k]), None)
    assert _k, (_rid, _old)
    _r[_k] = [(_new if x == _old else x) for x in _r[_k]]
for _start, _col, _old, _new in DEC6.EXAMPLE_EDITS6:
    _i = next(i for i, x in enumerate(D['financialExamples']) if x[0].startswith(_start))
    assert _old in D['financialExamples'][_i][_col], (_start, _old)
    D['financialExamples'][_i][_col] = D['financialExamples'][_i][_col].replace(_old, _new)
for _start, _old, _new in DEC6.QUALITY_EDITS6:
    _i = next(i for i, x in enumerate(D['quality']) if x.startswith(_start))
    assert _old in D['quality'][_i], (_start, _old)
    D['quality'][_i] = D['quality'][_i].replace(_old, _new)
def _deep6(x, old, new, hit):
    if isinstance(x, str):
        if old in x:
            hit[0] += 1
        return x.replace(old, new)
    if isinstance(x, list):
        return [_deep6(y, old, new, hit) for y in x]
    if isinstance(x, dict):
        return {k: _deep6(y, old, new, hit) for k, y in x.items()}
    return x


for _key, _old, _new in DEC6.OWNER_STR_EDITS:
    _hit = [0]
    D[_key] = _deep6(D[_key], _old, _new, _hit)
    assert _hit[0], (_key, _old)
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC6.DECISIONS)
DEC.SETTING_ADD.extend(DEC6.SETTING_ADD6)

# الجولة السابعة: الفرع وحدة مستقلة كأنه متجر لوحده
import b4_decisions7 as DEC7
for _rid, (_n, _title) in DEC7.TITLE.items():
    _touch(_rid, _n)['title'] = _title
for _n, _rid, _old, _new in DEC7.REPLACE:
    _r = _touch(_rid, _n)
    _k = next((k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k])), None)
    assert _k, (_rid, _old)
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC7.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC7.DECISIONS)

# الجولة الثامنة: مراجعة نموذج المال والإطلاق (التقسيم النظام الوحيد، ولا نقل من التطبيق الحالي)
import b4_decisions8 as DEC8
for _n, _rid in DEC8.DROP:
    assert _rid in _by, _rid
    D['requirements'] = [r for r in D['requirements'] if r['id'] != _rid]
    _ids3.setdefault(_n, []).append(_rid)
for _rid, (_n, _title) in DEC8.TITLE.items():
    _touch(_rid, _n)['title'] = _title
for _n, _rid, _old, _new in DEC8.REPLACE:
    _r = _touch(_rid, _n)
    _k = next((k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k])), None)
    assert _k, (_rid, _old)
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC8.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
for _n, _rid, _p in DEC8.PRIORITY:
    _touch(_rid, _n)['priority'] = _p
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC8.DECISIONS)

# الجولة التاسعة: تصحيحات 4.11 (لا تحويل آلي، والانتقال من المنصة الحالية، والإبلاغ للهيئة العامة للنقل)
import b4_decisions9 as DEC9
D['revision'] = DEC9.REVISION
for _after, _n, _new in DEC9.NEW_REQ:
    assert _new['id'] not in _by, _new['id']
    _i = next(i for i, x in enumerate(D['requirements']) if x['id'] == _after)
    D['requirements'].insert(_i + 1, copy.deepcopy(_new))
    _by[_new['id']] = D['requirements'][_i + 1]
    _ids3.setdefault(_n, []).append(_new['id'])
for _n, _rid, _old, _new in DEC9.REPLACE:
    _r = _touch(_rid, _n)
    _k = next((k for k in ('rules', 'acceptance') if any(x.startswith(_old) for x in _r[k])), None)
    assert _k, (_rid, _old)
    _r[_k] = [(_new if x.startswith(_old) else x) for x in _r[_k] if _new is not None or not x.startswith(_old)]
for _n, _rid, _kind, _txt in DEC9.ADD:
    _r = _touch(_rid, _n)
    _r['rules' if _kind == 'R' else 'acceptance'].append(_txt)
_first9 = {}  # عدد ما أُدرج «أولاً» في كل قائمة، ليبقى بترتيب كتابته
for _n, _rid, _kind, _after, _txt in DEC9.INSERT:
    _r = _touch(_rid, _n)
    _l = _r['rules' if _kind == 'R' else 'acceptance']
    if _after is None:
        _j = _first9.get((_rid, _kind), 0)
        _first9[(_rid, _kind)] = _j + 1
    else:
        _j = next((j + 1 for j, x in enumerate(_l) if x.startswith(_after)), None)
        assert _j is not None, (_rid, _after)
    _l.insert(_j, _txt)
for _n, _rid, _p in DEC9.PRIORITY:
    _touch(_rid, _n)['priority'] = _p
for _pid, _rid in DEC9.PAGE_REFS_ADD:
    _p = next(p for p in D['pages'] if p['id'] == _pid)
    if _rid not in _p['refs']:
        _p['refs'].append(_rid)
DEC.DECISIONS.extend((n, t, d, _ids3.get(n, [])) for n, t, d in DEC9.DECISIONS)

DEC.DECISIONS.sort(key=lambda x: x[0])
DEC.SETTING_EDITS.update(DEC3.SETTING_EDITS)
DEC.SETTING_EDITS.update(DEC4.SETTING_EDITS)
DEC.SETTING_ADD[0] = ('رسوم التوصيل', 'المطاعم والمحلات: 9 ر.س تشمل 3 كم + 1.5 لكل كيلو، حد 9–25؛ المارت والصيدليات: 12 ر.س تشمل 3 كم + 1.5 لكل كيلو، حد 12–30',
                      'عام للنظام وإعداد اختياري لكل مدينة', 'المال والرسوم', ['PAY-013'])
for _i, _row in enumerate(DEC.SETTING_ADD):
    if _row[0] in DEC5.SETTING_ADD_EDITS:
        DEC.SETTING_ADD[_i] = DEC5.SETTING_ADD_EDITS[_row[0]]
    if _row[0] in DEC5.SETTING_SCOPE_EDITS:
        DEC.SETTING_ADD[_i] = (_row[0], _row[1], DEC5.SETTING_SCOPE_EDITS[_row[0]], _row[3], _row[4])
SETTING_REFS_ADD = []
for _i, _row in DEC.SETTING_EDITS.items():
    D['settings'][_i] = list(_row)
for _a, _b, _c, _g, _refs in DEC.SETTING_ADD:
    D['settings'].append([_a, _b, _c])
    SETTING_REFS_ADD.append((len(D['settings']) - 1, _g, _refs))
_found6 = set()
for _row in D['settings']:
    if _row[0] in DEC6.SETTING_EDITS6:
        _found6.add(_row[0])
        _row[:] = list(DEC6.SETTING_EDITS6[_row[0]])
assert _found6 == set(DEC6.SETTING_EDITS6), set(DEC6.SETTING_EDITS6) - _found6
for _pid, _k, _old, _new in DEC.PAGE_EDITS:
    _p = next(p for p in D['pages'] if p['id'] == _pid)
    _p[_k] = [_new if x == _old else x for x in _p[_k]]
    assert _new in _p[_k]
for _pid, _k, _old, _new in TERMS6.PAGE_EDITS6:
    _p = next(p for p in D['pages'] if p['id'] == _pid)
    if isinstance(_p[_k], list):
        assert _old in _p[_k], (_pid, _k, _old)
        _p[_k] = [(_new if x == _old else x) for x in _p[_k] if _new is not None or x != _old]
    else:
        assert _p[_k] == _old, (_pid, _k, _old)
        _p[_k] = _new

# الجولة الثامنة: الإعدادات والأمثلة والتكاملات وبنود «قبل التشغيل»
_found8 = set()
for _row in D['settings']:
    if _row[0] in DEC8.SETTING_EDITS8:
        _found8.add(_row[0])
        _row[:] = list(DEC8.SETTING_EDITS8[_row[0]])
assert _found8 == set(DEC8.SETTING_EDITS8), set(DEC8.SETTING_EDITS8) - _found8
for _a, _b, _c, _g, _refs in DEC8.SETTING_ADD8:
    D['settings'].append([_a, _b, _c])
    SETTING_REFS_ADD.append((len(D['settings']) - 1, _g, _refs))
for _start in DEC8.EXAMPLE_DROP8:
    assert any(x[0].startswith(_start) for x in D['financialExamples']), _start
    D['financialExamples'] = [x for x in D['financialExamples'] if not x[0].startswith(_start)]
for _start, _col, _old, _new in DEC8.EXAMPLE_EDITS8:
    _i = next(i for i, x in enumerate(D['financialExamples']) if x[0].startswith(_start))
    assert _old in D['financialExamples'][_i][_col], (_start, _old)
    D['financialExamples'][_i][_col] = D['financialExamples'][_i][_col].replace(_old, _new)
for _row in D['integrations']:
    if _row[0] in DEC8.INTEGRATIONS_DESC8:
        _row[1] = DEC8.INTEGRATIONS_DESC8[_row[0]]
for _where, _name, _desc, _st in DEC8.INTEGRATION_ADD8:
    _i = next(i for i, x in enumerate(D['integrations']) if x[0] == _where)
    D['integrations'].insert(_i + 1, [_name, _desc, _st])
for _start, _new in DEC8.QUALITY_EDITS8:
    _i = next(i for i, x in enumerate(D['quality']) if x.startswith(_start))
    D['quality'][_i] = _new
for _id in DEC8.PRELAUNCH_DROP8:
    assert any(x[0] == _id for x in D['open']), _id
    D['open'] = [x for x in D['open'] if x[0] != _id]
for _id, _old, _new in DEC8.PRELAUNCH_EDITS8:
    _x = next(x for x in D['open'] if x[0] == _id)
    _j = next(j for j, y in enumerate(_x) if isinstance(y, str) and _old in y)
    _x[_j] = _x[_j].replace(_old, _new)

# الجولة التاسعة: الإعدادات والتكاملات والجودة وبنود «قبل التشغيل»
_found9 = set()
for _row in D['settings']:
    if _row[0] in DEC9.SETTING_EDITS9:
        _found9.add(_row[0])
        _row[:] = list(DEC9.SETTING_EDITS9[_row[0]])
assert _found9 == set(DEC9.SETTING_EDITS9), set(DEC9.SETTING_EDITS9) - _found9
for _row in D['integrations']:
    if _row[0] in DEC9.INTEGRATIONS9:
        _row[1], _row[2] = DEC9.INTEGRATIONS9[_row[0]]
for _start, _new in DEC9.QUALITY_EDITS9:
    _i = next(i for i, x in enumerate(D['quality']) if x.startswith(_start))
    D['quality'][_i] = _new
for _id, _old, _new in DEC9.PRELAUNCH_EDITS9:
    _x = next(x for x in D['open'] if x[0] == _id)
    _j = next(j for j, y in enumerate(_x) if isinstance(y, str) and _old in y)
    _x[_j] = _x[_j].replace(_old, _new)

# 3) مراجعة الصفحات: عناصر ناقصة، وسلوك الإجراءات، وصفحات جديدة، ومعاينات محسّنة
import b4_ux as UXM
UX_MOCKS, UX_MOCKS2 = UXM.apply(D, {r['id'] for r in D['requirements']}, HERE)

PRI = {'launch': ('p1', 'أساسي للإطلاق'), 'important': ('p2', 'مهم'), 'later': ('p3', 'لاحقاً'), 'foundation': ('p4', 'بنية مؤجلة')}
PRI_ORDER = ['launch', 'important', 'later', 'foundation']

MODULES = [  # (البادئة, الاسم, المجموعة في الملف)
    ('REG', 'الامتثال: برنامج «هدف»'), ('CUS', 'تطبيق العميل'), ('CRT', 'السلة والدفع'), ('ORD', 'دورة الطلب'),
    ('PAY', 'الدفع والرسوم والتسويات'), ('CAT', 'كتالوج المارت'), ('MER', 'التاجر والفروع'), ('DRV', 'المندوب'),
    ('DSP', 'التوزيع والمدن'), ('FLT', 'شركات التوصيل'), ('ADM', 'الإدارة'), ('SUP', 'الدعم'),
    ('MKT', 'العروض والإعلانات والولاء'), ('EXT', 'الخدمات'), ('INT', 'الربط مع الخدمات'), ('PHR', 'الصيدليات'),
    ('REP', 'التقارير'), ('SYS', 'البناء والتشغيل'), ('TAX', 'Taxi'),
]
for _after, _m, _name in DEC9.MODULE_ADD:
    MODULES.insert(next(i for i, x in enumerate(MODULES) if x[0] == _after) + 1, (_m, _name))
MOD_NAME = dict(MODULES)

SURF = [  # (المعرّف في الملف, الاسم, الوصف, رمز الصفحات)
    ('customer', 'تطبيق العميل', 'المتاجر والسلة والطلب والتتبع والرصيد.', 'C'),
    ('merchant', 'تطبيق التاجر', 'التجهيز والتسليم والمنيو والفريق.', 'M'),
    ('merchant-dash', 'لوحة التاجر', 'التقارير والمستحقات والفروع والصلاحيات (موقع ويب).', 'MD'),
    ('driver', 'تطبيق المندوب', 'المهام والاستلام والتسليم والأداء والأرباح.', 'D'),
    ('admin', 'لوحة الإدارة', 'التشغيل وملف التاجر والحسابات والدعم والإعدادات.', 'A'),
]
SURF_NAME = {s[0]: s[1] for s in SURF}

REQ = {r['id']: r for r in D['requirements']}
PAGES = {p['id']: p for p in D['pages']}
USED = {}
for p in D['pages']:
    if p.get('sub'):  # الشاشة الفرعية تتبع صفحتها ولا تُعد صفحة (D11_2)
        continue
    for r in p['refs']:
        USED.setdefault(r, []).append(p['id'])


def esc(s):
    return html.escape(str(s), quote=False)


def attr(s):
    return html.escape(str(s), quote=True)


ID_RE = re.compile(r'(?<![\w-])((?:[A-Z]{3}-\d{2,3})|TAX-FND|CFG-01|DATA-01|INT-SEL|D-\d{2})(?![\w-])')


def link_ids(text):
    """يحوّل معرّفات المتطلبات داخل نص (بعد الهروب) إلى روابط."""
    def rep(m):
        i = m.group(1)
        if i in REQ:
            return '<a class="rid" href="#%s">%s</a>' % (i, i)
        if i in ('CFG-01', 'INT-SEL', 'DATA-01'):
            return '<a class="rid" href="#prelaunch">%s</a>' % i
        return '<bdi class="rid">%s</bdi>' % i
    return ID_RE.sub(rep, text)


def fmt(text):
    """نص عادي → HTML آمن مع روابط المعرّفات ونظافة الفراغات حول الأقواس."""
    t = esc(text)
    t = re.sub(r'\(\s+', '(', t)
    t = re.sub(r'\s+\)', ')', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return link_ids(t)


def tag(pri):
    k, label = PRI[pri]
    return '<span class="tag %s">%s</span>' % (k, label)


def req_link(i, title=True):
    r = REQ.get(i)
    if not r:
        return '<bdi class="rid">%s</bdi>' % esc(i)
    return '<a class="rid" href="#%s">%s</a>%s' % (i, i, (' ' + esc(r['title'])) if title else '')


def tbl(head, rows, cls=''):
    h = ''.join('<th>%s</th>' % c for c in head)
    b = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)
    return '<div class="tbl %s"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cls, h, b)


def refs_html(ids):
    return ' · '.join('<a class="rid" href="#%s">%s</a>' % (i, i) if i in REQ else '<bdi class="rid">%s</bdi>' % i for i in ids)


def lines(text):
    """يفصل المقاطع المفصولة بـ«؛» إلى أسطر ليسهل مسح القيم المضغوطة."""
    parts = [p.strip() for p in re.split(r'[؛;]', str(text)) if p.strip()]
    return '<br>'.join(fmt(p) for p in parts)

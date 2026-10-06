# -*- coding: utf-8 -*-
"""النسخة الإنجليزية من الموقع: تُبنى من index.html العربي بقاموس ترجمة (i18n/en.json) وتُكتب في en/index.html.

كل «مقطع» نص عربي متصل (نص وعناصر سطرية مثل <a> و<b>) يُترجم كاملاً بوسومه، فيبقى ترتيب الجملة الإنجليزية سليماً.
المقطع الذي لا ترجمة له يبقى عربياً ويُطبع في تقرير البناء، ثم يُضاف إلى القاموس:
    python b4_en.py --missing missing.json   # يكتب المقاطع الناقصة لترجمتها
"""
import os, re, sys, json
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
DICT = os.path.join(HERE, 'i18n', 'en.json')
AR = re.compile(r'[؀-ۿ]')
INLINE = {'a', 'b', 'strong', 'i', 'em', 'bdi', 'small', 'code', 'br', 'sup', 'sub', 'kbd', 'mark', 'u', 'span',
          'abbr', 'time', 's', 'del', 'ins', 'wbr', 'tspan', 'q', 'cite', 'var', 'dfn', 'label'}
SKIP = {'script', 'style', 'svg:defs'}
ATTRS = ('aria-label', 'title', 'placeholder', 'value', 'alt', 'content', 'data-demo', 'data-edge-label',
         'data-node-label', 'data-node-sublabel', 'data-node-context', 'data-label')
WS = re.compile(r'\s+')


def key(s):
    return WS.sub(' ', s).strip()


def _inline_ok(n):
    if isinstance(n, Comment):
        return False
    if isinstance(n, NavigableString):
        return True
    if not isinstance(n, Tag) or n.name not in INLINE:
        return False
    return all(_inline_ok(c) for c in n.children)


def runs(soup):
    """قوائم عقد متجاورة (نص وعناصر سطرية) فيها عربي."""
    out = []

    def walk(el):
        if el.name in SKIP:
            return
        cur = []

        def flush():
            if cur and AR.search(''.join(str(x) for x in cur)):
                out.append(list(cur))
            cur.clear()
        for c in list(el.children):
            if _inline_ok(c):
                cur.append(c)
            else:
                flush()
                if isinstance(c, Tag):
                    walk(c)
        flush()
    walk(soup)
    return out


def attr_items(soup):
    for el in soup.find_all(True):
        for a in ATTRS:
            v = el.get(a)
            if isinstance(v, str) and AR.search(v):
                yield el, a, v


def segments(html):
    soup = BeautifulSoup(html, 'html.parser')
    segs = {key(''.join(str(x) for x in r)) for r in runs(soup)}
    segs |= {key(v) for _, _, v in attr_items(soup)}
    return segs


def translate(html, T):
    """يعيد (HTML الإنجليزي، المقاطع الناقصة)."""
    soup = BeautifulSoup(html, 'html.parser')
    missing = set()
    for r in runs(soup):
        raw = ''.join(str(x) for x in r)
        k = key(raw)
        en = T.get(k)
        if en is None:
            missing.add(k)
            continue
        lead = raw[:len(raw) - len(raw.lstrip())]
        trail = raw[len(raw.rstrip()):]
        frag = BeautifulSoup(lead + en + trail, 'html.parser')
        first = r[0]
        for n in list(frag.contents):
            first.insert_before(n)
        for n in r:
            n.extract()
    for el, a, v in attr_items(soup):
        en = T.get(key(v))
        if en is None:
            missing.add(key(v))
        else:
            el[a] = en
    h = soup.find('html')
    h['lang'], h['dir'] = 'en', 'ltr'
    btn = soup.find(id='lang-btn')
    if btn:
        btn['href'], btn['hreflang'], btn['lang'] = '../', 'ar', 'ar'
        btn.string = 'العربية'
    return str(soup), missing


def localize_paths(html):
    """en/index.html يستعمل ملفات الجذر نفسها."""
    html = re.sub(r'(href|src)="(assets/[^"]+)"', r'\1="../\2"', html)
    html = html.replace('href="prd.md"', 'href="../prd.en.md"')
    return html


def build(root):
    T = json.load(open(DICT, encoding='utf8')) if os.path.exists(DICT) else {}
    src = open(os.path.join(root, 'index.html'), encoding='utf8').read()
    en, missing = translate(src, T)
    en = localize_paths(en)
    os.makedirs(os.path.join(root, 'en'), exist_ok=True)
    open(os.path.join(root, 'en', 'index.html'), 'w', encoding='utf8').write(en)
    return missing


if __name__ == '__main__':
    root = os.path.dirname(HERE)
    if '--missing' in sys.argv:
        out = sys.argv[sys.argv.index('--missing') + 1]
        T = json.load(open(DICT, encoding='utf8')) if os.path.exists(DICT) else {}
        segs = segments(open(os.path.join(root, 'index.html'), encoding='utf8').read())
        miss = sorted(s for s in segs if s not in T)
        json.dump(miss, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
        print('missing', len(miss), 'of', len(segs))
    else:
        m = build(root)
        print('en/index.html written; untranslated segments:', len(m))

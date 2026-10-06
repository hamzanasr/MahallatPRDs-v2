# -*- coding: utf-8 -*-
"""يصوّر معاينة صفحة: python ux/shot.py C09   (أو C09_2 للمعاينة الثانية)
يقرأ ux/mocks/<ID>.html إن وُجد، وإلا المعاينة الأصلية من previews_raw.json، ويحفظ ux/shots/<ID>.png"""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
pid = sys.argv[1]
f = os.path.join(HERE, 'mocks', pid + '.html')
if os.path.exists(f):
    mock = open(f, encoding='utf8').read()
else:
    mock = json.load(open(os.path.join(ROOT, 'previews_raw.json'), encoding='utf8'))[pid.split('_')[0]]
desk = 'mk desk' in mock
a = os.path.join(ROOT, 'site4', 'assets').replace(os.sep, '/')
r = ROOT.replace(os.sep, '/')
page = ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="file:///%s/style.css"><link rel="stylesheet" href="file:///%s/mock.css">'
        '<link rel="stylesheet" href="file:///%s/mock_ux.css"></head>'
        '<body style="background:#e9eeec;margin:0;padding:20px"><div class="mock" style="max-width:%dpx;margin:0 auto">%s</div></body></html>') % (
    a, a, r, 1240 if desk else 420, mock)
out_html = os.path.join(HERE, 'shots', pid + '.html')
open(out_html, 'w', encoding='utf8').write(page)
png = os.path.join(HERE, 'shots', pid + '.png')
if os.path.exists(png):
    os.remove(png)
edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
size = '1290,1000' if desk else '480,800'
subprocess.run([edge, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                '--user-data-dir=' + os.path.join(HERE, 'shots', '.prof_' + pid),
                '--window-size=' + size, '--screenshot=' + png, 'file:///' + out_html.replace(os.sep, '/')],
               capture_output=True, timeout=90)
print(png if os.path.exists(png) else 'FAILED')

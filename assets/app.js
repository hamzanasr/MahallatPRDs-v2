(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var root = document.documentElement;
  var EN = root.lang === 'en';
  var T = function (ar, en) { return EN ? en : ar; };

  /* ---------- تبديل اللغة مع البقاء في الموضع نفسه ---------- */
  var lb = $('#lang-btn');
  if (lb) lb.addEventListener('click', function (e) { e.preventDefault(); location.href = lb.getAttribute('href') + location.hash; });

  /* ---------- المظهر ---------- */
  var themeBtn = $('#theme-btn');
  themeBtn.addEventListener('click', function () {
    var dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme:dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
  });

  /* ---------- القائمة الجانبية على الجوال ---------- */
  var side = $('#sidebar'), scrim = $('#scrim'), menuBtn = $('#menu-btn');
  function menu(open) {
    side.classList.toggle('open', open);
    scrim.classList.toggle('on', open);
    menuBtn.setAttribute('aria-expanded', String(open));
  }
  menuBtn.addEventListener('click', function () { menu(!side.classList.contains('open')); });
  scrim.addEventListener('click', function () { menu(false); });
  side.addEventListener('click', function (e) { if (e.target.closest('a')) menu(false); });

  /* ---------- تمييز القسم الحالي في القائمة ---------- */
  var links = {};
  $$('.sidebar a[data-sec]').forEach(function (a) { links[a.dataset.sec] = a; });
  var current = null;
  function setCurrent(id) {
    if (current === id || !links[id]) return;
    if (current) links[current].classList.remove('on');
    current = id;
    links[id].classList.add('on');
    var l = links[id], top = l.offsetTop, h = side.clientHeight;
    if (top < side.scrollTop + 40 || top > side.scrollTop + h - 60) side.scrollTop = top - h / 3;
  }
  var secs = $$('main > section');
  function spy() {
    var y = 90, pick = secs[0];
    secs.forEach(function (s) { if (s.getBoundingClientRect().top <= y) pick = s; });
    if (pick) setCurrent(pick.id);
  }
  var tick = false;
  addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(function () { tick = false; spy(); }); } }, { passive: true });
  spy();

  /* ---------- فتح العنصر المستهدف (روابط ومعرّفات وبحث) ---------- */
  function openParents(el) {
    for (var p = el; p; p = p.parentElement) if (p.tagName === 'DETAILS') p.open = true;
  }
  function flash(el) {
    el.classList.remove('flash');
    void el.offsetWidth;
    el.classList.add('flash');
    setTimeout(function () { el.classList.remove('flash'); }, 2400);
  }
  function go(el, center) {
    if (!el) return;
    if (el.closest('.mod')) resetCatalog();
    openParents(el);
    el.scrollIntoView({ block: center ? 'center' : 'start', behavior: 'auto' });
    flash(el);
  }
  function fromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (el) go(el, el.tagName === 'DETAILS');
  }
  addEventListener('hashchange', function () { fromHash(); spy(); });
  fromHash();
  addEventListener('load', function () { setTimeout(spy, 60); });

  /* ---------- فتح/إغلاق صفحات اللوحات ---------- */
  $$('main > section').forEach(function (s) {
    var pages = $$('details.page', s);
    if (pages.length < 2) return;
    var bar = document.createElement('div');
    bar.className = 'pgbar';
    bar.innerHTML = '<button type="button" data-o="1">' + T('فتح كل الصفحات', 'Expand all pages') + '</button><button type="button" data-o="0">' + T('إغلاق الكل', 'Collapse all') + '</button>';
    var h2 = $('h2', s);
    var anchor = $('.sub', s) || h2;
    anchor.insertAdjacentElement('afterend', bar);
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (b) pages.forEach(function (d) { d.open = b.dataset.o === '1'; });
    });
  });

  /* ---------- فهرس المتطلبات ---------- */
  var reqs = $$('details.req');
  var q = $('#cat-q'), mod = $('#cat-mod'), pri = $('#cat-pri'), count = $('#cat-count'), empty = $('#cat-empty');
  var priVal = '';
  function nz(s) {
    return (s || '').toLowerCase()
      .replace(/[ً-ٰٟـ]/g, '')
      .replace(/[إأآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
      .replace(/[٠-٩]/g, function (d) { return d.charCodeAt(0) - 1632; });
  }
  reqs.forEach(function (d) { d._t = nz(d.textContent); });
  function filterCatalog() {
    var terms = nz(q.value).split(/\s+/).filter(Boolean), m = mod.value, shown = 0;
    reqs.forEach(function (d) {
      var ok = (!m || d.id.indexOf(m + '-') === 0) &&
        (!priVal || (priVal === 'reg' ? d.dataset.reg === '1' : d.dataset.p === priVal)) &&
        terms.every(function (t) { return d._t.indexOf(t) > -1; });
      d.hidden = !ok;
      if (ok) shown++;
    });
    $$('.mod').forEach(function (s) { s.hidden = !$$('details.req:not([hidden])', s).length; });
    count.textContent = shown === reqs.length ? reqs.length + T(' متطلباً', ' requirements') : shown + T(' من ', ' of ') + reqs.length;
    empty.hidden = shown > 0;
  }
  function resetCatalog() {
    if (!q.value && !mod.value && !priVal) return;
    q.value = ''; mod.value = ''; priVal = '';
    $$('button', pri).forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.v === '')); });
    filterCatalog();
  }
  q.addEventListener('input', filterCatalog);
  mod.addEventListener('change', filterCatalog);
  pri.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    priVal = b.dataset.v;
    $$('button', pri).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    filterCatalog();
  });
  $('#cat-open').addEventListener('click', function () { reqs.forEach(function (d) { if (!d.hidden) d.open = true; }); });
  $('#cat-close').addEventListener('click', function () { reqs.forEach(function (d) { d.open = false; }); });
  filterCatalog();

  /* ---------- البحث الشامل ---------- */
  var sr = $('#sr'), srq = $('#sr-q'), srl = $('#sr-list');
  var index = null, sel = -1, results = [];

  function buildIndex() {
    index = [];
    var head = '';
    $$('main h2, main h3, main h4, main p, main li, main tr, main summary').forEach(function (el) {
      if (el.closest('.cat-tools,.pgbar,.hero,.mock')) return;
      if (el.tagName === 'LI' && el.querySelector('li')) return;
      var text = el.textContent.replace(/\s+/g, ' ').trim();
      if (text.length < 3) return;
      if (el.tagName === 'TR') {
        if (el.querySelector('th')) return;
        text = $$('td', el).map(function (c) { return c.textContent.replace(/\s+/g, ' ').trim(); }).filter(Boolean).join(' — ');
      }
      if (/^H[23]$/.test(el.tagName)) head = text.replace(/^\d+\s*/, '');
      var sec = el.closest('section');
      index.push({ el: el, text: text, n: nz(text), sec: sec ? $('h2', sec).textContent.replace(/^\d+/, '').trim() : '', ctx: head,
                   w: /^H[2-4]$/.test(el.tagName) ? 3 : el.tagName === 'SUMMARY' ? 2 : 0 });
    });
  }
  function esc(s) { return s.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
  function snippet(text, terms) {
    var n = nz(text), pos = -1;
    for (var i = 0; i < terms.length && pos < 0; i++) pos = n.indexOf(terms[i]);
    var start = Math.max(0, pos - 40), s = text.slice(start, start + 150);
    s = (start ? '… ' : '') + s + (start + 150 < text.length ? ' …' : '');
    var out = esc(s);
    terms.forEach(function (t) {
      // النص الأصلي والمطبَّع بنفس الطول غالباً؛ نبحث في النسخة المطبّعة ونظلّل المقابل
      var ns = nz(s), i = 0, parts = [], last = 0, k;
      while ((k = ns.indexOf(t, i)) > -1) { parts.push([k, k + t.length]); i = k + t.length; }
      if (!parts.length || ns.length !== s.length) return;
      var res = '';
      parts.forEach(function (p) { res += esc(s.slice(last, p[0])) + '<mark>' + esc(s.slice(p[0], p[1])) + '</mark>'; last = p[1]; });
      out = res + esc(s.slice(last));
    });
    return out;
  }
  function runSearch() {
    var terms = nz(srq.value).split(/\s+/).filter(Boolean);
    srl.innerHTML = ''; sel = -1; results = [];
    if (!terms.length) { srl.innerHTML = '<div class="sr-empty">' + T('اكتب كلمة أو معرّف متطلب مثل ORD-003', 'Type a word or a requirement ID such as ORD-003') + '</div>'; return; }
    var scored = [];
    index.forEach(function (it) {
      var ok = terms.every(function (t) { return it.n.indexOf(t) > -1; });
      if (!ok) return;
      var sc = it.w + (it.n.indexOf(terms[0]) === 0 ? 2 : 0) - Math.min(it.n.length, 400) / 400;
      scored.push([sc, it]);
    });
    scored.sort(function (a, b) { return b[0] - a[0]; });
    results = scored.slice(0, 40).map(function (x) { return x[1]; });
    if (!results.length) { srl.innerHTML = '<div class="sr-empty">' + T('لا توجد نتائج. جرّب كلمة أخرى.', 'No results. Try another word.') + '</div>'; return; }
    srl.innerHTML = results.map(function (r, i) {
      return '<button type="button" class="sr-item" role="option" data-i="' + i + '"><small>' + esc(r.sec) + (r.ctx && r.ctx !== r.sec ? ' › ' + esc(r.ctx) : '') + '</small><span>' + snippet(r.text, terms) + '</span></button>';
    }).join('');
    select(0);
  }
  function select(i) {
    var items = $$('.sr-item', srl);
    if (!items.length) return;
    sel = (i + items.length) % items.length;
    items.forEach(function (b, k) { b.setAttribute('aria-selected', String(k === sel)); });
    items[sel].scrollIntoView({ block: 'nearest' });
  }
  function openSearch() {
    if (!index) buildIndex();
    sr.hidden = false;
    srq.select();
    runSearch();
    setTimeout(function () { srq.focus(); }, 0);
  }
  function closeSearch() { sr.hidden = true; }
  function choose(i) {
    var r = results[i]; if (!r) return;
    closeSearch();
    setTimeout(function () { go(r.el, true); }, 30);
  }
  $('#search-btn').addEventListener('click', openSearch);
  srq.addEventListener('input', runSearch);
  srl.addEventListener('click', function (e) { var b = e.target.closest('.sr-item'); if (b) choose(+b.dataset.i); });
  sr.addEventListener('mousedown', function (e) { if (e.target === sr) closeSearch(); });
  addEventListener('keydown', function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (!sr.hidden) {
      if (e.key === 'Escape') { closeSearch(); e.preventDefault(); }
      else if (e.key === 'ArrowDown') { select(sel + 1); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { select(sel - 1); e.preventDefault(); }
      else if (e.key === 'Enter') { choose(sel); e.preventDefault(); }
      return;
    }
    if ((e.key === '/' && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) { e.preventDefault(); openSearch(); }
    else if (e.key === 'Escape') menu(false);
  });

  /* ---------- جداول القرارات: تسميات الأعمدة للعرض على الجوال ---------- */
  $$('.dec table').forEach(function (t) {
    var h = $$('thead th', t).map(function (x) { return x.textContent.trim(); });
    $$('tbody tr', t).forEach(function (tr) {
      $$('td', tr).forEach(function (td, i) { td.setAttribute('data-l', h[i] || ''); });
    });
  });


  /* ---------- حاسبة توضيحية للمارت ---------- */
  (function () {
    var out = $('#calc-result');
    if (!out) return;
    var ids = ['base', 'markup', 'rate', 'delivery', 'tip'];
    function v(id) { return Math.max(0, Number($('#calc-' + id).value) || 0); }
    function m(x) { return (Math.round(x * 100) / 100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + T(' ر.س', ' SAR'); }
    function r2(x) { return Math.round(x * 100) / 100; }
    function run() {
      var b = v('base'), mk = v('markup'), rt = v('rate'), dl = v('delivery'), tip = v('tip');
      var products = r2(b * (1 + mk / 100)), fee = r2((products + dl) * 0.025), mf = r2(b * rt / 100), total = r2(products + dl + fee + tip);
      out.innerHTML = '<small>' + T('المطلوب من العميل', 'Customer pays') + '</small><div class="big">' + m(total) + '</div>' +
        '<div class="row"><span>' + T('سعر المنتجات للعميل', 'Product price to customer') + '</span><b>' + m(products) + '</b></div>' +
        '<div class="row"><span>' + T('التوصيل', 'Delivery') + '</span><b>' + m(dl) + '</b></div>' +
        '<div class="row"><span>' + T('خدمة 2.5% دون الإكرامية', 'Service fee 2.5% (excl. tip)') + '</span><b>' + m(fee) + '</b></div>' +
        '<div class="row"><span>' + T('الإكرامية', 'Tip') + '</span><b>' + m(tip) + '</b></div>' +
        '<div class="row"><span>' + T('يصل للمندوب من الإكرامية بعد خصم 15%', 'Tip reaching the driver after 15% deduction') + '</span><b>' + m(r2(tip * 0.85)) + '</b></div>' +
        '<div class="row"><span>' + T('خصم نسبة التاجر', 'Merchant percentage deduction') + '</span><b>' + m(mf) + '</b></div>' +
        '<div class="row"><span>' + T('مستحق المنتجات للتاجر', 'Products due to merchant') + '</span><b>' + m(b - mf) + '</b></div>' +
        '<p>' + T('قبل ضريبة رسوم المنصة وتمويل العروض والاسترداد والغرامة اليدوية. لا رسم دفع إلكتروني للمارت.', 'Before platform-fee VAT, promotion funding, refunds and manual penalties. No online payment fee for Mart.') + '</p>';
    }
    ids.forEach(function (i) { $('#calc-' + i).addEventListener('input', run); });
    run();
  })();

  /* ---------- الطباعة: افتح كل شيء ---------- */
  addEventListener('beforeprint', function () { $$('details').forEach(function (d) { d.open = true; }); });
})();

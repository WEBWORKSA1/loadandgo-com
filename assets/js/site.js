/* LoadandGo.com: navigation, forms, video players, checklist, hero sizer. No dependencies. */
(function () {
  'use strict';
  var C = window.LG_CONFIG || {};
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }

  // menu
  var tog = $('.nav-toggle'), nav = $('#nav');
  if (tog) tog.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    tog.setAttribute('aria-expanded', open);
  });

  // cookie note
  var ck = $('.cookie');
  if (ck && !store('lg:ck')) {
    ck.hidden = false;
    $('button', ck).addEventListener('click', function () { store('lg:ck', 1); ck.hidden = true; });
  }

  // hero sizer on the home page
  var hr = $('#ht-rooms');
  if (hr) {
    var TR = [['Cargo van', 245], ['10 ft box truck', 400], ['12 ft box truck', 450], ['15 to 16 ft box truck', 760], ['20 ft box truck', 1000], ['22 ft box truck', 1200], ['26 ft box truck', 1650]];
    var sizer = function () {
      var rooms = +hr.value, need = rooms * 175 / 0.9, pick = TR[TR.length - 1];
      for (var i = 0; i < TR.length; i++) if (TR[i][1] >= need) { pick = TR[i]; break; }
      var pct = Math.min(1, need / pick[1]);
      $('#ht-n').textContent = rooms + (rooms === 1 ? ' furnished room' : ' furnished rooms');
      $('#ht-truck').textContent = need > 1650 ? '26 ft truck, plus a trailer' : pick[0];
      $('#ht-cuft').textContent = 'About ' + Math.round(need / 10) * 10 + ' cubic feet of cargo, which fills ' + Math.round(pct * 100) + '% of that truck.';
      $('#ht-fill').setAttribute('width', Math.round(318 * pct));
    };
    hr.addEventListener('input', sizer); sizer();
  }

  // video players load only when asked
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.vid-play');
    if (!b) return;
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(b.getAttribute('data-yt')) + '?autoplay=1&rel=0';
    f.title = b.getAttribute('aria-label').replace('Play video: ', '');
    f.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.setAttribute('allowfullscreen', '');
    b.parentNode.replaceChild(f, b);
  });

  // checklist
  $$('[data-checklist]').forEach(function (box) {
    var key = 'lg:check:' + box.getAttribute('data-checklist'), state = store(key) || {}, boxes = $$('[data-check]', box);
    function paint() {
      var done = boxes.filter(function (b) { return b.checked; }).length;
      $('.bar i', box).style.width = (done / boxes.length * 100) + '%';
      $('.count', box).textContent = done + ' of ' + boxes.length + ' done';
    }
    boxes.forEach(function (b) {
      b.checked = !!state[b.getAttribute('data-check')];
      b.addEventListener('change', function () { state[b.getAttribute('data-check')] = b.checked; store(key, state); paint(); });
    });
    var reset = $('[data-reset]', box);
    if (reset) reset.addEventListener('click', function () { state = {}; store(key, state); boxes.forEach(function (b) { b.checked = false; }); paint(); });
    paint();
  });

  // config-driven text and payment buttons
  $$('[data-config]').forEach(function (el) { var v = C[el.getAttribute('data-config')]; if (v) el.textContent = v; });
  var pay = $('#pay-links');
  if (pay && C.payments) {
    var names = { paypal: 'Give with PayPal', stripe: 'Give by card', kofi: 'Give on Ko-fi', buymeacoffee: 'Buy us a coffee' }, any = false;
    Object.keys(names).forEach(function (k) {
      var u = C.payments[k];
      if (u && /^https:\/\//.test(u)) { any = true; var a = document.createElement('a'); a.className = 'btn'; a.href = u; a.rel = 'noopener'; a.target = '_blank'; a.textContent = names[k]; pay.appendChild(a); }
    });
    if (!any) pay.hidden = true;
  }

  // forms: sent through the relay to the encoded inbox; the address is never written into a page
  function inbox() {
    return C._v.map(function (x, i) { return String.fromCharCode((x - (i % 7)) ^ C._k[i % C._k.length]); }).join('');
  }
  function valid(scope) {
    var ok = true;
    $$('input,select,textarea', scope).forEach(function (el) {
      if (el.className === 'hp') return;
      var good = el.checkValidity();
      el.classList.toggle('invalid', !good);
      if (!good && ok) { ok = false; el.focus(); }
    });
    return ok;
  }
  $$('.js-form').forEach(function (form) {
    var msg = $('.form-msg', form), btn = $('button[type=submit]', form), sets = $$('fieldset', form), step = 0;
    var pre = new URLSearchParams(location.search).get('topic');
    if (pre && form.elements.topic) form.elements.topic.value = pre;
    if (form.classList.contains('steps') && sets.length > 1) {
      var foot = $('.form-foot', form), navEl = document.createElement('div');
      navEl.className = 'step-nav';
      navEl.innerHTML = '<button type="button" class="btn alt" data-back>Back</button><button type="button" class="btn" data-next>Next</button><p class="step-count"></p>';
      form.insertBefore(navEl, foot);
      var show = function () {
        sets.forEach(function (s, i) { s.hidden = i !== step; });
        $('[data-back]', navEl).hidden = step === 0;
        $('[data-next]', navEl).hidden = step === sets.length - 1;
        btn.hidden = step !== sets.length - 1;
        $('.step-count', navEl).textContent = 'Step ' + (step + 1) + ' of ' + sets.length;
      };
      $('[data-next]', navEl).addEventListener('click', function () { if (valid(sets[step])) { step++; show(); sets[step].querySelector('input,select,textarea').focus(); } else { msg.textContent = 'Fill in the highlighted fields to continue.'; msg.className = 'form-msg bad'; } });
      $('[data-back]', navEl).addEventListener('click', function () { step--; show(); });
      show();
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!valid(form)) { msg.textContent = 'Fill in the highlighted fields, then send again.'; msg.className = 'form-msg bad'; return; }
      var data = {};
      $$('input,select,textarea', form).forEach(function (el) {
        if (!el.name) return;
        if (el.type === 'checkbox') { if (el.checked) data[el.name] = 'yes'; } else if (el.value) data[el.name] = el.value;
      });
      if (data._honey) { form.classList.add('sent'); return; }
      data._subject = '[' + (C.site || 'Site') + '] ' + form.getAttribute('data-subject');
      data._template = 'table';
      data._captcha = 'false';
      data.form = form.getAttribute('data-form');
      data.page = location.href;
      btn.disabled = true; msg.className = 'form-msg'; msg.textContent = 'Sending…';
      fetch(C.relay + inbox(), { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function () {
          form.classList.add('sent');
          var done = document.createElement('p');
          done.className = 'form-done'; done.setAttribute('role', 'status');
          done.textContent = form.getAttribute('data-done');
          form.appendChild(done);
        })
        .catch(function () {
          btn.disabled = false; msg.className = 'form-msg bad';
          msg.textContent = 'That did not send. Check your connection and send again, or use the contact link at the top of the page.';
        });
    });
  });
})();

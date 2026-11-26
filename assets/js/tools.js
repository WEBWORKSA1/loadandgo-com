/* LoadandGo.com calculators. Each tool reads the form values and returns a ticket:
   {label, big, gauge:[percent, caption], rows:[[name, value]], notes:[], warn}. */
(function () {
  'use strict';
  var form = document.querySelector('form[data-tool]');
  if (!form) return;
  var slug = form.getAttribute('data-tool'), out = document.getElementById('ticket'), KEY = 'lg:' + slug, FUEL = window.LG_FUEL || {};
  var DASH = '—';
  function n0(x) { return isFinite(x) ? Math.round(x).toLocaleString('en-US') : DASH; }
  function n1(x) { return isFinite(x) ? (Math.round(x * 10) / 10).toLocaleString('en-US') : DASH; }
  function n2(x) { return isFinite(x) ? x.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : DASH; }
  function usd(x) { return isFinite(x) ? '$' + n2(x) : DASH; }
  function usd0(x) { return isFinite(x) ? '$' + n0(x) : DASH; }
  function z(x) { x = parseFloat(x); return isFinite(x) && x > 0 ? x : 0; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var TRUCKS = [['Cargo van', 245], ['10 ft box truck', 400], ['12 ft box truck', 450], ['15–16 ft box truck', 760], ['20 ft box truck', 1000], ['22 ft box truck', 1200], ['26 ft box truck', 1650]];
  // interior length, width, height in inches, typical payload in lb
  var SPACES = {
    v53: [630, 100, 110, 45000, '53 ft dry van'], v48: [570, 100, 110, 45000, '48 ft dry van'],
    b26: [312, 96, 96, 10000, '26 ft box truck'], b16: [192, 92, 84, 4300, '16 ft box truck'], b10: [118, 76, 73, 2800, '10 ft box truck'],
    c20: [232, 92, 94, 44000, '20 ft container'], c40: [473, 92, 94, 44000, '40 ft container'], h40: [473, 92, 106, 44000, '40 ft high-cube container']
  };
  function space(v) {
    var s = SPACES[v.space];
    return s ? { l: s[0], w: s[1], h: s[2], max: z(v.smax) || s[3], name: s[4] } : { l: z(v.sl) * 12, w: z(v.sw) * 12, h: z(v.sh) * 12, max: z(v.smax), name: 'your space' };
  }
  var CLASSES = [[1, '400'], [2, '300'], [4, '250'], [6, '175'], [8, '125'], [10, '100'], [12, '92.5'], [15, '85'], [22.5, '70'], [30, '65'], [35, '60'], [50, '55'], [Infinity, '50']];
  var T = {};

  T['truck-size-calculator'] = function (v) {
    var skill = parseFloat(v.skill), goods = z(v.rooms) * parseFloat(v.fill) + z(v.boxes) * 3 + z(v.appl) * 35 + parseFloat(v.extra), need = goods / skill;
    if (!goods) return null;
    var pick = null, next = null;
    for (var i = 0; i < TRUCKS.length; i++) if (TRUCKS[i][1] >= need) { pick = TRUCKS[i]; next = TRUCKS[i + 1]; break; }
    var cap = pick ? pick[1] : 1650, pct = need / cap * 100, notes = [];
    if (pick && pct > 90 && next) notes.push('You are within 10% of full. The ' + next[0] + ' gives you room for the things you forgot to count.');
    notes.push('Truck volumes are typical figures for each size class. Check the cubic feet on your rental company’s spec sheet.');
    return {
      label: 'Recommended size', big: pick ? pick[0] : 'More than one 26 ft truck',
      gauge: [pct, 'of a typical ' + n0(cap) + ' cu ft cargo box'],
      rows: [['Truck space needed', n0(need) + ' cu ft'], ['Volume of your goods', n0(goods) + ' cu ft'], ['Estimated weight at 7 lb per cu ft', n0(goods * 7) + ' lb'], ['Portable containers of about 800 cu ft', String(Math.ceil(need / 800))]],
      notes: notes,
      warn: pick ? '' : 'This load is bigger than the largest rental box truck. Plan a second trip, tow a cargo trailer, or price containers or a full-service mover.'
    };
  };

  T['diy-moving-cost-calculator'] = function (v) {
    var miles = z(v.miles), gal = v.mpg > 0 ? miles / v.mpg : 0;
    var truck = z(v.days) * z(v.rate) + miles * z(v.permile), fuel = gal * z(v.price), help = z(v.helpers) * z(v.hours) * z(v.hourly), cover = z(v.days) * z(v.cover);
    var total = truck + fuel + help + cover + z(v.supplies) + z(v.extras);
    if (!total) return null;
    var rows = [['Truck rental', usd(truck)], ['Fuel, ' + n1(gal) + ' gal', usd(fuel)], ['Loading and unloading help', usd(help)], ['Damage cover', usd(cover)], ['Boxes and supplies', usd(z(v.supplies))], ['Tolls, lodging and food', usd(z(v.extras))]], notes = [];
    if (v.quote > 0) {
      var d = v.quote - total;
      rows.push(['Full-service quote', usd(v.quote)]);
      notes.push(d > 0 ? 'Doing it yourself saves about ' + usd0(d) + ' before you count your own time and sore back.' : 'The full-service quote is ' + usd0(-d) + ' cheaper than doing it yourself.');
    }
    notes.push('Replace every default with the figures on your own rental quote. One-way rentals are often a flat price with miles included: put it in the daily rate and set the mileage charge to 0.');
    return { label: 'Your DIY move budget', big: usd0(total), rows: rows, notes: notes };
  };

  T['payload-calculator'] = function (v) {
    var cap = z(v.placard) || (z(v.gvwr) - z(v.curb));
    if (!(cap > 0)) return null;
    var used = z(v.people) + z(v.gear) + z(v.tongue) + z(v.cargo), left = cap - used;
    return {
      label: left >= 0 ? 'Payload still available' : 'Over the payload rating by', big: n0(Math.abs(left)) + ' lb',
      gauge: [used / cap * 100, 'of the ' + n0(cap) + ' lb payload rating'],
      rows: [['Payload rating', n0(cap) + ' lb'], ['People', n0(z(v.people)) + ' lb'], ['Accessories and gear', n0(z(v.gear)) + ' lb'], ['Trailer tongue weight', n0(z(v.tongue)) + ' lb'], ['Cargo', n0(z(v.cargo)) + ' lb']],
      notes: ['The yellow tire and loading sticker on the driver door jamb is the number for your exact truck as built. Use it over any brochure figure.', 'Staying under payload does not guarantee each axle is under its own rating. Keep heavy items ahead of the rear axle.'],
      warn: left < 0 ? 'Overloaded. Remove ' + n0(-left) + ' lb, split the load into two trips, or use a vehicle with a higher rating.' : ''
    };
  };

  T['towing-capacity-calculator'] = function (v) {
    var lims = [];
    if (z(v.gcwr) && z(v.vehicle)) lims.push([z(v.gcwr) - z(v.vehicle), 'combined weight rating (GCWR minus loaded vehicle)']);
    if (z(v.towrating)) lims.push([z(v.towrating), 'vehicle tow rating']);
    if (z(v.hitch)) lims.push([z(v.hitch), 'hitch rating']);
    if (!lims.length) return null;
    lims.sort(function (a, b) { return a[0] - b[0]; });
    var lim = lims[0], tr = z(v.trailer), fifth = v.type === 'fifth', lo = fifth ? .15 : .10, hi = fifth ? .25 : .15;
    var rows = lims.map(function (l) { return ['Limit from ' + l[1], n0(l[0]) + ' lb']; });
    if (tr) rows.push(['Loaded trailer', n0(tr) + ' lb'], ['Target ' + (fifth ? 'pin' : 'tongue') + ' weight', n0(tr * lo) + ' to ' + n0(tr * hi) + ' lb']);
    return {
      label: 'Heaviest trailer you can pull', big: n0(Math.max(0, lim[0])) + ' lb',
      gauge: tr ? [tr / lim[0] * 100, 'of your limit, set by the ' + lim[1]] : null,
      rows: rows,
      notes: ['Your limit is the lowest-rated part of the system: vehicle, hitch, ball mount, ball or trailer. Check the stamp on each one.', (fifth ? 'Pin' : 'Tongue') + ' weight rides on the tow vehicle, so it counts against payload along with passengers and cargo.'],
      warn: tr > lim[0] ? 'Too heavy by ' + n0(tr - lim[0]) + ' lb. Lighten the trailer or the tow vehicle before you go.' : ''
    };
  };

  T['fuel-cost-calculator'] = function (v) {
    var miles = z(v.miles) * (v.round ? 2 : 1);
    if (!miles || !z(v.mpg)) return null;
    var gal = miles / v.mpg, cost = gal * z(v.price), rows = [['Distance driven', n0(miles) + ' mi'], ['Fuel burned', n1(gal) + ' gal'], ['Cost per mile', usd(cost / miles)]];
    if (z(v.tank)) rows.push(['Range per tank', n0(v.tank * v.mpg) + ' mi'], ['Fill-ups needed', String(Math.max(0, Math.ceil(gal / v.tank - 1e-9)))]);
    return { label: 'Fuel for this trip', big: usd(cost), rows: rows, notes: ['Use the mileage you get loaded, not the window sticker. A full box truck or a trailer in tow often burns far more than the same vehicle empty.'] };
  };

  T['tie-down-calculator'] = function (v) {
    var w = z(v.weight), len = z(v.length), wll = z(v.wll), f = parseFloat(v.method);
    if (!w || !len || !wll) return null;
    var byLen = v.blocked ? Math.ceil(len / 10) : (len <= 5 ? (w <= 1100 ? 1 : 2) : len <= 10 ? 2 : 2 + Math.ceil((len - 10) / 10));
    var need = w * .5, byWll = Math.ceil(need / (wll * f) - 1e-9), n = Math.max(byLen, byWll, 1);
    return {
      label: 'Minimum tie-downs', big: String(n),
      gauge: [need / (n * wll * f) * 100, 'of the restraint those ' + n + ' tie-downs provide'],
      rows: [['Needed by length and weight', String(byLen)], ['Needed for working load limit', String(byWll)], ['Aggregate working load limit required', n0(need) + ' lb'], ['Each tie-down counts for', n0(wll * f) + ' lb']],
      notes: ['Working load limit is printed on the strap tag or stamped on the chain. It is about one third of breaking strength, so never plan with the breaking number.', 'These are the federal minimums for commercial trucks in 49 CFR 393.106 and 393.110. They are a sound floor for a pickup or utility trailer too. Add more for tall, slick or top-heavy cargo.'],
      warn: n === 1 ? 'One strap meets the minimum, but a single strap lets cargo pivot. Use two.' : ''
    };
  };

  T['freight-class-calculator'] = function (v) {
    var cf = z(v.l) * z(v.w) * z(v.h) / 1728 * (z(v.pieces) || 1), wt = z(v.weight) * (z(v.pieces) || 1);
    if (!cf || !wt) return null;
    var d = wt / cf, cls = '50';
    for (var i = 0; i < CLASSES.length; i++) if (d < CLASSES[i][0]) { cls = CLASSES[i][1]; break; }
    return {
      label: 'Estimated freight class', big: 'Class ' + cls,
      rows: [['Density', n2(d) + ' lb per cu ft'], ['Total volume', n1(cf) + ' cu ft'], ['Total weight', n0(wt) + ' lb']],
      notes: ['Measure the longest, widest and tallest points including the pallet and any overhang. Carriers re-measure at the dock and bill the difference.', 'This uses the standard 13-step density scale. Items with special handling, stowability or liability rules can carry a different class, so confirm the NMFC item with your carrier before you ship.']
    };
  };

  T['pallet-calculator'] = function (v) {
    var s = space(v), pl = z(v.pl), pw = z(v.pw);
    if (!pl || !pw || !s.l || !s.w) return null;
    var a = Math.floor(s.l / pl) * Math.floor(s.w / pw), b = Math.floor(s.l / pw) * Math.floor(s.w / pl), floor = Math.max(a, b), tiers = v.stack ? 2 : 1;
    if (v.stack && z(v.ph) && s.h) tiers = Math.max(1, Math.min(2, Math.floor(s.h / v.ph)));
    var fit = floor * tiers, byWt = z(v.pwt) && s.max ? Math.floor(s.max / v.pwt) : Infinity, n = Math.min(fit, byWt);
    return {
      label: 'Pallets that fit in a ' + s.name, big: String(n),
      gauge: z(v.pwt) && s.max ? [n * v.pwt / s.max * 100, 'of the ' + n0(s.max) + ' lb payload'] : null,
      rows: [['Loaded straight', String(a) + ' on the floor'], ['Turned sideways', String(b) + ' on the floor'], ['Tiers', String(tiers)], ['Limit by space', String(fit)], ['Limit by weight', isFinite(byWt) ? String(byWt) : 'not set'], ['Total weight', z(v.pwt) ? n0(n * v.pwt) + ' lb' : DASH]],
      notes: ['Counts assume square pallets with no overhang. Leave an inch or two of working room per row.', byWt < fit ? 'Weight runs out before floor space. This load will “weigh out” before it “cubes out”.' : 'Space runs out before weight. Lighter freight like this is priced by the room it takes.']
    };
  };

  T['box-fit-calculator'] = function (v) {
    var s = space(v), d = [z(v.bl), z(v.bw), z(v.bh)];
    if (!d[0] || !d[1] || !d[2] || !s.l || !s.w || !s.h) return null;
    var P = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]], best = 0, bo = P[0];
    P.forEach(function (p) {
      if (v.upright && p[2] !== 2) return;
      var c = Math.floor(s.l / d[p[0]]) * Math.floor(s.w / d[p[1]]) * Math.floor(s.h / d[p[2]]);
      if (c > best) { best = c; bo = p; }
    });
    var byWt = z(v.bwt) && s.max ? Math.floor(s.max / v.bwt) : Infinity, n = Math.min(best, byWt), vol = d[0] * d[1] * d[2];
    return {
      label: 'Boxes that fit in a ' + s.name, big: n0(n),
      gauge: [n * vol / (s.l * s.w * s.h) * 100, 'of the space filled'],
      rows: [['Best layout (long × wide × high)', Math.floor(s.l / d[bo[0]]) + ' × ' + Math.floor(s.w / d[bo[1]]) + ' × ' + Math.floor(s.h / d[bo[2]])], ['Limit by space', n0(best)], ['Limit by weight', isFinite(byWt) ? n0(byWt) : 'not set'], ['Total weight', z(v.bwt) ? n0(n * v.bwt) + ' lb' : DASH]],
      notes: ['All boxes face the same way in this count. Mixing orientations in the last row can squeeze in a few more.']
    };
  };

  T['cubic-feet-calculator'] = function (v) {
    var k = { 'in': 1 / 12, ft: 1, cm: 1 / 30.48, m: 3.28084 }[v.unit] || 1, cf = z(v.l) * k * z(v.w) * k * z(v.h) * k * (z(v.qty) || 1);
    if (!cf) return null;
    var rows = [['Cubic yards', n2(cf / 27)], ['Cubic metres', n2(cf * 0.0283168)], ['Litres', n0(cf * 28.3168)]];
    if (z(v.weight)) rows.push(['Density', n2(z(v.weight) * (z(v.qty) || 1) / cf) + ' lb per cu ft']);
    var fit = TRUCKS.filter(function (t) { return t[1] >= cf; })[0];
    return { label: 'Volume', big: n1(cf) + ' cu ft', rows: rows, notes: [fit ? 'That would fit in a ' + fit[0].toLowerCase() + ' with ' + n0(fit[1] - cf) + ' cu ft to spare, if nothing else is going.' : 'That is more than one 26 ft box truck holds.'] };
  };

  T['bulk-material-calculator'] = function (v) {
    var yd = z(v.len) * z(v.wid) * (z(v.depth) / 12) / 27, dens = parseFloat(v.material);
    if (!yd) return null;
    var wt = yd * dens, pay = z(v.payload), bed = z(v.bed), perLoad = Math.min(bed || Infinity, pay ? pay / dens : Infinity);
    var loads = isFinite(perLoad) && perLoad > 0 ? Math.ceil(yd / perLoad - 1e-9) : NaN, full = bed * dens;
    return {
      label: 'Material to order', big: n1(yd) + ' cu yd',
      gauge: pay && bed ? [full / pay * 100, 'of payload if you fill the bed level'] : null,
      rows: [['Weight', n0(wt) + ' lb (' + n1(wt / 2000) + ' tons)'], ['Safe amount per trip', isFinite(perLoad) ? n2(perLoad) + ' cu yd' : DASH], ['Trips with your truck', isFinite(loads) ? String(loads) : DASH], ['A level bed would weigh', bed ? n0(full) + ' lb' : DASH]],
      notes: ['Weights are typical for dry to damp material. Wet soil, sand and gravel run heavier, so leave a margin.', 'Order 5 to 10% extra to cover settling and uneven ground.'],
      warn: pay && bed && full > pay ? 'A level bed of this material overloads your truck. Ask the yard to load ' + n2(pay / dens) + ' cu yd per trip, about ' + n0(pay / dens / bed * 100) + '% of the bed.' : ''
    };
  };

  T['cost-per-mile-calculator'] = function (v) {
    var miles = z(v.miles);
    if (!miles) return null;
    var fixed = (z(v.payment) + z(v.insurance) + z(v.otherfixed)) / miles, fuel = z(v.mpg) ? z(v.price) / v.mpg : 0, cpm = fixed + fuel + z(v.maint) + z(v.pay);
    var rows = [['Fixed costs', usd(fixed) + ' per mi'], ['Fuel', usd(fuel) + ' per mi'], ['Maintenance and tires', usd(z(v.maint)) + ' per mi'], ['Driver pay', usd(z(v.pay)) + ' per mi'], ['Monthly cost at ' + n0(miles) + ' mi', usd0(cpm * miles)]], notes = [], warn = '';
    var all = z(v.loaded) + z(v.deadhead);
    if (z(v.rate) && all) {
      var per = v.rate / all, profit = v.rate - cpm * all;
      rows.push(['This load pays, all miles', usd(per) + ' per mi'], ['Profit on this load', usd0(profit)]);
      if (profit < 0) warn = 'This load loses ' + usd0(-profit) + '. You need at least ' + usd0(cpm * all) + ' to break even on ' + n0(all) + ' total miles.';
      else notes.push('Break-even for this run is ' + usd0(cpm * all) + '. Everything above that is yours.');
    }
    notes.push('Count every mile you drive, loaded or empty. Deadhead miles cost the same to run and pay nothing.');
    return { label: 'Your cost to run one mile', big: usd(cpm), rows: rows, notes: notes, warn: warn };
  };

  T['packing-box-calculator'] = function (v) {
    var boxes = Math.round(z(v.rooms) * parseFloat(v.style) + z(v.people) * 5);
    if (!boxes) return null;
    var s = Math.round(boxes * .4), m = Math.round(boxes * .35), l = boxes - s - m, ward = Math.ceil(z(v.people) * 1.5);
    return {
      label: 'Boxes to pack', big: String(boxes),
      rows: [['Small, 1.5 cu ft, for books and heavy items', String(s)], ['Medium, 3 cu ft, for kitchen and general', String(m)], ['Large, 4.5 cu ft, for bedding and light bulky items', String(l)], ['Wardrobe boxes', String(ward)], ['Rolls of packing tape', String(Math.ceil(boxes / 15))], ['Space the boxes take', n0(s * 1.5 + m * 3 + l * 4.5) + ' cu ft']],
      notes: ['This is a starting count from a simple rule: a set number of boxes per room, plus five per person. Buy from a seller that takes back unused boxes.', 'Heavy things go in small boxes. If you cannot lift it comfortably, it is the wrong box.']
    };
  };

  // ---------------------------------------------------------------- engine
  function read() {
    var v = {};
    [].forEach.call(form.elements, function (e) {
      if (!e.name) return;
      v[e.name] = e.type === 'checkbox' ? e.checked : e.type === 'number' ? (e.value === '' ? NaN : parseFloat(e.value)) : e.value;
    });
    return v;
  }
  function apply(o, all) {
    Object.keys(o).forEach(function (k) {
      var e = form.elements[k];
      if (!e || (k === 'price' && !all && !o._pu)) return;
      if (e.type === 'checkbox') e.checked = o[k] === true || o[k] === '1' || o[k] === 'true'; else e.value = o[k];
    });
  }
  function setPrice(force) {
    var p = form.elements.price, f = form.elements.fuel;
    if (!p || !f || (p.dataset.user && !force)) return;
    var set = FUEL[f.value] || {}, val = set[(form.elements.region || {}).value] || set.US;
    if (val) p.value = val;
  }
  function text(t) {
    var lines = [t.label + ': ' + t.big];
    (t.rows || []).forEach(function (r) { lines.push(r[0] + ': ' + r[1]); });
    if (t.warn) lines.push(t.warn);
    lines.push('From ' + location.href.split('?')[0]);
    return lines.join('\n');
  }
  var last = null;
  function run() {
    var v = read(), t = null;
    try { t = T[slug](v); } catch (e) { t = null; }
    last = t;
    try { var s = {}; [].forEach.call(form.elements, function (e) { if (e.name) s[e.name] = e.type === 'checkbox' ? e.checked : e.value; }); if (form.elements.price && form.elements.price.dataset.user) s._pu = 1; localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* storage is optional */ }
    if (!t) { out.innerHTML = '<p class="tk-wait">Enter your numbers and the result prints here.</p>'; return; }
    var h = '<div class="tk-head"><span>LoadandGo.com load ticket</span><span>' + new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + '</span></div>';
    h += '<p class="tk-label">' + esc(t.label) + '</p><p class="tk-big">' + esc(t.big) + '</p>';
    if (t.gauge && isFinite(t.gauge[0])) {
      var p = t.gauge[0];
      h += '<div class="gauge' + (p > 100 ? ' over' : p > 85 ? ' near' : '') + '" role="img" aria-label="' + n0(p) + ' percent ' + esc(t.gauge[1]) + '"><i style="width:' + Math.min(p, 125) / 1.25 + '%"></i><b></b></div><p class="tk-g">' + n0(p) + '% ' + esc(t.gauge[1]) + '</p>';
    }
    if (t.warn) h += '<p class="tk-warn">' + esc(t.warn) + '</p>';
    h += '<table><tbody>' + (t.rows || []).map(function (r) { return '<tr><td>' + esc(r[0]) + '</td><td>' + esc(r[1]) + '</td></tr>'; }).join('') + '</tbody></table>';
    if (t.notes && t.notes.length) h += '<ul class="tk-notes">' + t.notes.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    h += '<div class="tk-actions"><button type="button" class="btn alt small" data-act="copy">Copy result</button><button type="button" class="btn alt small" data-act="link">Copy link</button><button type="button" class="btn alt small" data-act="print">Print</button></div>';
    out.innerHTML = h;
  }
  out.addEventListener('click', function (e) {
    var act = e.target.getAttribute && e.target.getAttribute('data-act');
    if (!act) return;
    if (act === 'print') return window.print();
    var q = [].filter.call(form.elements, function (el) { return el.name; }).map(function (el) { return encodeURIComponent(el.name) + '=' + encodeURIComponent(el.type === 'checkbox' ? (el.checked ? 1 : 0) : el.value); }).join('&');
    var val = act === 'copy' ? text(last) : location.href.split('?')[0] + '?' + q, b = e.target, old = b.textContent;
    var ok = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = old; }, 1400); };
    if (navigator.clipboard) navigator.clipboard.writeText(val).then(ok, function () { window.prompt('Copy this:', val); }); else window.prompt('Copy this:', val);
  });

  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (saved) { apply(saved, false); if (saved._pu && form.elements.price) form.elements.price.dataset.user = 1; }
  } catch (e) { /* storage is optional */ }
  if (location.search.length > 1) {
    var o = {};
    new URLSearchParams(location.search).forEach(function (val, k) { o[k] = val; });
    apply(o, true);
    if (o.price && form.elements.price) form.elements.price.dataset.user = 1;
  }
  setPrice(false);
  form.addEventListener('input', function (e) {
    if (e.target.name === 'price') e.target.dataset.user = 1;
    if (e.target.name === 'fuel' || e.target.name === 'region') setPrice(true);
    if (e.target.name === 'space') { var c = form.querySelector('[name=smax]'); if (c) c.value = (SPACES[e.target.value] || [])[3] || ''; }
    run();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  run();
})();

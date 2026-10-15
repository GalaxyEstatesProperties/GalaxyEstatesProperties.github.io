/**
 * Galaxy Estates Properties: land listings back end (Google Apps Script, free).
 *
 * What it does
 *  - Receives "Post your land" submissions from galaxyestatesproperties.co.in/land.html
 *  - Re-checks them on the server (phone, map link, boundary, area against the 7/12, location),
 *    saves them in this Google Sheet and emails you every submission with the seller's phone.
 *  - Publishes only listings whose Status is LIVE (or SOLD). Phone and email are never published.
 *
 * Setup (5 minutes, once)
 *  1. Create a new Google Sheet (sheets.new) named "Galaxy Estates land listings".
 *  2. Extensions → Apps Script. Delete the sample code and paste this whole file. Save.
 *  3. Deploy → New deployment → type "Web app".
 *     Execute as: Me.  Who has access: Anyone.  Deploy, allow the permissions it asks for.
 *  4. Copy the Web app URL (https://script.google.com/macros/s/…/exec) and send it to your web developer
 *     (it goes into LAND_API in tools/land_build.py).
 *
 * Managing listings: in the "Listings" sheet change the Status column to
 *   LIVE (shown), HIDDEN (not shown), SOLD (shown as sold) or REVIEW (waiting for you).
 */
var OWNER_EMAIL = 'samirdabhi2309@gmail.com';
var SHEET_NAME = 'Listings';
var COLS = ['id', 'created', 'status', 'checks', 'name', 'phone', 'email', 'role', 'type', 'district', 'taluka', 'village', 'survey', 'pcard', 'tp',
  'areaValue', 'areaUnit', 'areaDeclaredM2', 'areaDrawnM2', 'price', 'priceUnit', 'auth', 'zone', 'road', 'corridor', 'link', 'linkLat', 'linkLng', 'poly', 'notes'];
var PUBLIC = ['id', 'created', 'status', 'checks', 'role', 'type', 'district', 'taluka', 'village', 'survey', 'pcard', 'tp', 'areaValue', 'areaUnit',
  'price', 'priceUnit', 'auth', 'zone', 'road', 'corridor', 'link', 'poly', 'notes'];
var UNIT_M2 = { sqm: 1, sqyd: 0.83612736, sqft: 0.09290304, guntha: 101.17141056, vigha16: 1618.74256896, vigha20: 2023.4282112, acre: 4046.8564224, hectare: 10000 };
var AUTH = { AUDA: [23.03, 72.57, 48], GUDA: [23.22, 72.65, 30], SUDA: [21.18, 72.83, 40], VUDA: [22.31, 73.18, 32], RUDA: [22.30, 70.80, 32], TOWN: null, OUT: null, UNSURE: null };
var ROADS = ['none', 'r6', 'r9', 'r12', 'r18', 'r36', 'r45'];
var PRICE_UNITS = ['total', 'sqyd', 'sqm', 'vigha16', 'acre'];

/* ---------------- pure helpers (also unit-tested outside Google) ---------------- */
function toM2(value, unit) {
  var v = String(value || '').trim();
  if (unit === 'has') {
    var m = v.match(/^(\d+)\s*[-.:/ ]\s*(\d{1,2})\s*[-.:/ ]\s*(\d{1,2})$/);
    if (!m || +m[2] > 99 || +m[3] > 99) return NaN;
    return (+m[1]) * 10000 + (+m[2]) * 100 + (+m[3]);
  }
  if (!UNIT_M2[unit]) return NaN;
  var n = parseFloat(v.replace(/,/g, ''));
  return n > 0 ? n * UNIT_M2[unit] : NaN;
}
function rad(d) { return d * Math.PI / 180; }
function project(poly) {
  var lat0 = 0, lng0 = 0, i;
  for (i = 0; i < poly.length; i++) { lat0 += poly[i][0]; lng0 += poly[i][1]; }
  lat0 /= poly.length; lng0 /= poly.length;
  var k = Math.cos(rad(lat0)), R = 6371008.8;
  return poly.map(function (p) { return [R * rad(p[1] - lng0) * k, R * rad(p[0] - lat0)]; });
}
function polyArea(poly) {
  var p = project(poly), a = 0;
  for (var i = 0; i < p.length; i++) { var q = p[(i + 1) % p.length]; a += p[i][0] * q[1] - q[0] * p[i][1]; }
  return Math.abs(a / 2);
}
function selfIntersects(poly) {
  var p = project(poly), n = p.length;
  function cross(a, b, c) { return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]); }
  for (var i = 0; i < n; i++) for (var j = i + 1; j < n; j++) {
    if (Math.abs(i - j) <= 1 || (i === 0 && j === n - 1)) continue;
    var a = p[i], b = p[(i + 1) % n], c = p[j], d = p[(j + 1) % n];
    if (cross(a, b, c) * cross(a, b, d) < 0 && cross(c, d, a) * cross(c, d, b) < 0) return true;
  }
  return false;
}
function centroid(poly) {
  var la = 0, ln = 0;
  poly.forEach(function (p) { la += p[0]; ln += p[1]; });
  return [la / poly.length, ln / poly.length];
}
function distM(a, b) { var k = Math.cos(rad((a[0] + b[0]) / 2)); return 6371008.8 * Math.sqrt(Math.pow(rad(b[0] - a[0]), 2) + Math.pow(rad(b[1] - a[1]) * k, 2)); }
function inGujarat(p) { return p[0] > 20.0 && p[0] < 24.8 && p[1] > 68.0 && p[1] < 74.6; }
function coordsFromText(s) {
  s = String(s || '');
  var pats = [/!3d(-?\d{1,2}\.\d+)!4d(-?\d{1,3}\.\d+)/, /@(-?\d{1,2}\.\d+),\s*(-?\d{1,3}\.\d+)/,
    /[?&](?:q|ll|query|center|destination|daddr)=(-?\d{1,2}\.\d+)(?:,|%2C)\s*\+?(-?\d{1,3}\.\d+)/i, /\/search\/(-?\d{1,2}\.\d+),\+?(-?\d{1,3}\.\d+)/];
  for (var i = 0; i < pats.length; i++) { var m = s.match(pats[i]); if (m) return [+m[1], +m[2]]; }
  return null;
}
function mapsLinkOk(s) {
  var m = String(s || '').trim().match(/^https:\/\/([^\/?#]+)(\/[^\s]*)?$/i);
  if (!m) return false;
  var host = m[1].toLowerCase(), path = m[2] || '';
  if (host === 'maps.app.goo.gl') return true;
  if (host === 'goo.gl') return /^\/maps/.test(path);
  if (/^maps\.google\.[a-z.]+$/.test(host)) return true;
  if (/^(www\.)?google\.[a-z.]+$/.test(host)) return /^\/maps(\/|\?|$)/.test(path);
  return false;
}
function validPhone(v) {
  var d = String(v || '').replace(/\D/g, '');
  if (d.length === 12 && d.indexOf('91') === 0) d = d.slice(2);
  if (d.length === 11 && d.charAt(0) === '0') d = d.slice(1);
  if (!/^[6-9]\d{9}$/.test(d)) return '';
  if (/^(\d)\1{9}$/.test(d) || d === '9876543210' || d === '1234567890') return '';
  return d;
}
function clip(v, n) { return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n || 120); }
function maskContacts(s) { return String(s || '').replace(/(\+?\d[\d\s-]{8,}\d)|([^\s@]+@[^\s@]+)/g, '•••'); }

/**
 * Validate one submission. Returns {error} for unusable data, otherwise {row, status, reasons, checks}.
 * linkCoords: coordinates resolved from the map link (short links are expanded by the caller).
 */
function assess(d, linkCoords) {
  if (!d || typeof d !== 'object') return { error: 'Empty submission.' };
  if (d._gotcha) return { error: 'Rejected.' };
  var phone = validPhone(d.phone);
  if (!phone) return { error: 'Enter a valid 10-digit mobile number.' };
  var name = clip(d.name, 80);
  if (name.length < 2) return { error: 'Enter your full name.' };
  var need = ['district', 'taluka', 'village'];
  for (var i = 0; i < need.length; i++) if (clip(d[need[i]], 60).length < 2) return { error: 'Enter the ' + need[i] + '.' };
  if (!clip(d.survey, 60) && !clip(d.pcard, 60)) return { error: 'Enter the survey / block no. or the property card no.' };
  if (!mapsLinkOk(d.link)) return { error: 'Paste a Google Maps link of the land.' };
  var poly = Array.isArray(d.poly) ? d.poly.map(function (p) { return [Number(p[0]), Number(p[1])]; }) : [];
  if (poly.length < 3 || poly.length > 60 || !poly.every(function (p) { return isFinite(p[0]) && isFinite(p[1]); })) return { error: 'Draw the land on the map (at least 3 corners).' };
  if (!poly.every(inGujarat)) return { error: 'The boundary must be in Gujarat.' };
  if (selfIntersects(poly)) return { error: 'The boundary lines cross each other. Please redraw.' };
  var drawn = polyArea(poly);
  if (drawn < 40 || drawn > 5e6) return { error: 'The drawn area is not realistic. Please redraw.' };
  var declared = toM2(d.areaValue, d.areaUnit);
  if (!isFinite(declared)) return { error: 'Enter the area as on the 7/12.' };
  var price = Number(d.price);
  if (!(price > 0) || price > 1e11) return { error: 'Enter the asking price.' };
  var auth = AUTH.hasOwnProperty(d.auth) ? d.auth : 'UNSURE';

  var reasons = [], checks = [];
  var r = drawn / declared;
  if (r >= 0.85 && r <= 1.15) checks.push('Area on the map is within ' + Math.round(Math.abs(r - 1) * 100) + '% of the 7/12 area');
  else reasons.push('area on the map (' + Math.round(drawn) + ' sq.m) differs from the 7/12 (' + Math.round(declared) + ' sq.m)');
  var c = centroid(poly);
  if (linkCoords) {
    var dist = distM(linkCoords, c);
    if (dist <= 1500) checks.push('map link matches the boundary (' + Math.round(dist) + ' m)');
    else reasons.push('map link is ' + (dist / 1000).toFixed(1) + ' km from the boundary');
  } else reasons.push('map link location could not be read');
  var a = AUTH[auth];
  if (a && distM([a[0], a[1]], c) > a[2] * 1000) reasons.push('land is outside the chosen authority area');
  if (auth === 'UNSURE' || auth === 'OUT') checks.push('zoning to be confirmed');
  if (d.role === 'Broker with written mandate') reasons.push('posted by a broker: confirm the owner mandate');

  var row = {
    created: new Date().toISOString(), name: name, phone: '+91' + phone, email: clip(d.email, 120), role: clip(d.role, 40), type: clip(d.type, 40),
    district: clip(d.district, 40), taluka: clip(d.taluka, 60), village: clip(d.village, 60), survey: clip(d.survey, 60), pcard: clip(d.pcard, 60), tp: clip(d.tp, 80),
    areaValue: clip(d.areaValue, 20), areaUnit: clip(d.areaUnit, 10), areaDeclaredM2: Math.round(declared), areaDrawnM2: Math.round(drawn),
    price: price, priceUnit: PRICE_UNITS.indexOf(d.priceUnit) >= 0 ? d.priceUnit : 'total', auth: auth, zone: clip(d.zone, 10),
    road: ROADS.indexOf(d.road) >= 0 ? d.road : 'none', corridor: d.corridor ? 'yes' : '', link: clip(d.link, 400),
    linkLat: linkCoords ? linkCoords[0] : '', linkLng: linkCoords ? linkCoords[1] : '',
    poly: JSON.stringify(poly.map(function (p) { return [+p[0].toFixed(7), +p[1].toFixed(7)]; })), notes: maskContacts(clip(d.notes, 600))
  };
  return { row: row, status: reasons.length ? 'REVIEW' : 'LIVE', reasons: reasons, checks: checks };
}

/* ---------------- Google services ---------------- */
function sheet_() {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) { sh = ss.insertSheet(SHEET_NAME); sh.appendRow(COLS); sh.setFrozenRows(1); }
  return sh;
}
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function resolveLink_(link) {
  var c = coordsFromText(link);
  if (c) return c;
  try {   // short link: read where it redirects without loading the page
    var url = link;
    for (var i = 0; i < 4; i++) {
      var res = UrlFetchApp.fetch(url, { followRedirects: false, muteHttpExceptions: true });
      var loc = res.getHeaders()['Location'] || res.getHeaders()['location'];
      if (!loc) break;
      c = coordsFromText(decodeURIComponent(loc));
      if (c) return c;
      url = loc;
    }
  } catch (e) { /* unreachable link: left for review */ }
  return null;
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var res = assess(d, mapsLinkOk(d && d.link) ? resolveLink_(String(d.link).trim()) : null);
    if (res.error) return json_({ ok: false, error: res.error });
    var sh = sheet_(), data = sh.getDataRange().getValues(), head = data[0];
    var col = function (n) { return head.indexOf(n); };
    var dayAgo = Date.now() - 864e5, recent = 0;
    for (var i = 1; i < data.length; i++) {
      if (String(data[i][col('phone')]) === res.row.phone && new Date(data[i][col('created')]).getTime() > dayAgo) recent++;
      var st = String(data[i][col('status')]);
      if ((st === 'LIVE' || st === 'REVIEW') && res.row.survey && String(data[i][col('survey')]).toLowerCase() === res.row.survey.toLowerCase()
          && String(data[i][col('village')]).toLowerCase() === res.row.village.toLowerCase()) res.reasons.push('the same survey no. and village is already listed (' + data[i][col('id')] + ')');
    }
    if (recent >= 3) return json_({ ok: false, error: 'This number has already posted 3 lands today. Please call us to add more.' });
    var status = res.reasons.length ? 'REVIEW' : 'LIVE';
    var id = 'L' + Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyMMdd') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
    res.row.id = id; res.row.status = status;
    res.row.checks = status === 'LIVE' ? 'Checked when posted: ' + res.checks.join('; ') + '.' : 'Needs review: ' + res.reasons.join('; ') + '.';
    sh.appendRow(COLS.map(function (k) { return res.row[k] === undefined ? '' : res.row[k]; }));
    CacheService.getScriptCache().remove('list');
    var r = res.row, ss = SpreadsheetApp.getActive();
    MailApp.sendEmail({
      to: OWNER_EMAIL,
      subject: (status === 'LIVE' ? '[LIVE] ' : '[REVIEW] ') + 'Land posted: ' + r.village + ', ' + r.taluka + ' (' + r.district + ') ' + id,
      body: ['Status: ' + status + (status === 'REVIEW' ? '  (change Status to LIVE in the sheet to publish)' : '  (shown on the website now; set HIDDEN to remove)'),
        r.checks, '', 'Seller: ' + r.name + '  ' + r.phone + (r.email ? '  ' + r.email : '') + '  (' + r.role + ')',
        'Land: ' + r.type + ', ' + r.village + ', ' + r.taluka + ', ' + r.district, 'Survey/block: ' + (r.survey || '-') + '   Property card: ' + (r.pcard || '-') + '   TP/FP: ' + (r.tp || '-'),
        'Area: ' + r.areaValue + ' ' + r.areaUnit + ' (' + r.areaDeclaredM2 + ' sq.m)   Drawn: ' + r.areaDrawnM2 + ' sq.m',
        'Price: Rs ' + r.price + ' (' + r.priceUnit + ')', 'Authority/zone/road: ' + r.auth + ' / ' + r.zone + ' / ' + r.road + (r.corridor ? ' (within 200 m)' : ''),
        'Map link: ' + r.link, 'Notes: ' + (r.notes || '-'), '', 'Sheet: ' + ss.getUrl(),
        'Listing: https://galaxyestatesproperties.co.in/land.html#land-' + id].join('\n')
    });
    return json_({ ok: true, id: id, status: status, reason: res.reasons.join('; ') });
  } catch (err) {
    return json_({ ok: false, error: 'Could not save just now. Please try again or WhatsApp us.' });
  } finally {
    try { lock.releaseLock(); } catch (e) { /* not held */ }
  }
}

function doGet(e) {
  var cache = CacheService.getScriptCache(), hit = cache.get('list');
  if (hit) return ContentService.createTextOutput(hit).setMimeType(ContentService.MimeType.JSON);
  var data = sheet_().getDataRange().getValues(), head = data[0], out = [];
  for (var i = 1; i < data.length; i++) {
    var o = {};
    head.forEach(function (h, j) { o[h] = data[i][j]; });
    var st = String(o.status).trim().toUpperCase();
    if (st !== 'LIVE' && st !== 'SOLD') continue;
    var p = {};
    PUBLIC.forEach(function (k) { p[k] = o[k]; });
    p.status = st;
    p.created = o.created instanceof Date ? o.created.toISOString() : String(o.created);
    try { p.poly = JSON.parse(o.poly); } catch (err) { continue; }
    p.corridor = String(o.corridor) === 'yes';
    p.price = Number(o.price) || 0;
    p.notes = maskContacts(o.notes);
    if (st === 'LIVE' && /^Needs review/.test(String(o.checks))) p.checks = 'Verified by Galaxy Estates Properties.';
    out.push(p);
  }
  var body = JSON.stringify({ ok: true, listings: out });
  try { cache.put('list', body, 60); } catch (err) { /* too large to cache */ }
  return ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
}

if (typeof module !== 'undefined') module.exports = { toM2: toM2, polyArea: polyArea, selfIntersects: selfIntersects, coordsFromText: coordsFromText, mapsLinkOk: mapsLinkOk, validPhone: validPhone, assess: assess, maskContacts: maskContacts };

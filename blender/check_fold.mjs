// Run with:  node blender/check_fold.mjs
// Replays the pop-up plant's fold exactly as the page moves it (it runs the page's own code, lifted out of index.html, on the poses in models/fold.bin)
// and measures how far any two tiles pass into each other on the way. Fails if any pair goes deeper than 2 cm beyond how the two sit when finished.
import fs from 'fs';
import { fileURLToPath } from 'url';
const ROOT = fileURLToPath(new URL('..', import.meta.url));
const THREE = await import(ROOT + 'vendor/three.module.min.js');
const html = fs.readFileSync(ROOT + 'index.html', 'utf8');
const grab = (start, end) => { const a = html.indexOf(start), b = html.indexOf(end, a); if (a < 0 || b < 0) throw new Error('not found: ' + start); return html.slice(a, b); };
// the page's own code, so this cannot drift from it
const src = grab('  var sQ = new THREE.Quaternion(), sT = new THREE.Vector3();', '  (function () { // self-check: any two poses') + grab('  var STAGE = {', '  function tickFold(t, A) {') + grab('      lag = g === \'floor\'', '      if (x > 0.7 && x < 1) P.tint');
const clamp = (x, a, b) => Math.max(a, Math.min(b, x)), seg = (u, a, b) => clamp((u - a) / (b - a), 0, 1), mix = (a, b, t) => a + (b - a) * t, smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const make = new Function('THREE', 'clamp', 'seg', 'mix', 'smooth', 'parts', src.replace(/\n      lag = /, '\n  return function (u) { var i, P, st, g, x, lag; for (i = 0; i < parts.length; i++) { P = parts[i]; g = P.n[1]; st = STAGE[g];\n      lag = ') + '\n  } };');
const bin = fs.readFileSync(ROOT + 'models/fold.bin'), hl = bin.readUInt32LE(0), head = JSON.parse(bin.subarray(4, 4 + hl).toString()), tf = new Float32Array(bin.buffer.slice(bin.byteOffset + 4 + hl + head.off[3], bin.byteOffset + 4 + hl + head.off[3] + head.pname.length * 40)); // the file's header, and each part's place and rotation
const raw = head.pname.map((n, k) => head.alt[k].length ? { n, p: [...tf.subarray(k * 10, k * 10 + 3)], q: [...tf.subarray(k * 10 + 3, k * 10 + 7)], p2: head.alt[k].slice(0, 3), q2: head.alt[k].slice(3, 7) } : null).filter(Boolean);
const parts = raw.map(r => ({ n: r.n.split('.'), p: new THREE.Vector3(...r.p), q: new THREE.Quaternion(...r.q), p2: new THREE.Vector3(...r.p2), q2: new THREE.Quaternion(...r.q2), cp: new THREE.Vector3(), cq: new THREE.Quaternion(), half: new THREE.Vector3(['post', 'beam', 'leg'].includes(r.n.split('.')[1]) ? 0.046 : 0.196, 0.017, 0.196) }));
const pose = make(THREE, clamp, seg, mix, smooth, parts);
// screwOf is defined inside src; build each part's screw through a second tiny function
const mk2 = new Function('THREE', src.slice(0, src.indexOf('  var STAGE = {')) + '\n return screwOf;');
const screwOf = mk2(THREE); parts.forEach(P => { P.sw = screwOf(P.p, P.q, P.p2, P.q2); });
const ax = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()], bx = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()], T = new THREE.Vector3(), L = new THREE.Vector3();
function depth(A, B, shrink) { // how deep two boxes are into each other (0 or less: apart), by the separating-axis test
  const e = [1, 0, 0, 0, 1, 0, 0, 0, 1]; for (let i = 0; i < 3; i++) { ax[i].set(e[i * 3], e[i * 3 + 1], e[i * 3 + 2]).applyQuaternion(A.cq); bx[i].set(e[i * 3], e[i * 3 + 1], e[i * 3 + 2]).applyQuaternion(B.cq); }
  T.copy(B.cp).sub(A.cp); const ha = [A.half.x - shrink, A.half.y - shrink, A.half.z - shrink], hb = [B.half.x - shrink, B.half.y - shrink, B.half.z - shrink]; let best = 9;
  const test = (l) => { const n = l.length(); if (n < 1e-6) return true; let ra = 0, rb = 0; for (let i = 0; i < 3; i++) { ra += ha[i] * Math.abs(ax[i].dot(l)); rb += hb[i] * Math.abs(bx[i].dot(l)); } const d = (ra + rb - Math.abs(T.dot(l))) / n; if (d < best) best = d; return d > 0; };
  for (let i = 0; i < 3; i++) if (!test(ax[i])) return best; for (let i = 0; i < 3; i++) if (!test(bx[i])) return best;
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) if (!test(L.crossVectors(ax[i], bx[j]))) return best;
  return best;
}
const N = 600, hits = new Map(), SH = +(process.argv[2] || 0.004);
for (let s = 0; s <= N; s++) { const u = s / N; pose(u);
  for (let i = 0; i < parts.length; i++) for (let j = i + 1; j < parts.length; j++) { const d = depth(parts[i], parts[j], SH); if (d > 0) { const k = i + '|' + j, h = hits.get(k) || { a: parts[i].n.slice(1).join('.'), b: parts[j].n.slice(1).join('.'), max: 0, at: 0, from: u, to: u, rest: 0 }; if (d > h.max) { h.max = d; h.at = u; } h.to = u; if (s === N) h.rest = d; hits.set(k, h); } } }
const list = [...hits.values()].filter(h => h.max > h.rest + 0.004).sort((x, y) => (y.max - y.rest) - (x.max - x.rest));
console.log('pairs that pass into each other on the way (beyond how they sit when finished):', list.length, 'of', parts.length * (parts.length - 1) / 2);
list.slice(0, 30).forEach(h => console.log((h.a + ' x ' + h.b).padEnd(30), 'deepest', h.max.toFixed(3), 'at u', h.at.toFixed(2), 'from', h.from.toFixed(2), 'to', h.to.toFixed(2), 'rest', h.rest.toFixed(3)));
const restBad = [...hits.values()].filter(h => h.rest > 0.006); console.log('pairs overlapping when finished by more than 6 mm:', restBad.length, restBad.slice(0, 8).map(h => h.a + ' x ' + h.b + ' ' + h.rest.toFixed(3)).join('; '));
const worst = list.length ? list[0].max - list[0].rest : 0;
if (worst > 0.02) { console.error('FAIL: a pair passes ' + worst.toFixed(3) + ' into each other'); process.exit(1); } else console.log('ok: nothing passes more than ' + worst.toFixed(3) + ' into anything else');

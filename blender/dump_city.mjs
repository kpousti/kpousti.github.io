// Run with:  node blender/dump_city.mjs
// Writes blender/city_layout.json: the San Diego model exactly as the page lays it out (street corners, streets and what each costs to drive, every building, landmark and prop with its place and size),
// and the page's own A* run for the home trip (the streets in the order it explored them, and the route it found). It runs the page's own code, lifted out of index.html, so it cannot drift from it.
// blender/film_route.py reads the file. Run this again, then render again, if the page's city or its search ever changes.
import fs from 'fs';
import { fileURLToPath } from 'url';
const ROOT = fileURLToPath(new URL('..', import.meta.url)), html = fs.readFileSync(ROOT + 'index.html', 'utf8');
const grab = (start, end) => { const a = html.indexOf(start), b = html.indexOf(end, a); if (a < 0 || b < 0) throw new Error('not found: ' + start); return html.slice(a, b); };
const src = grab('function rng(seed) {', '// Repeatable noise') + grab('function hashNoise(k)', '\n') + '\n'
  + grab('  var rnd = rng(7), n = 10, i, j;', '  // ----- The model, lit like a product shot')            // the street graph, the lots, A*
  + 'var sites = [];\n' + grab('    var land = lots.filter(', '    sites.forEach(function (L) { need[L.kit]') // which kit piece stands on which lot, and the props
  + 'var run = astar(start, goal); return { n: n, nx: nx, nz: nz, edges: edges.map(function (e) { return { a: e.a, b: e.b, cost: e.cost }; }), sites: sites.map(function (L) { return { kit: L.kit, cx: L.cx, cz: L.cz, w: L.w, h: L.h, d: L.d, ang: L.ang }; }),'
  + ' parks: parks.map(function (Q) { return { cx: Q.cx, cz: Q.cz, w: Q.w, d: Q.d, ang: Q.ang }; }), start: start, goal: goal, order: run.order.map(function (e) { return edges.indexOf(e); }), path: run.path };';
const city = new Function(src)();
// self-check: the route starts and ends where it should, every step of it is a street, and every street on it was explored
const street = (a, b) => city.edges.findIndex(e => (e.a === a && e.b === b) || (e.a === b && e.b === a)), steps = city.path.slice(1).map((q, k) => street(city.path[k], q));
if (city.path[0] !== city.start || city.path[city.path.length - 1] !== city.goal || steps.includes(-1) || steps.some(s => !city.order.includes(s)) || !city.sites.length) throw new Error('the dumped city does not hold together');
fs.writeFileSync(ROOT + 'blender/city_layout.json', JSON.stringify(city, (k, v) => typeof v === 'number' && !Number.isInteger(v) ? +v.toFixed(5) : v) + '\n');
console.log(`corners ${city.nx.length}, streets ${city.edges.length}, pieces ${city.sites.length} (${[...new Set(city.sites.map(s => s.kit))].join(' ')}), parks ${city.parks.length}; home trip ${city.start} to ${city.goal}: ${city.order.length} streets explored, route of ${steps.length} streets`);

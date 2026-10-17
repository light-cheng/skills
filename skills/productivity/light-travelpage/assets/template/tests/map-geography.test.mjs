import test from 'node:test';
import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { Window } from 'happy-dom';

test('mobile map zoom starts at the configured itinerary inset', (t) => {
  const window = new Window({ url: 'http://localhost/' });
  t.after(() => window.happyDOM.abort());
  window.eval(readFileSync(new URL('../route-ui.js', import.meta.url), 'utf8') + '\nwindow.mapZoomScrollLeftForTest = mapZoomScrollLeft;');
  const region = { canvas: { width: 1448 }, projection: { frame: { x: 1000, width: 300 } } };
  const offset = window.mapZoomScrollLeftForTest(region, 1100, 350, true);
  assert.ok(offset > 650 && offset < 750, `right-side inset should be visible; got ${offset}`);
  assert.equal(window.mapZoomScrollLeftForTest(region, 1100, 350, false), 375);
});

test('geographic map builds a sourced outline and keeps coordinates fixed', (t) => {
  const root = mkdtempSync(path.join(tmpdir(), 'travel-geography-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, 'scripts'), { recursive: true });
  mkdirSync(path.join(root, 'assets/maps/templates'), { recursive: true });
  copyFileSync(new URL('../scripts/build-map.mjs', import.meta.url), path.join(root, 'scripts/build-map.mjs'));
  copyFileSync(new URL('../scripts/sketch-layout.mjs', import.meta.url), path.join(root, 'scripts/sketch-layout.mjs'));
  writeFileSync(path.join(root, 'package.json'), '{"type":"module"}\n');
  writeFileSync(path.join(root, 'assets/maps/templates/manifest.json'), '{"templates":[],"disclaimer":"fixture"}\n');
  writeFileSync(path.join(root, 'assets/maps/test-coast.geojson'), JSON.stringify({
    type: 'Feature', geometry: { type: 'MultiPolygon', coordinates: [[[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]] }
  }));
  const trip = {
    metadata: { assets: {} }, config: { modules: { overview: true } }, trip: {},
    map: {
      mapMode: 'geographic-outline',
      disclaimer: '本图仅表达地点的相对方位与路线顺序，不代表真实比例或精确地理边界。',
      region: { id: 'test', label: 'Test', countryCode: 'JP', geographic: {
        outlineFile: 'assets/maps/test-coast.geojson', baseImage: 'assets/maps/test-coast.svg',
        mainBounds: [0, 0, 2, 2], mainFrame: { x: 600, y: 100, width: 700, height: 800 },
        detailBounds: [0, 0, 2, 2], detailFrame: { x: 50, y: 600, width: 500, height: 400 }
      } },
      places: [
        { id: 'a', name: 'A', countryCode: 'JP', geo: { lat: .5, lng: .5 } },
        { id: 'b', name: 'B', countryCode: 'JP', geo: { lat: 1.5, lng: 1.5 } }
      ],
      routes: [{ day: 1, placeIds: ['a', 'b'] }]
    }
  };
  const tripPath = path.join(root, 'trip-data.json');
  const build = () => spawnSync(process.execPath, ['scripts/build-map.mjs'], { cwd: root, encoding: 'utf8' });
  writeFileSync(tripPath, JSON.stringify(trip));
  const positive = build();
  assert.equal(positive.status, 0, positive.stderr);
  const result = JSON.parse(readFileSync(tripPath, 'utf8')).routeMap.regions[0];
  assert.equal(result.mapMode, 'geographic-inset');
  assert.match(result.disclaimer, /地理轮廓来自配置的边界数据/);
  assert.doesNotMatch(result.disclaimer, /不代表真实比例或精确地理边界/);
  assert.match(result.description, /地理轮廓与行程地点/);
  assert.ok(result.places[0].x < result.places[1].x);
  assert.ok(result.places[0].y > result.places[1].y);
  assert.match(readFileSync(path.join(root, result.baseImage), 'utf8'), /<path d="M/);

  trip.map.region.geographic.detailBounds = [0, 0, 1, 1];
  writeFileSync(tripPath, JSON.stringify(trip));
  const negative = build();
  assert.notEqual(negative.status, 0);
  assert.match(negative.stderr, /outside detail bounds/);
});

test('sketch map reads each day from the schedule and starts from the previous night', async () => {
  const { buildSketch } = await import('../scripts/sketch-layout.mjs');
  const place = (id, lat, lng, countryCode = 'JP') => ({ id, name: id, countryCode, geo: { lat, lng } });
  const tripData = {
    places: [place('home', 22.3, 113.9, 'HK'), place('airport', 33.58, 130.45), place('station', 33.59, 130.42), place('hotel', 33.5905, 130.4205), place('lake', 33.26, 131.37)],
    accommodations: [{ placeId: 'hotel', checkIn: '2026-11-12', checkOut: '2026-11-14', status: 'confirmed' }],
    days: [
      { day: 1, date: '2026-11-12', schedule: [{ time: '12:00', type: 'flight', text: '飞机', placeIds: ['home', 'airport'] }, { time: '18:00', type: 'transfer', text: '西铁巴士', placeIds: ['airport', 'station'] }] },
      { day: 2, date: '2026-11-13', schedule: [{ time: '09:00', type: 'transfer', text: '特急' }, { time: '12:00', type: 'walk', placeId: 'lake' }, { time: '17:00', type: 'return', text: '特急回酒店' }] }
    ]
  };
  const sketch = buildSketch({ tripData, mapData: { region: { countryCode: 'JP' }, modeWords: ['西铁巴士'] }, boundary: null, canvas: { width: 1448, height: 1086 } });
  assert.deepEqual(sketch.nodes.find((node) => node.id === 'station').placeIds.sort(), ['hotel', 'station']);
  assert.deepEqual(sketch.days[0].legs.map((leg) => [leg.from, leg.to, leg.mode]), [['home', 'airport', '飞机'], ['airport', 'station', '西铁巴士']]);
  assert.deepEqual(sketch.days[1].legs.map((leg) => [leg.from, leg.to, leg.time]), [['station', 'lake', '09:00'], ['lake', 'station', '17:00']]);
  assert.equal(sketch.away[0].id, 'home');
});

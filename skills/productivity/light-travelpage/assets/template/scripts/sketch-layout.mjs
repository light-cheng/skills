/* Hand-drawn schematic map: places keep their real bearings, crowded areas are magnified,
   and every day's legs are read from the itinerary schedule so the map cannot drift from it. */

const MERGE_KM = 1;
const MIN_GAP = 96;
const MARGIN_DEG = 0.16;
const TRANSPORT_TYPES = new Set(["flight", "transfer", "return", "train", "rail", "drive", "rental-car", "ferry", "boat", "cable-car", "walk", "hike"]);
// Generic transport words; a trip adds named services (a sightseeing train, a bus line) through map.modeWords.
const MODE_WORDS = ["新干线", "高铁", "特急", "高速巴士", "巴士", "出租车", "打车", "地铁", "缆车", "渡轮", "步行", "徒步"];
const TYPE_NAMES = { flight: "飞机", transfer: "交通", return: "返程", train: "火车", rail: "火车", drive: "自驾", "rental-car": "租车", ferry: "渡轮", boat: "游船", "cable-car": "缆车", walk: "步行", hike: "徒步" };

function geoOf(place) {
  const lat = Number(place?.geo?.lat), lng = Number(place?.geo?.lng ?? place?.geo?.lon);
  return Number.isFinite(lat) && Number.isFinite(lng) ? { lat, lng } : null;
}

function distanceKm(a, b) {
  const r = (v) => v * Math.PI / 180;
  const h = Math.sin(r(b.lat - a.lat) / 2) ** 2 + Math.cos(r(a.lat)) * Math.cos(r(b.lat)) * Math.sin(r(b.lng - a.lng) / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

const round = (value) => Number(value.toFixed(1));

function placeIdsOf(item) {
  return [...new Set([...(Array.isArray(item.placeIds) ? item.placeIds : []), ...(item.placeId ? [item.placeId] : [])])];
}

function modeOf(item, words = MODE_WORDS) {
  const text = String(item?.text || item?.title || "");
  const word = words.find((candidate) => text.includes(candidate));
  return word || TYPE_NAMES[item?.type] || "";
}

function applyLens(point, lens) {
  const dx = point.x - lens.x, dy = point.y - lens.y, r = Math.hypot(dx, dy);
  if (r === 0 || r >= lens.R) return point;
  const t = r / lens.R, f = t * (lens.m + 1) / (lens.m * t + 1), k = f * lens.R / r;
  return { x: lens.x + dx * k, y: lens.y + dy * k };
}

// Fisheye lenses over clusters closer than MIN_GAP; the same warp is applied to the coastline,
// so a magnified place never lands in the sea.
function buildLenses(points) {
  const lenses = [];
  let current = points.map((point) => ({ ...point }));
  for (let pass = 0; pass < 6; pass += 1) {
    const parent = current.map((_, index) => index);
    const find = (index) => parent[index] === index ? index : (parent[index] = find(parent[index]));
    let crowded = false;
    for (let i = 0; i < current.length; i += 1) for (let j = i + 1; j < current.length; j += 1) {
      if (Math.hypot(current[i].x - current[j].x, current[i].y - current[j].y) < MIN_GAP) { parent[find(i)] = find(j); crowded = true; }
    }
    if (!crowded) break;
    const groups = {};
    current.forEach((_, index) => (groups[find(index)] ||= []).push(index));
    for (const group of Object.values(groups).filter((members) => members.length > 1)) {
      const x = group.reduce((sum, index) => sum + current[index].x, 0) / group.length;
      const y = group.reduce((sum, index) => sum + current[index].y, 0) / group.length;
      let nearest = Infinity, spread = 0;
      for (const i of group) {
        spread = Math.max(spread, Math.hypot(current[i].x - x, current[i].y - y));
        for (const j of group) if (i < j) nearest = Math.min(nearest, Math.hypot(current[i].x - current[j].x, current[i].y - current[j].y));
      }
      const lens = { pass, x, y, R: Math.max(130, spread + MIN_GAP * 1.4), m: Math.min(5, Math.max(0.4, MIN_GAP * 1.15 / Math.max(nearest, 4) - 1)) };
      lenses.push(lens);
      current = current.map((point) => applyLens(point, lens));
    }
  }
  return lenses;
}

function simplify(points, epsilon) {
  if (points.length < 3) return points;
  const [x1, y1] = points[0], [x2, y2] = points.at(-1);
  const length = Math.hypot(x2 - x1, y2 - y1) || 1e-12;
  let farthest = 0, index = 0;
  for (let i = 1; i < points.length - 1; i += 1) {
    const [x, y] = points[i];
    const distance = Math.abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / length;
    if (distance > farthest) { farthest = distance; index = i; }
  }
  if (farthest <= epsilon) return [points[0], points.at(-1)];
  return [...simplify(points.slice(0, index + 1), epsilon).slice(0, -1), ...simplify(points.slice(index), epsilon)];
}

function simplifyRing(ring, epsilon) {
  let far = 0;
  ring.forEach(([x, y], index) => { if (Math.hypot(x - ring[0][0], y - ring[0][1]) > Math.hypot(ring[far][0] - ring[0][0], ring[far][1] - ring[0][1])) far = index; });
  return [...simplify(ring.slice(0, far + 1), epsilon).slice(0, -1), ...simplify(ring.slice(far), epsilon)];
}

function stayFor(accommodations, date) {
  return accommodations.find((stay) => stay.placeId && stay.checkIn <= date && date < stay.checkOut) || null;
}

export function buildSketch({ tripData, mapData, boundary, canvas }) {
  const regionCodes = new Set([mapData.region?.countryCode, ...(mapData.region?.countryCodes || [])].filter(Boolean).map((code) => String(code).toUpperCase()));
  const mapPlaces = new Map((mapData.places || []).map((place) => [place.id, place]));
  const placeById = new Map((tripData.places || []).map((place) => [place.id, { ...place, ...(mapPlaces.get(place.id) || {}) }]));
  for (const [id, place] of mapPlaces) if (!placeById.has(id)) placeById.set(id, place);
  const isAway = (place) => place && regionCodes.size && place.countryCode && !regionCodes.has(String(place.countryCode).toUpperCase());

  // Places in the schedule, in order of first use.
  const usage = new Map();
  for (const day of tripData.days || []) for (const item of day.schedule || []) for (const id of placeIdsOf(item)) usage.set(id, (usage.get(id) || 0) + 1);
  for (const stay of tripData.accommodations || []) if (stay.placeId) usage.set(stay.placeId, (usage.get(stay.placeId) || 0) + 1);
  const located = [...usage.keys()].map((id) => placeById.get(id)).filter((place) => place && !isAway(place) && geoOf(place));
  const missing = [...usage.keys()].filter((id) => { const place = placeById.get(id); return place && !isAway(place) && !geoOf(place); });

  // Merge places within MERGE_KM into one map node; the most used place names the node.
  const nodes = [];
  for (const place of located) {
    const geo = geoOf(place);
    const node = nodes.find((candidate) => candidate.members.some((member) => distanceKm(geoOf(member), geo) <= MERGE_KM));
    if (node) node.members.push(place); else nodes.push({ members: [place] });
  }
  nodes.forEach((node) => {
    node.members.sort((a, b) => (usage.get(b.id) || 0) - (usage.get(a.id) || 0));
    node.id = node.members[0].id;
    node.geo = geoOf(node.members[0]);
  });
  const nodeOf = new Map(nodes.flatMap((node) => node.members.map((member) => [member.id, node.id])));

  // Fit the node bounds into the canvas, leaving the left column for the title and legend.
  const lats = nodes.map((node) => node.geo.lat), lngs = nodes.map((node) => node.geo.lng);
  const bounds = { west: Math.min(...lngs) - MARGIN_DEG, east: Math.max(...lngs) + MARGIN_DEG, south: Math.min(...lats) - MARGIN_DEG, north: Math.max(...lats) + MARGIN_DEG };
  const frame = { x: 380, y: 40, width: canvas.width - 420, height: canvas.height - 80 };
  const kx = Math.cos((bounds.north + bounds.south) / 2 * Math.PI / 180);
  const scale = Math.min(frame.width / ((bounds.east - bounds.west) * kx), frame.height / (bounds.north - bounds.south));
  const ox = frame.x + (frame.width - (bounds.east - bounds.west) * kx * scale) / 2;
  const oy = frame.y + (frame.height - (bounds.north - bounds.south) * scale) / 2;
  const project = ({ lat, lng }) => ({ x: ox + (lng - bounds.west) * kx * scale, y: oy + (bounds.north - lat) * scale });
  const lenses = buildLenses(nodes.map((node) => project(node.geo)));
  const warp = (point) => lenses.reduce((current, lens) => applyLens(current, lens), point);
  nodes.forEach((node) => { const point = warp(project(node.geo)); node.x = round(point.x); node.y = round(point.y); });

  // Legs from the schedule. Each day starts where the previous night was spent and ends at tonight's stay.
  const awayTargets = new Map();
  const nodeFor = (id) => {
    const place = placeById.get(id);
    if (isAway(place)) {
      if (!awayTargets.has(id)) awayTargets.set(id, { id, label: place.nameZh || place.name || id, away: true });
      return id;
    }
    return nodeOf.get(id) || null;
  };
  const accommodations = tripData.accommodations || [];
  const modeWords = [...(Array.isArray(mapData.modeWords) ? mapData.modeWords : []), ...MODE_WORDS];
  const days = (tripData.days || []).map((day, index, all) => {
    const previous = index ? stayFor(accommodations, all[index - 1].date) : null;
    let current = previous ? nodeFor(previous.placeId) : null;
    let pending = null;
    const legs = [];
    // An item naming two or more places is the move itself; a single place is reached by the last transport mentioned before it.
    const move = (to, item, explicit) => {
      if (!to || to === current) { current = to || current; return; }
      if (current) {
        const source = explicit ? item : pending || item;
        legs.push({ from: current, to, time: source?.time || "", mode: modeOf(source, modeWords) });
      }
      current = to; pending = null;
    };
    for (const item of day.schedule || []) {
      const ids = placeIdsOf(item).map(nodeFor).filter(Boolean);
      if (!ids.length) { if (TRANSPORT_TYPES.has(item.type)) pending = item; continue; }
      ids.forEach((id) => move(id, item, ids.length > 1));
    }
    const stay = stayFor(accommodations, day.date);
    if (stay) move(nodeFor(stay.placeId), pending);
    return { day: day.day, date: day.date, title: day.title, stay: stay ? nodeFor(stay.placeId) : null, stayPending: stay ? stay.status !== "confirmed" : false, legs };
  });

  // Direction for places outside the region: real bearing when known, otherwise south-west.
  for (const target of awayTargets.values()) {
    const place = placeById.get(target.id), geo = geoOf(place);
    const anchor = days.flatMap((day) => day.legs).find((leg) => leg.from === target.id || leg.to === target.id);
    const near = nodes.find((node) => node.id === (anchor?.from === target.id ? anchor?.to : anchor?.from));
    const vector = geo && near ? { x: (geo.lng - near.geo.lng) * kx, y: near.geo.lat - geo.lat } : { x: -0.45, y: 1 };
    const length = Math.hypot(vector.x, vector.y) || 1;
    target.dir = [round(vector.x / length), round(vector.y / length)];
  }

  const nights = (id) => days.filter((day) => day.stay === id);
  const landmarks = (mapData.region?.landmarks || []).filter((mark) => geoOf(mark)).map((mark) => {
    const point = warp(project(geoOf(mark)));
    return { type: mark.type === "sea" ? "sea" : "mountain", name: mark.name, x: round(point.x), y: round(point.y) };
  });
  const coast = (boundary?.geometry?.coordinates || []).flatMap((polygon) => polygon.slice(0, 1)).filter((ring) => {
    const xs = ring.map(([lng]) => lng), ys = ring.map(([, lat]) => lat);
    return Math.max(...xs) > bounds.west - 0.5 && Math.min(...xs) < bounds.east + 0.5 && Math.max(...ys) > bounds.south - 0.5 && Math.min(...ys) < bounds.north + 0.5;
  }).map((ring) => "M" + simplifyRing(ring, 0.0015).map(([lng, lat]) => { const p = warp(project({ lat, lng })); return `${p.x.toFixed(1)} ${p.y.toFixed(1)}`; }).join("L") + "Z").join("");

  return {
    missing,
    nodes: nodes.map((node) => ({
      id: node.id,
      placeIds: node.members.map((member) => member.id),
      x: node.x,
      y: node.y,
      label: node.members[0].nameZh || node.members[0].name || node.id,
      sub: node.members.slice(1, 3).map((member) => member.nameZh || member.name).join(" · "),
      nights: nights(node.id).length,
      pending: nights(node.id).some((day) => day.stayPending)
    })),
    away: [...awayTargets.values()],
    days,
    landmarks,
    coast,
    bounds: Object.fromEntries(Object.entries(bounds).map(([key, value]) => [key, Number(value.toFixed(4))]))
  };
}

export function sketchBaseSvg(sketch, canvas, ariaLabel) {
  const xml = (value) => String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&apos;" })[character]);
  const marks = sketch.landmarks.map((mark) => mark.type === "sea"
    ? `<text x="${mark.x}" y="${mark.y}" text-anchor="middle" font-size="22" letter-spacing="8" fill="#8f7655" font-family="'Kaiti SC', STKaiti, KaiTi, 'Songti SC', serif">${xml(mark.name)}</text>`
    : `<g transform="translate(${mark.x} ${mark.y})"><path d="M-22 10 L-5 -15 L4 -4 L10 -11 L24 10Z" fill="#9c7a52" fill-opacity=".45" stroke="#9c7a52" stroke-width="1.5" stroke-linejoin="round" filter="url(#rough)"/><text y="30" text-anchor="middle" font-size="16" fill="#7a6248" font-family="'Kaiti SC', STKaiti, KaiTi, 'Songti SC', serif">${xml(mark.name)}</text></g>`).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${canvas.width} ${canvas.height}" role="img" aria-label="${xml(ariaLabel)}">
  <defs>
    <filter id="rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="4"/></filter>
    <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="2" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.35  0 0 0 0 0.2  0 0 0 0.08 0"/></filter>
    <pattern id="waves" width="44" height="24" patternUnits="userSpaceOnUse"><path d="M3 13 q8 -6 16 0 t16 0" fill="none" stroke="#b9a37f" stroke-width="1.2" opacity=".55"/></pattern>
  </defs>
  <rect width="${canvas.width}" height="${canvas.height}" fill="#e2e0cf"/>
  <rect width="${canvas.width}" height="${canvas.height}" fill="url(#waves)" opacity=".7"/>
  <path d="${sketch.coast}" fill="#f8f0dc" stroke="#8a6a45" stroke-width="2" stroke-linejoin="round" filter="url(#rough)"/>
  <rect width="${canvas.width}" height="${canvas.height}" filter="url(#paper)"/>
  ${marks}
</svg>\n`;
}

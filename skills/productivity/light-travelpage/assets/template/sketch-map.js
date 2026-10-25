/* Hand-drawn route map. Layout comes from scripts/sketch-layout.mjs; this file draws routes, arrows, step numbers and labels. */
const SKETCH_FONT = "'Kaiti SC', STKaiti, KaiTi, 'Songti SC', serif";
const SKETCH_INK = "#3a2a1a", SKETCH_SUB = "#7a6248", SKETCH_PAPER = "#f8f0dc";

function sketchUnit(vector) {
  const length = Math.hypot(vector.x, vector.y) || 1;
  return { x: vector.x / length, y: vector.y / length };
}

function sketchQuad(a, c, b, t) {
  return { x: (1 - t) ** 2 * a.x + 2 * (1 - t) * t * c.x + t * t * b.x, y: (1 - t) ** 2 * a.y + 2 * (1 - t) * t * c.y + t * t * b.y };
}

function sketchTangent(a, c, b, t) {
  return { x: 2 * (1 - t) * (c.x - a.x) + 2 * t * (b.x - c.x), y: 2 * (1 - t) * (c.y - a.y) + 2 * t * (b.y - c.y) };
}

function sketchTextWidth(text, size) {
  return [...String(text)].reduce((width, character) => width + (character.charCodeAt(0) < 128 ? 0.58 : 1) * size, 0);
}

function sketchLegs(sketch, dayNumber) {
  if (dayNumber) {
    const day = sketch.days.find((item) => item.day === dayNumber);
    return (day?.legs || []).map((leg, index) => ({ ...leg, day: dayNumber, step: index + 1 }));
  }
  // Overview: one line per place pair per day; a return trip on the same day gets arrows at both ends.
  return sketch.days.flatMap((day) => {
    const seen = new Map();
    day.legs.forEach((leg) => {
      const key = [leg.from, leg.to].sort().join("|");
      if (seen.has(key)) { if (seen.get(key).from !== leg.from) seen.get(key).both = true; return; }
      seen.set(key, { ...leg, day: day.day });
    });
    return [...seen.values()];
  });
}

function sketchViewport(source, dayNumber) {
  const canvas = source.canvas || { width: 1448, height: 1086 };
  const sketch = source.sketch;
  if (!dayNumber || !sketch) return { x: 0, y: 0, width: canvas.width, height: canvas.height };
  const nodes = new Map(sketch.nodes.map((node) => [node.id, node]));
  const day = sketch.days.find((item) => item.day === dayNumber);
  const ids = new Set([...(day?.legs || []).flatMap((leg) => [leg.from, leg.to]), day?.stay].filter((id) => nodes.has(id)));
  if (!ids.size) return { x: 0, y: 0, width: canvas.width, height: canvas.height };
  const points = [...ids].map((id) => nodes.get(id));
  (day?.legs || []).forEach((leg) => {
    const away = sketch.away.find((item) => item.id === leg.from || item.id === leg.to);
    const near = nodes.get(away?.id === leg.from ? leg.to : leg.from);
    if (away && near) points.push({ x: near.x + away.dir[0] * 150, y: near.y + away.dir[1] * 150 });
  });
  let x0 = Math.min(...points.map((p) => p.x)) - 170, x1 = Math.max(...points.map((p) => p.x)) + 170;
  let y0 = Math.min(...points.map((p) => p.y)) - 130, y1 = Math.max(...points.map((p) => p.y)) + 150;
  let width = Math.max(x1 - x0, canvas.width / 1.8), height = Math.max(y1 - y0, canvas.height / 1.8);
  if (width / height > canvas.width / canvas.height) height = width * canvas.height / canvas.width; else width = height * canvas.width / canvas.height;
  width = Math.min(width, canvas.width); height = Math.min(height, canvas.height);
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  return {
    x: Math.round(Math.min(Math.max(0, cx - width / 2), canvas.width - width)),
    y: Math.round(Math.min(Math.max(0, cy - height / 2), canvas.height - height)),
    width: Math.round(width), height: Math.round(height)
  };
}

// options.labelScale enlarges marks and text for small embeds (the itinerary side map); the route page uses the default.
// options.dayTitle: false leaves out the date and title line when the page already shows them beside the map.
function sketchMapArtwork(days, source, dayNumber = 0, options = {}) {
  const sketch = source.sketch;
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&apos;" })[character]);
  const f = (value) => Number(value).toFixed(1);
  const canvas = source.canvas || { width: 1448, height: 1086 };
  const view = sketchViewport(source, dayNumber);
  const u = view.width / canvas.width * (Number(options.labelScale) || 1);
  const nodes = new Map(sketch.nodes.map((node) => [node.id, node]));
  const today = dayNumber ? sketch.days.find((day) => day.day === dayNumber) : null;
  const legs = sketchLegs(sketch, dayNumber);
  const active = new Set(today ? [...legs.flatMap((leg) => [leg.from, leg.to]), today.stay].filter((id) => nodes.has(id)) : nodes.keys());
  const colorFor = (day) => source.routes?.find((route) => route.day === day)?.color || "#954434";
  const nodeR = 9 * u, lineW = 4.5 * u, arrowSize = 10 * u;
  const rough = 'filter="url(#sketch-rough)"';
  const lines = [], marks = [], obstacles = [], samples = [], labels = [];

  const arrow = (p, dir, color) => {
    const e = sketchUnit(dir), n = { x: -e.y, y: e.x }, s = arrowSize;
    const tip = { x: p.x + e.x * s * 0.9, y: p.y + e.y * s * 0.9 };
    const left = { x: p.x - e.x * s * 0.6 + n.x * s * 0.75, y: p.y - e.y * s * 0.6 + n.y * s * 0.75 };
    const right = { x: p.x - e.x * s * 0.6 - n.x * s * 0.75, y: p.y - e.y * s * 0.6 - n.y * s * 0.75 };
    marks.push(`<path d="M${f(tip.x)} ${f(tip.y)}L${f(left.x)} ${f(left.y)}L${f(right.x)} ${f(right.y)}Z" fill="${color}" stroke="${SKETCH_PAPER}" stroke-width="${1.5 * u}" stroke-linejoin="round"/>`);
    obstacles.push({ x: p.x - s, y: p.y - s, w: s * 2, h: s * 2 });
  };
  const chip = (p, text, color, caption, normal) => {
    marks.push(`<g transform="translate(${f(p.x)} ${f(p.y)}) scale(${u})"><circle r="13" fill="${esc(color)}" stroke="${SKETCH_PAPER}" stroke-width="2.5"/><text y="5.2" text-anchor="middle" font-family="${SKETCH_FONT}" font-size="16" font-weight="700" fill="#fff">${esc(text)}</text></g>`);
    obstacles.push({ x: p.x - 15 * u, y: p.y - 15 * u, w: 30 * u, h: 30 * u });
    if (!caption) return;
    // Mode and time sit beside the step number, on the outer side of the curve.
    const size = 15 * u, width = sketchTextWidth(caption, size);
    const side = normal.x >= 0 ? 1 : -1;
    const x = p.x + side * 20 * u, y = p.y + normal.y * 10 * u + 5 * u;
    marks.push(`<text x="${f(x)}" y="${f(y)}" text-anchor="${side > 0 ? "start" : "end"}" font-family="${SKETCH_FONT}" font-size="${f(size)}" fill="${SKETCH_SUB}" stroke="${SKETCH_PAPER}" stroke-width="${4 * u}" stroke-linejoin="round" paint-order="stroke">${esc(caption)}</text>`);
    obstacles.push({ x: side > 0 ? x : x - width, y: y - size, w: width, h: size * 1.3 });
  };

  // Single-day view keeps the rest of the trip as faint dotted context.
  const context = [];
  if (today) {
    const seen = new Set();
    sketch.days.forEach((day) => day.legs.forEach((leg) => {
      const key = [leg.from, leg.to].sort().join("|");
      if (seen.has(key) || !nodes.has(leg.from) || !nodes.has(leg.to)) return;
      seen.add(key);
      const a = nodes.get(leg.from), b = nodes.get(leg.to);
      context.push(`<path d="M${f(a.x)} ${f(a.y)}L${f(b.x)} ${f(b.y)}" stroke="#9c8a70" stroke-width="${2 * u}" stroke-dasharray="${2 * u} ${7 * u}" stroke-linecap="round" fill="none" opacity=".5"/>`);
    }));
  }

  // Repeated trips between the same two places run side by side.
  const groups = new Map();
  legs.forEach((leg) => { const key = [leg.from, leg.to].sort().join("|"); if (!groups.has(key)) groups.set(key, []); groups.get(key).push(leg); });
  groups.forEach((group, key) => {
    const [ka, kb] = key.split("|");
    group.forEach((leg, index) => {
      const color = colorFor(leg.day);
      const label = String(today ? leg.step : leg.day);
      const caption = today ? [leg.mode, leg.time].filter(Boolean).join(" ") : "";
      const spread = index - (group.length - 1) / 2;
      const away = sketch.away.find((item) => item.id === leg.from || item.id === leg.to);
      if (away) {
        const inbound = away.id === leg.from;
        const p = nodes.get(inbound ? leg.to : leg.from);
        if (!p) return;
        const dir = sketchUnit({ x: away.dir[0], y: away.dir[1] }), side = { x: -dir.y, y: dir.x }, sign = inbound ? -1 : 1;
        const far = { x: p.x + dir.x * 170 * u + side.x * 30 * u * sign, y: p.y + dir.y * 170 * u + side.y * 30 * u * sign };
        const near = { x: p.x + dir.x * (nodeR + 6 * u) + side.x * 5 * u * sign, y: p.y + dir.y * (nodeR + 6 * u) + side.y * 5 * u * sign };
        const a = inbound ? far : near, b = inbound ? near : far;
        const c = { x: (a.x + b.x) / 2 + side.x * 14 * u * sign, y: (a.y + b.y) / 2 + side.y * 14 * u * sign };
        lines.push(`<path d="M${f(a.x)} ${f(a.y)}Q${f(c.x)} ${f(c.y)} ${f(b.x)} ${f(b.y)}" fill="none" stroke="${color}" stroke-width="${lineW * 0.8}" stroke-dasharray="${10 * u} ${8 * u}" stroke-linecap="round" ${rough}/>`);
        arrow(sketchQuad(a, c, b, 0.75), sketchTangent(a, c, b, 0.75), color);
        chip(sketchQuad(a, c, b, 0.42), label, color, caption, side);
        marks.push(`<text x="${f(far.x)}" y="${f(far.y + (dir.y > 0 ? 24 : -12) * u)}" text-anchor="middle" font-family="${SKETCH_FONT}" font-size="${17 * u}" fill="${SKETCH_INK}" stroke="${SKETCH_PAPER}" stroke-width="${4 * u}" paint-order="stroke">✈ ${esc(away.label)}</text>`);
        obstacles.push({ x: far.x - 40 * u, y: far.y - 30 * u, w: 80 * u, h: 60 * u });
        for (let t = 0; t <= 1; t += 0.05) samples.push(sketchQuad(a, c, b, t));
        return;
      }
      const A = nodes.get(leg.from), B = nodes.get(leg.to), CA = nodes.get(ka), CB = nodes.get(kb);
      if (!A || !B) return;
      const along = sketchUnit({ x: CB.x - CA.x, y: CB.y - CA.y }), normal = { x: -along.y, y: along.x };
      const length = Math.hypot(CB.x - CA.x, CB.y - CA.y), short = length / u < 170;
      const bend = Math.min(60, length * 0.09) + spread * 17 * u * (short ? 1.7 : 1);
      const C = { x: (A.x + B.x) / 2 + normal.x * bend, y: (A.y + B.y) / 2 + normal.y * bend };
      const trim = (p) => { const e = sketchUnit({ x: C.x - p.x, y: C.y - p.y }); return { x: p.x + e.x * (nodeR + 6 * u), y: p.y + e.y * (nodeR + 6 * u) }; };
      const a = trim(A), b = trim(B), d = `M${f(a.x)} ${f(a.y)}Q${f(C.x)} ${f(C.y)} ${f(b.x)} ${f(b.y)}`;
      lines.push(`<path d="${d}" fill="none" stroke="${SKETCH_PAPER}" stroke-width="${lineW + 3 * u}" stroke-linecap="round" opacity=".8"/><path d="${d}" fill="none" stroke="${color}" stroke-width="${lineW}" stroke-linecap="round" ${rough}/>`);
      const at = short ? 0.84 : 0.8;
      arrow(sketchQuad(a, C, b, at), sketchTangent(a, C, b, at), color);
      if (leg.both) { const tangent = sketchTangent(a, C, b, 1 - at); arrow(sketchQuad(a, C, b, 1 - at), { x: -tangent.x, y: -tangent.y }, color); }
      const chipT = Math.min(0.64, Math.max(0.28, 0.46 + spread * (short ? 0.2 : 0.13)));
      const outward = { x: normal.x * Math.sign(bend || 1), y: normal.y * Math.sign(bend || 1) };
      // Short hops inside a magnified area get the step number only; their captions would collide.
      chip(sketchQuad(a, C, b, chipT), label, color, short || group.length > 2 || length / u < 230 ? "" : caption, outward);
      for (let t = 0; t <= 1; t += 0.04) samples.push(sketchQuad(a, C, b, t));
    });
  });

  const nodeMarks = [];
  sketch.nodes.forEach((node) => {
    const on = active.has(node.id);
    const stay = today ? today.stay === node.id : node.nights > 0;
    obstacles.push({ x: node.x - nodeR - 2 * u, y: node.y - nodeR - 2 * u, w: nodeR * 2 + 4 * u, h: nodeR * 2 + 4 * u });
    nodeMarks.push(`<g opacity="${on ? 1 : 0.35}"><circle cx="${f(node.x)}" cy="${f(node.y)}" r="${f(nodeR)}" fill="${stay ? SKETCH_INK : "#fffaf0"}" stroke="${SKETCH_INK}" stroke-width="${2.6 * u}" ${rough}/>${stay ? `<circle cx="${f(node.x)}" cy="${f(node.y)}" r="${f(3.2 * u)}" fill="#fffaf0"/>` : ""}</g>`);
  });

  // Title and legend block; reserve its space before placing place names.
  const header = [];
  if (today) {
    const x = view.x + 30 * u, y = view.y + view.height - 30 * u;
    if (options.dayTitle !== false) header.push(`<text x="${f(x)}" y="${f(y - 34 * u)}" font-family="${SKETCH_FONT}" font-size="${36 * u}" font-weight="700" fill="${SKETCH_INK}" stroke="${SKETCH_PAPER}" stroke-width="${6 * u}" paint-order="stroke">${esc((today.date || "").slice(5).replace("-", "/"))}　${esc(today.title)}</text>`);
    header.push(`<text x="${f(x)}" y="${f(y)}" font-family="${SKETCH_FONT}" font-size="${16 * u}" fill="${SKETCH_SUB}" stroke="${SKETCH_PAPER}" stroke-width="${4 * u}" paint-order="stroke">圆圈数字是当天第几步，箭头是方向${today.stay ? `；今晚住 ${esc(nodes.get(today.stay)?.label || "")}${today.stayPending ? "（未订）" : ""}` : ""}</text>`);
    const headerHeight = (options.dayTitle === false ? 56 : 100) * u;
    obstacles.push({ x: view.x, y: view.y + view.height - headerHeight, w: Math.min(view.width, 760 * u), h: headerHeight });
  } else {
    const heading = source.heading || { text: source.label, x: 40, y: 100, size: 40 };
    const legend = source.legend || { x: 42, y: 160, gap: 42 };
    header.push(`<text x="${heading.x}" y="${heading.y}" font-family="${SKETCH_FONT}" font-size="${heading.size || 40}" font-weight="700" fill="${SKETCH_INK}">${esc(heading.text)}</text>`);
    sketch.days.forEach((day, index) => {
      const y = legend.y + index * legend.gap, date = days.find((item) => item.day === day.day)?.date || day.date || "";
      header.push(`<g data-date="${esc(date)}"><circle cx="${legend.x + 13}" cy="${y - 7}" r="13" fill="${colorFor(day.day)}"/><text x="${legend.x + 13}" y="${y - 1.5}" text-anchor="middle" font-family="${SKETCH_FONT}" font-size="16" font-weight="700" fill="#fff">${day.day}</text><text x="${legend.x + 36}" y="${y}" font-family="${SKETCH_FONT}" font-size="20" fill="${SKETCH_INK}">${esc(date.slice(5).replace("-", "/"))} ${esc(String(day.title || "").split("｜")[0])}</text></g>`);
    });
    header.push(`<text x="${legend.x}" y="${legend.y + sketch.days.length * legend.gap + 10}" font-family="${SKETCH_FONT}" font-size="16" fill="${SKETCH_SUB}">圆圈数字是第几天 · 实心点是住宿</text>`);
    obstacles.push({ x: 0, y: 0, w: 370, h: canvas.height });
  }

  // Place names: eight candidate spots per place, keep the one with the fewest collisions.
  const placed = [];
  const overlap = (r, o) => Math.max(0, Math.min(r.x + r.w, o.x + o.w) - Math.max(r.x, o.x)) * Math.max(0, Math.min(r.y + r.h, o.y + o.h) - Math.max(r.y, o.y));
  [...sketch.nodes].sort((a, b) => active.has(b.id) - active.has(a.id)).forEach((node) => {
    if (node.x < view.x || node.x > view.x + view.width || node.y < view.y || node.y > view.y + view.height) return;
    const on = active.has(node.id);
    let sub = "";
    if (today && on) sub = today.stay === node.id && today.stayPending ? "今晚住（未订）" : node.sub || "";
    else if (!today && node.nights) sub = `住 ${node.nights} 晚${node.pending ? "（未订）" : ""}`;
    const main = (on ? 25 : 19) * u, small = 15 * u;
    const w = Math.max(sketchTextWidth(node.label, main), sub ? sketchTextWidth(sub, small) : 0);
    const h = main + (sub ? small + 6 * u : 0), d = nodeR + 8 * u;
    const spots = [[d, -h / 2, "start"], [-d - w, -h / 2, "end"], [-w / 2, -d - h, "middle"], [-w / 2, d, "middle"], [d * 0.8, -d * 0.8 - h, "start"], [-d * 0.8 - w, -d * 0.8 - h, "end"], [d * 0.8, d * 0.8, "start"], [-d * 0.8 - w, d * 0.8, "end"]];
    let best = null;
    spots.forEach(([dx, dy, anchor], index) => {
      const r = { x: node.x + dx, y: node.y + dy, w, h };
      let score = index * 2 * u * u;
      [...obstacles, ...placed].forEach((o) => { score += overlap(r, o) * (on ? 1 : 0.3); });
      samples.forEach((s) => { if (s.x > r.x - 3 * u && s.x < r.x + w + 3 * u && s.y > r.y - 3 * u && s.y < r.y + h + 3 * u) score += 60 * u * u; });
      if (r.x < view.x + 6 * u || r.x + w > view.x + view.width - 6 * u || r.y < view.y + 6 * u || r.y + h > view.y + view.height - 6 * u) score += 1e6;
      if (!best || score < best.score) best = { r, anchor, score };
    });
    if (best.score >= 1e6 || (!on && best.score > 400 * u * u)) return;
    placed.push(best.r);
    const x = best.anchor === "start" ? best.r.x : best.anchor === "end" ? best.r.x + w : best.r.x + w / 2;
    const y = best.r.y + main * 0.85;
    labels.push(`<g opacity="${on ? 1 : 0.45}" font-family="${SKETCH_FONT}"><text x="${f(x)}" y="${f(y)}" text-anchor="${best.anchor}" font-size="${f(main)}" font-weight="700" fill="${SKETCH_INK}" stroke="${SKETCH_PAPER}" stroke-width="${5 * u}" stroke-linejoin="round" paint-order="stroke">${esc(node.label)}</text>${sub ? `<text x="${f(x)}" y="${f(y + small + 6 * u)}" text-anchor="${best.anchor}" font-size="${f(small)}" fill="${SKETCH_SUB}" stroke="${SKETCH_PAPER}" stroke-width="${4 * u}" stroke-linejoin="round" paint-order="stroke">${esc(sub)}</text>` : ""}</g>`);
  });

  const north = `<g transform="translate(${f(view.x + view.width - 40 * u)} ${f(view.y + view.height - 44 * u)}) scale(${u})" fill="${SKETCH_INK}" font-family="${SKETCH_FONT}"><path d="M0 -28 L9 0 L0 -7 L-9 0Z"/><text y="22" text-anchor="middle" font-size="17" font-weight="700">N</text></g>`;
  const title = today ? today.title : source.title || "旅行路线";
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${view.x} ${view.y} ${view.width} ${view.height}" role="img" aria-label="${esc(source.ariaLabel || title)}" data-sketch-version="1">
  <title>${esc(title)}</title>
  <desc>${esc(source.disclaimer || "")}</desc>
  <defs><filter id="sketch-rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="${f(0.03 / u)}" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="${f(3 * u)}"/></filter></defs>
  <image href="${esc(source.baseImage)}" width="${canvas.width}" height="${canvas.height}" preserveAspectRatio="none"/>
  <g id="sketch-context">${context.join("")}</g>
  <g id="sketch-routes">${lines.join("")}</g>
  <g id="sketch-places">${nodeMarks.join("")}</g>
  <g id="sketch-marks">${marks.join("")}</g>
  <g id="sketch-labels">${labels.join("")}</g>
  <g id="sketch-heading">${header.join("")}${north}</g>
  </svg>`;
}

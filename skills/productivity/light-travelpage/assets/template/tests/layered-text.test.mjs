import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Window } from "happy-dom";
import { validateTrip } from "../scripts/validate.mjs";

const read = name => readFileSync(new URL("../" + name, import.meta.url), "utf8");

function layeredTrip() {
  const data = JSON.parse(read("trip-data.json"));
  data.metadata.tripId = "layered-text";
  data.metadata.localLanguage = "fr";
  Object.assign(data.trip, { status: "confirmed", startDate: "2026-11-12", endDate: "2026-11-12", dayCount: 1 });
  Object.assign(data.config.modules, { itinerary: true, todo: true, accommodations: true });
  data.places = [{ id: "station", name: "Station", geo: { lat: 48.85, lng: 2.35 } }];
  data.days = [{ day: 1, date: "2026-11-12", title: "Arrive", locations: [], schedule: [
    { id: "train", time: "10:00", type: "train", placeId: "station", text: "Take the train. Platform 3.",
      detail: { lead: "Take the train", sections: [{ label: "Where", points: ["Platform 3", "Car 5"] }, { label: "Empty", points: [] }] } },
    { id: "walk", time: "12:00", type: "walk", text: "Plain entry stays plain", ticketIds: ["bus"] }
  ] }];
  data.ticketPlanning.items = [
    { id: "bus", day: 1, name: "Local bus", requirement: "on-site", guidance: ["Pay cash", "Exact change"] },
    { id: "museum", day: 1, name: "Museum", requirement: "advance-required", guidance: "Book online" }
  ];
  data.preTrip.packingItems = [];
  data.preTrip.cashBudget = { title: "Cash plan", currency: "EUR", rows: [{ item: "Bus", amount: "4", pay: "cash", cash: true }], notes: ["Carry coins"] };
  return data;
}

async function render(t, data, todos = []) {
  const validation = validateTrip(data, new URL("../", import.meta.url).pathname);
  assert.equal(validation.ok, true, validation.errors.join("\n"));
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  const errors = [];
  w.console.error = (...args) => errors.push(args.map(String).join(" "));
  w.document.write(read("index.html").replace(/<script\b[^>]*>[\s\S]*?<\/script>/g, "").replace(/<link[^>]+rel="stylesheet"[^>]*>/g, ""));
  w.HTMLElement.prototype.scrollIntoView = () => {}; w.scrollTo = () => {};
  w.fetch = async url => ({ ok: true, json: async () => String(url) === "trip-data.json" ? structuredClone(data)
    : ({ version: 1, revision: 0, todos, tickets: [], bills: [], travelers: [], settings: null }) });
  w.TravelMaps = { button: () => "" };
  w.eval(read("runtime-storage.js"));
  await w.eval(read("travel-cards.js") + "\n" + read("overview-map.js") + "\n" + read("route-ui.js") + "\n" + read("app.js").replace('document.addEventListener("DOMContentLoaded", init);', "") + "\nwindow.__state = state;\ninit();");
  assert.equal(w.document.querySelector("#loading-error").hidden, true, errors.join("\n"));
  return { w, errors };
}

test("schedule detail renders a lead and labelled points, and plain entries keep their text", async t => {
  const { w, errors } = await render(t, layeredTrip());
  const detail = w.document.querySelector(".schedule-text--detail");
  assert.equal(detail.querySelector(".schedule-lead").textContent, "Take the train");
  assert.deepEqual([...detail.querySelectorAll(".schedule-section__label")].map(e => e.textContent), ["Where"]);
  assert.deepEqual([...detail.querySelectorAll("li")].map(e => e.textContent), ["Platform 3", "Car 5"]);
  assert.ok([...w.document.querySelectorAll(".schedule-text")].some(e => e.textContent === "Plain entry stays plain"));
  assert.deepEqual(errors, []);
});

test("day header shows the weekday and on-site tickets do not count as pending purchases", async t => {
  const { w } = await render(t, layeredTrip());
  assert.equal(w.document.querySelector(".day-weekday").textContent, "周四");
  assert.equal(w.document.querySelector(".day-ticket-summary").textContent, "1 项待购票");
  assert.deepEqual([...w.document.querySelectorAll('[data-inline-ticket="bus"] .schedule-ticket__guidance span')].map(e => e.textContent), ["Pay cash", "Exact change"]);
});

test("cash budget uses the authored currency and stays hidden without rows", async t => {
  const { w } = await render(t, layeredTrip());
  const budget = w.document.querySelector("#cash-budget");
  assert.equal(budget.hidden, false);
  assert.deepEqual([...budget.querySelectorAll("th")].map(e => e.textContent), ["项目", "EUR", "怎么付"]);
  assert.ok(!budget.innerHTML.includes("JPY"));
  const empty = layeredTrip();
  empty.preTrip.cashBudget = { rows: [] };
  const second = await render(t, empty);
  assert.equal(second.w.document.querySelector("#cash-budget").hidden, true);
});

test("long to-dos are layered and a blank-line card gets the local language and a copy button", async t => {
  const todos = [
    { id: "long", text: "现金：先换钱。路上要付：巴士；出租车；寺庙门票。", completed: false },
    { id: "card", text: "给前台看这张卡片\n\nBonjour\nMerci", completed: false },
    { id: "short", text: "带护照", completed: false }
  ];
  const { w } = await render(t, layeredTrip(), todos);
  const long = w.document.querySelector('[data-todo-id="long"]');
  assert.equal(long.querySelector(".todo-label").textContent, "现金");
  assert.deepEqual([...long.querySelectorAll(".todo-bullet")].map(e => e.textContent), ["巴士", "出租车", "寺庙门票。"]);
  const card = w.document.querySelector('[data-todo-id="card"] .todo-card');
  assert.equal(card.getAttribute("lang"), "fr");
  assert.equal(card.querySelector(".todo-card-text").textContent, "Bonjour\nMerci");
  assert.ok(!w.document.querySelector('[data-todo-id="card"] .todo-text').textContent.includes("Bonjour"));
  assert.equal(w.document.querySelector('[data-todo-id="short"] .todo-card'), null);
  assert.equal(w.document.querySelector('[data-todo-id="short"] .todo-label'), null);
});

test("copy button copies only the card text and falls back when the clipboard refuses", async t => {
  const todos = [{ id: "card", text: "说明\n\nLine one\nLine two", completed: false }];
  const { w } = await render(t, layeredTrip(), todos);
  const copied = [];
  Object.defineProperty(w.navigator, "clipboard", { configurable: true, value: { writeText: async text => { copied.push(text); } } });
  const button = w.document.querySelector("[data-copy-card]");
  button.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.deepEqual(copied, ["Line one\nLine two"]);
  assert.equal(button.textContent, "已复制");
  Object.defineProperty(w.navigator, "clipboard", { configurable: true, value: { writeText: async () => { throw new Error("denied"); } } });
  w.document.execCommand = () => false;
  button.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(button.textContent, "请长按选择复制");
});

test("stay cards list cancellation and navigation points and mark pending stays as not booked", async t => {
  const data = layeredTrip();
  data.accommodations = [
    { id: "inn", name: "Inn", placeId: "station", status: "confirmed", checkIn: "2026-11-12", checkOut: "2026-11-13", roomType: "Twin",
      cancellationPoints: ["Free until 11/10", "Pay at the desk"], navigationPoints: ["South exit", "5 minutes on foot"] },
    { id: "later", status: "pending", checkIn: null, checkOut: null }
  ];
  const { w } = await render(t, data);
  const inn = w.document.querySelector("#stay-inn");
  assert.deepEqual([...inn.querySelectorAll(".stay-points h4")].map(e => e.textContent), ["取消和付款", "位置和入住"]);
  assert.equal(inn.querySelectorAll(".stay-points li").length, 4);
  assert.equal(w.document.querySelector("#stay-later .soft-label").textContent, "待预订");
});

async function submitTodo(w, adapter, text) {
  w.__state.runtimeAdapters.todos = adapter;
  w.LightTravelRefresh = async () => {};
  const errors = [];
  w.addEventListener("light:sync-status", event => errors.push(event.detail.message));
  w.document.querySelector("#todo-input").value = text;
  w.document.querySelector("#todo-form").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await new Promise(resolve => setTimeout(resolve, 0));
  return errors;
}

test("a to-do cannot be resubmitted while the previous save is pending or busy", async t => {
  for (const flag of ["pending", "busy"]) {
    const { w } = await render(t, layeredTrip());
    const calls = [];
    const errors = await submitTodo(w, { [flag]: true, applyChange: async (...args) => { calls.push(args); return {}; } }, "Buy stamps");
    assert.equal(calls.length, 0, flag);
    assert.equal(w.document.querySelector("#todo-input").value, "Buy stamps", flag);
    assert.equal(errors.length, 1, flag);
  }
});

test("the to-do input clears only after the save is confirmed, including a recovered retry", async t => {
  const { w } = await render(t, layeredTrip());
  let saved;
  await submitTodo(w, { applyChange: async (_c, todo) => { saved = todo; return { todos: [] }; } }, "Not echoed");
  assert.equal(w.document.querySelector("#todo-input").value, "Not echoed");
  await submitTodo(w, { applyChange: async (_c, todo) => ({ todos: [todo] }) }, "Echoed");
  assert.equal(w.document.querySelector("#todo-input").value, "");
  const queued = { pending: false, applyChange: async (_c, todo) => { saved = todo; queued.pending = true; throw new Error("offline"); } };
  const errors = await submitTodo(w, queued, "Retry me");
  assert.deepEqual(errors, ["offline"]);
  assert.equal(w.document.querySelector("#todo-input").value, "Retry me");
  w.LightTravelRecoverSavedMutation([{ snapshot: { todos: [saved] } }]);
  assert.equal(w.document.querySelector("#todo-input").value, "");
  const failed = { pending: false, applyChange: async () => { throw new Error("rejected"); } };
  await submitTodo(w, failed, "Keep me");
  w.LightTravelRecoverSavedMutation([{ snapshot: { todos: [{ id: "other", text: "Keep me" }] } }]);
  assert.equal(w.document.querySelector("#todo-input").value, "Keep me");
});

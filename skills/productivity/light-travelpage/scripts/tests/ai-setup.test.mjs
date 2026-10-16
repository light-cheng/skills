import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { PassThrough } from "node:stream";
import { detectFormats, mergeDevVars, readHidden, setup } from "../ai-setup.mjs";

const script = fileURLToPath(new URL("../ai-setup.mjs", import.meta.url));
const KEY = "synthetic-setup-key-0123456789";
const openaiModels = { object: "list", data: [{ id: "gpt-test", object: "model" }, { id: "gpt-other", object: "model" }] };
const anthropicModels = { data: [{ id: "claude-test", type: "model", display_name: "Claude Test" }], has_more: false };

// A fake upstream: which formats answer /models, and whether the tool round trip calls the tool.
function upstream({ openai = null, anthropic = null, toolCall = true, seen = [] } = {}) {
  return async (url, options) => {
    seen.push({ url, options });
    const isAnthropic = Object.hasOwn(options.headers, "anthropic-version");
    if (url.endsWith("/models") || url.endsWith("/models?limit=1000")) {
      const body = isAnthropic ? anthropic : openai;
      return body ? Response.json(body) : new Response("no", { status: 401 });
    }
    const body = JSON.parse(options.body);
    if (url.endsWith("/messages"))
      return Response.json({ role: "assistant", stop_reason: toolCall ? "tool_use" : "end_turn",
        content: toolCall ? [{ type: "tool_use", id: "t1", name: body.tools[0].name, input: { ok: true } }] : [{ type: "text", text: "hi" }] });
    if (url.endsWith("/chat/completions"))
      return Response.json({ choices: [{ message: { role: "assistant", content: "",
        tool_calls: toolCall ? [{ id: "c1", type: "function", function: { name: body.tools[0].function.name, arguments: '{"ok":true}' } }] : [] } }] });
    return new Response("unexpected", { status: 404 });
  };
}

function project() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "travel-ai-setup-"));
  fs.mkdirSync(path.join(dir, "server")); fs.writeFileSync(path.join(dir, "server", "ai-client.js"), "// v0.2.8 runtime\n");
  fs.writeFileSync(path.join(dir, "ai-config.json"), '{"provider":"off"}\n');
  fs.writeFileSync(path.join(dir, ".dev.vars"), "ACCESS_CODE_HASH=abc\nOPENAI_API_KEY=old\nOPENAI_MODEL=old-model\nTRIP_ID=fixture\n");
  return dir;
}
const options = (dir, extra = {}) => ({ projectDir: dir, baseUrl: "https://upstream.example/v1", format: "auto", target: "local",
  apiKey: KEY, model: null, choose: null, log: () => {}, ...extra });

test("detection tells OpenAI-shaped and Anthropic-shaped model lists apart", async () => {
  assert.deepEqual((await detectFormats("https://u.example/v1", KEY, upstream({ openai: openaiModels }))).map((f) => f.format), ["openai-chat"]);
  assert.deepEqual((await detectFormats("https://u.example/v1", KEY, upstream({ anthropic: anthropicModels }))).map((f) => f.format), ["anthropic-messages"]);
  const both = await detectFormats("https://u.example/v1", KEY, upstream({ openai: openaiModels, anthropic: anthropicModels }));
  assert.deepEqual(both.map((f) => f.format).sort(), ["anthropic-messages", "openai-chat"]);
  assert.deepEqual(both.find((f) => f.format === "anthropic-messages").models, ["claude-test"]);
  assert.deepEqual(await detectFormats("https://u.example/v1", KEY, upstream()), []);
});

test("an Anthropic service is detected, its model chosen, round-tripped and written to .dev.vars", async (t) => {
  const dir = project(); t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const seen = [];
  const result = await setup(options(dir, { fetchImpl: upstream({ anthropic: anthropicModels, seen }), choose: async (models) => models[0] }));
  assert.deepEqual(result, { format: "anthropic-messages", model: "claude-test", roundTrip: "tool call returned" });
  const vars = fs.readFileSync(path.join(dir, ".dev.vars"), "utf8");
  assert.match(vars, /^AI_BASE_URL=https:\/\/upstream\.example\/v1$/m);
  assert.match(vars, /^AI_API_FORMAT=anthropic-messages$/m);
  assert.match(vars, /^AI_MODEL=claude-test$/m);
  assert.match(vars, new RegExp(`^AI_API_KEY=${KEY}$`, "m"));
  assert.match(vars, /^ACCESS_CODE_HASH=abc$/m); assert.match(vars, /^TRIP_ID=fixture$/m);
  assert.deepEqual(fs.readdirSync(dir).filter((name) => name.endsWith(".tmp")), []);
  assert.doesNotMatch(vars, /OPENAI_/);
  assert.equal(fs.statSync(path.join(dir, ".dev.vars")).mode & 0o777, 0o600);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(dir, "ai-config.json"))), { provider: "on" });
  assert.ok(seen.some((s) => s.url.endsWith("/messages")));
});

test("both formats answering needs the owner to pick one", async (t) => {
  const dir = project(); t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  await assert.rejects(setup(options(dir, { fetchImpl: upstream({ openai: openaiModels, anthropic: anthropicModels }), model: "gpt-test" })),
    /--format/);
  const asked = [];
  const picked = await setup(options(dir, { fetchImpl: upstream({ openai: openaiModels, anthropic: anthropicModels }),
    choose: async (items, label) => { asked.push(label); return label === "Format" ? "anthropic-messages" : items[0]; } }));
  assert.deepEqual(asked, ["Format"]); assert.equal(picked.format, "anthropic-messages"); assert.equal(picked.model, "claude-test");
  const result = await setup(options(dir, { fetchImpl: upstream({ openai: openaiModels, anthropic: anthropicModels }),
    format: "openai-chat", model: "gpt-test" }));
  assert.equal(result.format, "openai-chat");
});

test("a typed model ID works when the model list is unavailable", async (t) => {
  const dir = project(); t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  await assert.rejects(setup(options(dir, { fetchImpl: upstream() })), /--format/);
  const result = await setup(options(dir, { fetchImpl: upstream(), format: "openai-chat", model: "typed-model" }));
  assert.deepEqual(result, { format: "openai-chat", model: "typed-model", roundTrip: "tool call returned" });
});

test("a failed tool round trip writes nothing", async (t) => {
  const dir = project(); t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const before = fs.readFileSync(path.join(dir, ".dev.vars"), "utf8");
  await assert.rejects(setup(options(dir, { fetchImpl: upstream({ openai: openaiModels, toolCall: false }), model: "gpt-test" })),
    /tool call/);
  assert.equal(fs.readFileSync(path.join(dir, ".dev.vars"), "utf8"), before);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(dir, "ai-config.json"))), { provider: "off" });
});

test("several models and no choice: the list is shown and nothing is written", async (t) => {
  const dir = project(); t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  await assert.rejects(setup(options(dir, { fetchImpl: upstream({ openai: openaiModels }) })), /gpt-test.*gpt-other|--model/s);
});

test("the Pages target hands the settings to wrangler on stdin, never in a file or argument", async (t) => {
  const dir = project(); t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  let call;
  const runCommand = (command, args, opts) => { call = { command, args, body: JSON.parse(opts.input) }; return { status: 0 }; };
  await setup(options(dir, { fetchImpl: upstream({ anthropic: anthropicModels }), target: "pages", projectName: "trip-site", runCommand }));
  assert.equal(call.command, "npx");
  assert.deepEqual(call.args, ["wrangler", "pages", "secret", "bulk", "--project-name", "trip-site"]);
  assert.deepEqual(Object.keys(call.body).sort(), ["AI_API_FORMAT", "AI_API_KEY", "AI_BASE_URL", "AI_MODEL"]);
  assert.ok(!call.args.some((arg) => arg.includes(KEY)));
  const failed = project(); t.after(() => fs.rmSync(failed, { recursive: true, force: true }));
  await assert.rejects(setup(options(failed, { fetchImpl: upstream({ anthropic: anthropicModels }), target: "pages", projectName: "x",
    runCommand: () => ({ status: 1 }) })), /wrangler/);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(failed, "ai-config.json"))), { provider: "off" });
});

test("a page without the v0.2.8 runtime, or a symlinked settings file, is refused before anything is written", async (t) => {
  const old = project(); t.after(() => fs.rmSync(old, { recursive: true, force: true }));
  fs.rmSync(path.join(old, "server"), { recursive: true });
  let calls = 0; const counting = async (...args) => { calls++; return upstream({ anthropic: anthropicModels })(...args); };
  await assert.rejects(setup(options(old, { fetchImpl: counting })), /v0\.2\.8/); assert.equal(calls, 0);
  assert.match(fs.readFileSync(path.join(old, ".dev.vars"), "utf8"), /OPENAI_API_KEY=old/);
  const linked = project(); t.after(() => fs.rmSync(linked, { recursive: true, force: true }));
  const outside = path.join(linked, "..", path.basename(linked) + "-outside"); fs.writeFileSync(outside, "");
  t.after(() => fs.rmSync(outside, { force: true }));
  fs.rmSync(path.join(linked, ".dev.vars")); fs.symlinkSync(outside, path.join(linked, ".dev.vars"));
  await assert.rejects(setup(options(linked, { fetchImpl: upstream({ anthropic: anthropicModels }) })), /symlink/);
  assert.equal(fs.readFileSync(outside, "utf8"), "");
});

test("the hidden prompt never echoes the key, through edits and arrow keys", async () => {
  const input = new PassThrough(); input.isTTY = true; const modes = []; input.setRawMode = (on) => modes.push(on);
  const output = new PassThrough(); let shown = ""; output.on("data", (chunk) => { shown += chunk; });
  const answer = readHidden(input, output, "API key (hidden): ");
  input.write("SECRETKEY"); input.write("\u007f"); input.write("\u001b[D"); input.write("Zz"); input.write("\r");
  assert.equal(await answer, "SECRETKEZz");
  assert.equal(shown, "API key (hidden): \n"); assert.deepEqual(modes, [true, false]);
  const cancelled = readHidden(input, output, "? "); input.write("abc\u0003");
  await assert.rejects(cancelled, /Cancelled/);
  const eof = readHidden(input, output, "? "); input.write("\u0004");
  await assert.rejects(eof, /Cancelled/);
  const closed = readHidden(input, output, "? "); input.end();
  await assert.rejects(closed, /closed/);
});

test("mergeDevVars replaces AI settings, drops the old OPENAI_ ones and keeps the rest", () => {
  const merged = mergeDevVars("A=1\nAI_MODEL=x\nOPENAI_BASE_URL=y\n# note\nB=2\n", { AI_MODEL: "m", AI_BASE_URL: "u" });
  assert.equal(merged, "A=1\n# note\nB=2\nAI_MODEL=m\nAI_BASE_URL=u\n");
});

test("the command line refuses a key argument and never prints the key", () => {
  const refused = spawnSync(process.execPath, [script, os.tmpdir(), "--base-url", "https://u.example/v1", "--api-key", KEY], { encoding: "utf8" });
  assert.notEqual(refused.status, 0); assert.doesNotMatch(refused.stdout + refused.stderr, new RegExp(KEY));
  const noKey = spawnSync(process.execPath, [script, os.tmpdir(), "--base-url", "https://u.example/v1"],
    { encoding: "utf8", env: { PATH: process.env.PATH }, input: "" });
  assert.notEqual(noKey.status, 0); assert.match(noKey.stderr, /AI_API_KEY/);
  for (const bad of ["https://user:pw@u.example/v1", "https://u.example/v1/messages"]) {
    const result = spawnSync(process.execPath, [script, os.tmpdir(), "--base-url", bad], { encoding: "utf8", env: { PATH: process.env.PATH, AI_API_KEY: KEY } });
    assert.notEqual(result.status, 0, bad); assert.doesNotMatch(result.stdout + result.stderr, new RegExp(KEY));
  }
});

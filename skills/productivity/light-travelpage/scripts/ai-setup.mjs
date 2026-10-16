#!/usr/bin/env node
// Configure a generated travel page's AI service at deployment time.
// The page owner picks the service and model here; travelers never can.
//
// usage: node ai-setup.mjs <project-directory> --base-url <url>
//          [--format auto|openai-chat|openai-responses|anthropic-messages] [--model <id>]
//          [--target local|pages] [--project-name <pages-project>]
// The key comes from AI_API_KEY or a hidden prompt, never from the command line.
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { createAiClient, normalizeApiFormat, normalizeBaseUrl } from "../assets/template/server/ai-client.js";

const ANTHROPIC_VERSION = "2023-06-01";
const PING = { type: "function", function: { name: "ping", description: "Connectivity check. Call it with ok set to true.",
  parameters: { type: "object", properties: { ok: { type: "boolean" } }, required: ["ok"], additionalProperties: false } } };

async function probe(url, headers, fetchImpl) {
  try {
    const response = await fetchImpl(url, { method: "GET", redirect: "manual", headers, signal: AbortSignal.timeout(15000) });
    return response.ok ? await response.json() : null;
  } catch { return null; }
}

/** Formats whose model list answers, each with its model IDs. OpenAI lists say object "model"; Anthropic lists say type "model". */
export async function detectFormats(baseUrl, apiKey, fetchImpl = fetch) {
  const base = normalizeBaseUrl(baseUrl), found = [];
  const lists = [
    await probe(`${base}/models`, apiKey ? { Authorization: `Bearer ${apiKey}` } : {}, fetchImpl),
    // Anthropic pages its model list (20 by default); ask for all of them at once.
    await probe(`${base}/models?limit=1000`, { ...(apiKey ? { "x-api-key": apiKey } : {}), "anthropic-version": ANTHROPIC_VERSION }, fetchImpl),
  ];
  for (const list of lists) {
    const items = Array.isArray(list?.data) ? list.data.filter((item) => typeof item?.id === "string") : null;
    if (!items) continue;
    const format = items.some((item) => item.type === "model") && !items.some((item) => item.object === "model")
      ? "anthropic-messages" : "openai-chat";
    if (!found.some((entry) => entry.format === format)) found.push({ format, models: items.map((item) => item.id) });
  }
  return found;
}

/** Replace AI_* lines, drop the older OPENAI_* lines, keep every other line in order. */
export function mergeDevVars(existing, settings) {
  const kept = existing.split("\n").filter((line) => line !== "" && !/^(AI|OPENAI)_[A-Z_]+=/.test(line));
  return [...kept, ...Object.entries(settings).map(([name, value]) => `${name}=${value}`)].join("\n") + "\n";
}

function refuseSymlink(file) {
  if (fs.existsSync(file) && fs.lstatSync(file).isSymbolicLink()) throw new Error(`${path.basename(file)} is a symlink; refusing to write through it.`);
}

/** Write through a new 0600 file in the same folder, then rename, so the key is never in a readable file. */
function writePrivate(file, text) {
  refuseSymlink(file);
  const temporary = path.join(path.dirname(file), `.${path.basename(file)}.${process.pid}.tmp`);
  fs.writeFileSync(temporary, text, { mode: 0o600, flag: "wx" });
  try { fs.renameSync(temporary, file); } catch (error) { fs.rmSync(temporary, { force: true }); throw error; }
}

/** The setup writes settings only the v0.2.8 runtime reads; an older page would lose its AI. */
function requireCurrentRuntime(projectDir) {
  if (!fs.existsSync(path.join(projectDir, "ai-config.json")) || !fs.existsSync(path.join(projectDir, "server", "ai-client.js")))
    throw new Error("This is not a travel page generated with v0.2.8 or later (server/ai-client.js is missing). Older pages keep their OPENAI_* settings; see references/ai-integration.md.");
}

export async function setup({ projectDir, baseUrl, format = "auto", model = null, target = "local", projectName = null,
  apiKey = "", fetchImpl = fetch, choose = null, runCommand = spawnSync, log = console.log }) {
  const base = normalizeBaseUrl(baseUrl);
  if (!["local", "pages"].includes(target)) throw new Error("--target must be local or pages");
  if (target === "pages" && !projectName) throw new Error("--target pages needs --project-name");
  requireCurrentRuntime(projectDir);
  const detected = await detectFormats(base, apiKey, fetchImpl);
  let models;
  if (format === "auto") {
    if (detected.length === 0) throw new Error("Could not read the service's model list; pass --format and --model.");
    let entry = detected[0];
    if (detected.length > 1) {
      const formats = detected.map((item) => item.format);
      if (!choose) throw new Error(`The service answers as ${formats.join(" and ")}; pass --format to choose one.`);
      const picked = await choose(formats, "Format");
      entry = detected.find((item) => item.format === picked);
      if (!entry) throw new Error(`Unknown format ${picked}; pass --format to choose one.`);
    }
    ({ format, models } = entry);
  } else {
    format = normalizeApiFormat(format);
    const family = format === "anthropic-messages" ? "anthropic-messages" : "openai-chat";
    models = detected.find((entry) => entry.format === family)?.models || [];
  }
  if (!model) {
    if (models.length === 1) model = models[0];
    else if (models.length && choose) model = await choose(models, "Model");
    else if (models.length) throw new Error(`Pass --model with one of: ${models.join(", ")}`);
    else throw new Error("The model list is unavailable; pass --model with the model ID.");
  }
  if (models.length && !models.includes(model)) log(`Note: ${model} is not in the service's model list; the round trip decides.`);

  // A listed model is only discovery: require one real tool call before writing anything.
  const client = createAiClient({ baseUrl: base, apiKey, apiFormat: format, fetchImpl });
  const reply = await client.complete({ model, tools: [PING], messages: [
    { role: "system", content: "You are a connectivity check." },
    { role: "user", content: "Call the ping tool with ok set to true." },
  ] });
  if (!(reply.tool_calls || []).some((call) => call.function?.name === "ping"))
    throw new Error(`The model answered without a tool call; nothing was written.${format === "openai-chat" ? " Try --format openai-responses." : ""}`);

  const settings = { AI_BASE_URL: base, AI_API_KEY: apiKey, AI_MODEL: model, AI_API_FORMAT: format };
  if (target === "local") {
    const file = path.join(projectDir, ".dev.vars");
    writePrivate(file, mergeDevVars(fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "", settings));
  } else {
    // The secrets go to wrangler on stdin, so no file holds the key even if the run is interrupted.
    const result = runCommand("npx", ["wrangler", "pages", "secret", "bulk", "--project-name", projectName],
      { cwd: projectDir, input: JSON.stringify(settings), stdio: ["pipe", "inherit", "inherit"] });
    if (result.status !== 0) throw new Error("wrangler could not store the Pages secrets; nothing else was changed.");
  }
  const config = path.join(projectDir, "ai-config.json");
  refuseSymlink(config);
  fs.writeFileSync(config, JSON.stringify({ provider: "on" }, null, 2) + "\n");
  return { format, model, roundTrip: "tool call returned" };
}

/** Read a line without echoing anything: raw mode, our own handling of Enter, Backspace and Ctrl-C. */
export function readHidden(input, output, question) {
  return new Promise((resolve, reject) => {
    let value = "", escape = false;
    output.write(question);
    input.setRawMode(true); input.resume(); input.setEncoding("utf8");
    const finish = (error) => {
      input.setRawMode(false); input.pause(); input.removeListener("data", onData); input.removeListener("end", onEnd);
      output.write("\n");
      error ? reject(error) : resolve(value.trim());
    };
    const onData = (chunk) => {
      for (const char of chunk) {
        if (escape) { if (/[A-Za-z~]/.test(char)) escape = false; continue; }  // skip arrow keys and other sequences
        if (char === "\u001b") escape = true;
        else if (char === "\r" || char === "\n") return finish();
        else if (char === "\u0003" || (char === "\u0004" && !value)) return finish(new Error("Cancelled."));
        else if (char === "\u007f" || char === "\b") value = value.slice(0, -1);
        else if (char >= " ") value += char;
      }
    };
    const onEnd = () => finish(new Error("Input closed before the key was entered."));
    input.on("data", onData); input.on("end", onEnd);
  });
}

function chooseFromList(items, label) {
  return new Promise((resolve) => {
    items.forEach((id, index) => console.log(`${index + 1}. ${id}`));
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(`${label} number: `, (answer) => { rl.close(); resolve(items[Number(answer) - 1] || answer.trim()); });
  });
}

async function main(argv) {
  const options = { projectDir: null, baseUrl: null, format: "auto", model: null, target: "local", projectName: null };
  const flags = { "--base-url": "baseUrl", "--format": "format", "--model": "model", "--target": "target", "--project-name": "projectName" };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--api-key" || argv[i].startsWith("--api-key="))
      throw new Error("Do not pass the key on the command line; set AI_API_KEY or answer the hidden prompt.");
    if (flags[argv[i]] && i + 1 < argv.length) options[flags[argv[i]]] = argv[++i];
    else if (!argv[i].startsWith("--") && !options.projectDir) options.projectDir = argv[i];
    else throw new Error("usage: ai-setup.mjs <project-directory> --base-url <url> [--format …] [--model <id>] [--target local|pages] [--project-name <name>]");
  }
  if (!options.projectDir || !options.baseUrl) throw new Error("usage: ai-setup.mjs <project-directory> --base-url <url>");
  normalizeBaseUrl(options.baseUrl);
  let apiKey = process.env.AI_API_KEY || "";
  if (!apiKey) {
    if (!process.stdin.isTTY) throw new Error("Set AI_API_KEY, or run in a terminal to type the key at a hidden prompt.");
    apiKey = await readHidden(process.stdin, process.stdout, "API key (hidden): ");
  }
  const result = await setup({ ...options, apiKey, choose: process.stdin.isTTY ? chooseFromList : null });
  console.log(`AI ready: format ${result.format}, model ${result.model}, ${result.roundTrip}. Target: ${options.target}.`);
  console.log(options.target === "pages"
    ? "Next: rebuild and deploy the page (npm run build, then deploy) so the AI entry appears."
    : "Next: rebuild (npm run build) and restart the local preview.");
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  main(process.argv.slice(2)).catch((error) => { console.error(error.message); process.exit(1); });
}

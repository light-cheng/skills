#!/usr/bin/env node
// Strict Seam 1 validator for SKILL.md YAML frontmatter, agents/openai.yaml
// invocation policy sync, and internal relative markdown/HTML links.

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { createRequire } from "node:module";
import { basename, delimiter, dirname, extname, join, relative, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const defaultRepoRoot = resolve(scriptDir, "..");

function loadYamlModule() {
  const req = createRequire(import.meta.url);
  const searchPaths = [join(defaultRepoRoot, "node_modules")];

  if (process.env.NODE_PATH) {
    for (const entry of process.env.NODE_PATH.split(delimiter)) {
      if (entry) {
        searchPaths.push(resolve(entry));
      }
    }
  }

  const gitCommon = spawnSync("git", ["rev-parse", "--git-common-dir"], {
    cwd: defaultRepoRoot,
    encoding: "utf8",
  });
  if (gitCommon.status === 0 && gitCommon.stdout.trim()) {
    const commonDir = resolve(defaultRepoRoot, gitCommon.stdout.trim());
    searchPaths.push(join(dirname(commonDir), "node_modules"));
  }

  const resolved = req.resolve("yaml", { paths: searchPaths });
  return req(resolved);
}

const YAML = loadYamlModule();

function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseArgs(argv) {
  let repoRoot = defaultRepoRoot;
  let requireSkills = false;
  const targets = [];

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--repo") {
      if (i + 1 >= argv.length) {
        throw new Error("--repo requires a directory argument");
      }
      repoRoot = resolve(argv[i + 1]);
      i += 1;
    } else if (arg === "--require-skills") {
      requireSkills = true;
    } else if (arg.startsWith("-")) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      targets.push(resolve(arg));
    }
  }

  return { repoRoot, requireSkills, targets };
}

function listSubdirs(parentDir) {
  if (!existsSync(parentDir)) {
    return [];
  }
  return readdirSync(parentDir)
    .filter((name) => !name.startsWith("."))
    .map((name) => join(parentDir, name))
    .filter((fullPath) => statSync(fullPath).isDirectory())
    .sort();
}

function discoverSkillPackages(repoRoot) {
  const found = [...listSubdirs(join(repoRoot, "skills", "core"))];
  for (const pluginDir of listSubdirs(join(repoRoot, "plugins"))) {
    found.push(...listSubdirs(join(pluginDir, "skills")));
  }
  return found;
}

function extractFrontmatter(content) {
  const normalized = content.replace(/\r\n/g, "\n");
  if (!normalized.startsWith("---\n")) {
    return { error: "SKILL.md must begin with a '---' YAML frontmatter block" };
  }
  const closingIndex = normalized.indexOf("\n---", 4);
  if (closingIndex === -1) {
    return { error: "SKILL.md is missing a closing '---' YAML frontmatter delimiter" };
  }
  const afterClose = normalized.slice(closingIndex + 4);
  if (afterClose.length > 0 && !afterClose.startsWith("\n")) {
    return { error: "Closing '---' delimiter in SKILL.md must sit on its own line" };
  }
  return {
    frontmatter: normalized.slice(4, closingIndex),
    body: afterClose.startsWith("\n") ? afterClose.slice(1) : afterClose,
  };
}

function parseStrictYaml(source, label, errors) {
  const doc = YAML.parseDocument(source, { strict: true, uniqueKeys: true });
  for (const err of doc.errors) {
    errors.push(`${label}: YAML error: ${err.message.trim()}`);
  }
  for (const warn of doc.warnings) {
    errors.push(`${label}: YAML warning: ${warn.message.trim()}`);
  }
  if (doc.errors.length > 0) {
    return null;
  }
  const value = doc.toJS();
  if (!isPlainObject(value)) {
    errors.push(`${label}: root YAML node must be a mapping`);
    return null;
  }
  return value;
}

function stripCodeAndComments(markdown) {
  const normalized = markdown.replace(/\r\n/g, "\n");
  const lines = normalized.split("\n");
  const keptLines = [];
  let activeFence = null;

  for (const line of lines) {
    const fenceMatch = line.match(/^\s*(`{3,}|~{3,})/);
    if (!activeFence) {
      if (fenceMatch) {
        activeFence = { char: fenceMatch[1][0], length: fenceMatch[1].length };
        continue;
      }
      keptLines.push(line);
    } else if (
      fenceMatch &&
      fenceMatch[1][0] === activeFence.char &&
      fenceMatch[1].length >= activeFence.length &&
      line.trim() === fenceMatch[1]
    ) {
      activeFence = null;
    }
  }

  return keptLines
    .join("\n")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/`+[^`]*`+/g, "");
}

function extractRelativeTargets(markdown) {
  const cleaned = stripCodeAndComments(markdown);
  const rawTargets = [];

  const mdLinkRegex = /!?\[[^\]]*\]\(([^)]+)\)/g;
  for (const match of cleaned.matchAll(mdLinkRegex)) {
    let inner = match[1].trim();
    if (inner.startsWith("<") && inner.includes(">")) {
      inner = inner.slice(1, inner.indexOf(">")).trim();
    } else {
      inner = inner.split(/\s+/)[0];
    }
    if (inner) {
      rawTargets.push(inner);
    }
  }

  const htmlAttrRegex = /\b(?:src|href|srcset)\s*=\s*["']([^"']+)["']/gi;
  for (const match of cleaned.matchAll(htmlAttrRegex)) {
    const firstCandidate = match[1].split(",")[0].trim().split(/\s+/)[0];
    if (firstCandidate) {
      rawTargets.push(firstCandidate);
    }
  }

  return rawTargets.filter((target) => {
    if (target.startsWith("#") || target.startsWith("//")) {
      return false;
    }
    if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(target)) {
      return false;
    }
    return true;
  });
}

function collectMarkdownFiles(dirPath) {
  const results = [];
  if (!existsSync(dirPath)) {
    return results;
  }
  const ignored = new Set([".git", "node_modules", "__pycache__", ".pytest_cache", ".scratch"]);
  for (const entry of readdirSync(dirPath)) {
    if (ignored.has(entry) || entry.startsWith(".")) {
      continue;
    }
    const fullPath = join(dirPath, entry);
    const st = statSync(fullPath);
    if (st.isDirectory()) {
      results.push(...collectMarkdownFiles(fullPath));
    } else if (st.isFile() && extname(entry).toLowerCase() === ".md") {
      results.push(fullPath);
    }
  }
  return results;
}

function countMeaningfulWords(markdown) {
  const stripped = stripCodeAndComments(markdown)
    .replace(/<[^>]+>/g, " ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1");
  const cjkChars = stripped.match(/[\u3400-\u9fff\uf900-\ufaff]/g) ?? [];
  const nonCjkTokens = stripped
    .replace(/[\u3400-\u9fff\uf900-\ufaff]/g, " ")
    .split(/\s+/)
    .map((tok) => tok.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ""))
    .filter(Boolean);
  return nonCjkTokens.length + cjkChars.length;
}

function checkRootReadmeWordFloor(mdPath, displayBase, errors, minWords = 40) {
  const content = readFileSync(mdPath, "utf8");
  const label = relative(displayBase, mdPath) || basename(mdPath);
  const count = countMeaningfulWords(content);
  if (count < minWords) {
    errors.push(`${label}: word count is ${count}, expected at least ${minWords} words`);
  }
}

function checkMarkdownLinks(mdPath, displayBase, errors) {
  const content = readFileSync(mdPath, "utf8");
  const label = relative(displayBase, mdPath) || basename(mdPath);
  for (const rawTarget of extractRelativeTargets(content)) {
    const withoutFragment = rawTarget.split("#")[0].split("?")[0];
    if (!withoutFragment) {
      continue;
    }
    let decoded = withoutFragment;
    try {
      decoded = decodeURIComponent(withoutFragment);
    } catch {
      // Keep literal target when percent-decoding is not applicable.
    }
    const resolvedTarget = resolve(dirname(mdPath), decoded);
    if (!existsSync(resolvedTarget)) {
      errors.push(`${label}: broken relative link '${rawTarget}' (missing ${resolvedTarget})`);
    }
  }
}

function validateSkillPackage(pkgDir, displayBase, errors) {
  const pkgLabel = relative(displayBase, pkgDir) || basename(pkgDir);
  if (!existsSync(pkgDir) || !statSync(pkgDir).isDirectory()) {
    errors.push(`${pkgLabel}: skill package directory does not exist`);
    return;
  }

  const expectedName = basename(pkgDir);
  const skillMdPath = join(pkgDir, "SKILL.md");
  const openaiYamlPath = join(pkgDir, "agents", "openai.yaml");

  if (!existsSync(skillMdPath)) {
    errors.push(`${pkgLabel}: missing SKILL.md`);
    return;
  }

  const skillContent = readFileSync(skillMdPath, "utf8");
  const extracted = extractFrontmatter(skillContent);
  if (extracted.error) {
    errors.push(`${pkgLabel}/SKILL.md: ${extracted.error}`);
    return;
  }

  const fm = parseStrictYaml(extracted.frontmatter, `${pkgLabel}/SKILL.md`, errors);
  if (!fm) {
    return;
  }

  if (typeof fm.name !== "string" || fm.name.trim() === "") {
    errors.push(`${pkgLabel}/SKILL.md: 'name' must be a non-empty string`);
  } else if (fm.name !== expectedName) {
    errors.push(`${pkgLabel}/SKILL.md: frontmatter name '${fm.name}' must match directory '${expectedName}'`);
  }

  if (typeof fm.description !== "string" || fm.description.trim() === "") {
    errors.push(`${pkgLabel}/SKILL.md: 'description' must be a non-empty string`);
  }

  if ("disable-model-invocation" in fm) {
    if (fm["disable-model-invocation"] !== true) {
      errors.push(
        `${pkgLabel}/SKILL.md: omit 'disable-model-invocation' on model-invoked skills (only 'disable-model-invocation: true' is permitted)`,
      );
    }
  }

  if ("argument-hint" in fm && (typeof fm["argument-hint"] !== "string" || fm["argument-hint"].trim() === "")) {
    errors.push(`${pkgLabel}/SKILL.md: 'argument-hint' must be a non-empty string`);
  }

  if (!existsSync(openaiYamlPath)) {
    errors.push(`${pkgLabel}: missing agents/openai.yaml`);
  } else {
    const openaiRaw = readFileSync(openaiYamlPath, "utf8");
    const openai = parseStrictYaml(openaiRaw, `${pkgLabel}/agents/openai.yaml`, errors);
    if (openai) {
      if (!isPlainObject(openai.interface)) {
        errors.push(`${pkgLabel}/agents/openai.yaml: 'interface' must be a mapping`);
      } else {
        if (typeof openai.interface.display_name !== "string" || openai.interface.display_name.trim() === "") {
          errors.push(`${pkgLabel}/agents/openai.yaml: 'interface.display_name' must be a non-empty string`);
        }
        if (
          typeof openai.interface.short_description !== "string" ||
          openai.interface.short_description.trim() === ""
        ) {
          errors.push(`${pkgLabel}/agents/openai.yaml: 'interface.short_description' must be a non-empty string`);
        }
      }

      if (!isPlainObject(openai.policy) || typeof openai.policy.allow_implicit_invocation !== "boolean") {
        errors.push(`${pkgLabel}/agents/openai.yaml: 'policy.allow_implicit_invocation' must be a boolean`);
      } else {
        const isUserInvoked = fm["disable-model-invocation"] === true;
        const expectedImplicit = !isUserInvoked;
        if (openai.policy.allow_implicit_invocation !== expectedImplicit) {
          errors.push(
            `${pkgLabel}: invocation metadata out of sync (SKILL.md disable-model-invocation=${Boolean(
              fm["disable-model-invocation"],
            )} requires agents/openai.yaml policy.allow_implicit_invocation=${expectedImplicit})`,
          );
        }
      }
    }
  }

  for (const mdFile of collectMarkdownFiles(pkgDir)) {
    checkMarkdownLinks(mdFile, displayBase, errors);
  }
}

function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(`error: ${err.message}`);
    process.exit(1);
  }

  const { repoRoot, requireSkills, targets } = parsed;
  const skillDirs = targets.length > 0 ? targets : discoverSkillPackages(repoRoot);
  const errors = [];

  if (requireSkills && skillDirs.length === 0) {
    errors.push(`No skill packages found under ${repoRoot}`);
  }

  for (const pkgDir of skillDirs) {
    validateSkillPackage(pkgDir, repoRoot, errors);
  }

  if (targets.length === 0) {
    for (const rootDoc of ["README.md", "README.zh-CN.md"]) {
      const docPath = join(repoRoot, rootDoc);
      if (existsSync(docPath)) {
        checkMarkdownLinks(docPath, repoRoot, errors);
        checkRootReadmeWordFloor(docPath, repoRoot, errors);
      }
    }
  }

  if (errors.length > 0) {
    for (const err of errors) {
      console.error(`FAIL: ${err}`);
    }
    process.exit(1);
  }

  console.log(`OK: validated ${skillDirs.length} skill package(s).`);
}

main();

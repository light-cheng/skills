#!/usr/bin/env node
// Synchronizes or checks package.json version across both plugin manifests
// (.claude-plugin/plugin.json and plugins/light-manuscript/.claude-plugin/plugin.json),
// and enforces the pure-skills manifest rule (no mcpServers block).

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const defaultRepoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function parseArgs(argv) {
  let repoRoot = defaultRepoRoot;
  let checkOnly = false;
  let requireManifests = false;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--repo") {
      if (i + 1 >= argv.length) {
        throw new Error("--repo requires a directory argument");
      }
      repoRoot = resolve(argv[i + 1]);
      i += 1;
    } else if (arg === "--check") {
      checkOnly = true;
    } else if (arg === "--require-manifests") {
      requireManifests = true;
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }

  return { repoRoot, checkOnly, requireManifests };
}

function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(`error: ${err.message}`);
    process.exit(1);
  }

  const { repoRoot, checkOnly, requireManifests } = options;
  const packageJsonPath = join(repoRoot, "package.json");
  if (!existsSync(packageJsonPath)) {
    console.error(`error: missing ${packageJsonPath}`);
    process.exit(1);
  }

  const { version } = JSON.parse(readFileSync(packageJsonPath, "utf8"));
  if (typeof version !== "string" || version.trim() === "") {
    console.error(`error: package.json is missing a valid version string`);
    process.exit(1);
  }

  const pluginManifestRelPaths = [
    ".claude-plugin/plugin.json",
    "plugins/light-manuscript/.claude-plugin/plugin.json",
  ];
  const marketplaceRelPath = ".claude-plugin/marketplace.json";
  const errors = [];
  let checkedCount = 0;

  for (const relPath of pluginManifestRelPaths) {
    const fullPath = join(repoRoot, relPath);
    if (!existsSync(fullPath)) {
      if (requireManifests) {
        errors.push(`missing required manifest: ${relPath}`);
      }
      continue;
    }

    checkedCount += 1;
    const raw = readFileSync(fullPath, "utf8");
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (err) {
      errors.push(`${relPath}: invalid JSON (${err.message})`);
      continue;
    }

    if ("mcpServers" in parsed) {
      errors.push(`${relPath}: 'mcpServers' is forbidden in pure-skills plugin manifests`);
      continue;
    }

    if (parsed.version === version) {
      console.log(`${relPath} version is ${version} (in sync)`);
      continue;
    }

    if (checkOnly) {
      errors.push(
        `${relPath} version is '${parsed.version}', expected '${version}' from package.json`,
      );
      continue;
    }

    const updated = raw.replace(/("version"\s*:\s*")[^"]*(")/, `$1${version}$2`);
    if (JSON.parse(updated).version !== version) {
      errors.push(`${relPath}: failed to rewrite version field`);
      continue;
    }

    writeFileSync(fullPath, updated, "utf8");
    console.log(`${relPath} version ${parsed.version} -> ${version}`);
  }

  const marketplacePath = join(repoRoot, marketplaceRelPath);
  if (!existsSync(marketplacePath)) {
    if (requireManifests) {
      errors.push(`missing required manifest: ${marketplaceRelPath}`);
    }
  } else {
    try {
      const marketplace = JSON.parse(readFileSync(marketplacePath, "utf8"));
      if (Array.isArray(marketplace.plugins)) {
        for (const entry of marketplace.plugins) {
          if (entry && typeof entry === "object" && "mcpServers" in entry) {
            errors.push(`${marketplaceRelPath}: plugin entry '${entry.name}' must not declare mcpServers`);
          }
        }
      }
    } catch (err) {
      errors.push(`${marketplaceRelPath}: invalid JSON (${err.message})`);
    }
  }

  if (errors.length > 0) {
    for (const err of errors) {
      console.error(`FAIL: ${err}`);
    }
    process.exit(1);
  }

  if (checkedCount === 0) {
    console.log(`OK: package.json version is ${version} (0 plugin manifests present yet).`);
  }
}

main();

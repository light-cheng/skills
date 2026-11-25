#!/usr/bin/env node
// Cross-platform pytest runner used by `npm test` and CI.
// Dynamically discovers root `tests/`, `skills/*/*/tests`, and `plugins/*/skills/*/tests`
// unless explicit paths/args are passed on the command line.

import { existsSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

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

function discoverPytestSuites() {
  const suites = [];
  if (existsSync(join(repoRoot, "tests"))) {
    suites.push("tests");
  }
  for (const categoryOrSkill of listSubdirs(join(repoRoot, "skills"))) {
    if (existsSync(join(categoryOrSkill, "SKILL.md"))) {
      const directTests = join(categoryOrSkill, "tests");
      if (existsSync(directTests)) {
        suites.push(relative(repoRoot, directTests));
      }
      continue;
    }
    for (const skillDir of listSubdirs(categoryOrSkill)) {
      const testsDir = join(skillDir, "tests");
      if (existsSync(testsDir)) {
        suites.push(relative(repoRoot, testsDir));
      }
    }
  }
  for (const pluginDir of listSubdirs(join(repoRoot, "plugins"))) {
    for (const skillDir of listSubdirs(join(pluginDir, "skills"))) {
      const testsDir = join(skillDir, "tests");
      if (existsSync(testsDir)) {
        suites.push(relative(repoRoot, testsDir));
      }
    }
  }
  return suites;
}

function commandWorks(cmd, args) {
  const res = spawnSync(cmd, args, { stdio: "ignore" });
  return res.status === 0;
}

function pythonAtLeast310(pythonBin) {
  const res = spawnSync(
    pythonBin,
    ["-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"],
    { stdio: "ignore" },
  );
  return res.status === 0;
}

function resolvePytestRunner() {
  if (process.env.PYTEST_BIN) {
    return [process.env.PYTEST_BIN, []];
  }
  for (const py of ["python3.13", "python3.12", "python3.11", "python3.10"]) {
    if (commandWorks(py, ["-m", "pytest", "--version"])) {
      return [py, ["-m", "pytest"]];
    }
  }
  if (pythonAtLeast310("python3") && commandWorks("python3", ["-m", "pytest", "--version"])) {
    return ["python3", ["-m", "pytest"]];
  }
  if (commandWorks("pytest", ["--version"])) {
    return ["pytest", []];
  }
  if (commandWorks("uv", ["--version"])) {
    return ["uv", ["run", "--python", "3.12", "--with", "pytest", "pytest"]];
  }
  return ["python3", ["-m", "pytest"]];
}

const userArgs = process.argv.slice(2);
const targets = userArgs.length > 0 ? userArgs : discoverPytestSuites();

if (targets.length === 0) {
  console.log("No pytest suites found.");
  process.exit(0);
}

const [cmd, baseArgs] = resolvePytestRunner();
const result = spawnSync(cmd, [...baseArgs, ...targets], {
  cwd: repoRoot,
  stdio: "inherit",
});

process.exit(result.status ?? 1);

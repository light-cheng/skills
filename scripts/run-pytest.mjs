#!/usr/bin/env node
// Cross-platform pytest runner used by `npm test` and CI.
// Discovers active pytest directories in the repository unless explicit paths/args are given.

import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const defaultSuites = [
  "tests",
  "skills/core/agent-config/tests",
  "plugins/light-manuscript/skills/manuscript-ops/tests",
];

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
const targets =
  userArgs.length > 0
    ? userArgs
    : defaultSuites.filter((rel) => existsSync(join(repoRoot, rel)));

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

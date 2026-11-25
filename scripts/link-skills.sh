#!/usr/bin/env bash
set -euo pipefail

# Dev-only maintainer helper for local development.
# Symlinks repository skills into local harness discovery directories:
#   - ~/.claude/skills  (Claude Code)
#   - ~/.agents/skills  (Codex and Agent Skills-compatible harnesses)
#
# By default, links only the 8 core skills under skills/core/*.
# Pass --all or --with-optional to also link optional plugins under plugins/*/skills/*.

INCLUDE_OPTIONAL=0

for arg in "$@"; do
  case "$arg" in
    --all|--with-optional)
      INCLUDE_OPTIONAL=1
      ;;
    -h|--help)
      echo "Usage: $0 [--all | --with-optional]"
      exit 0
      ;;
    *)
      echo "error: unknown option '$arg' (expected --all or --with-optional)" >&2
      exit 1
      ;;
  esac
done

REPO="$(cd "$(dirname "$0")/.." && pwd)"

if [ -n "${LINK_SKILLS_DESTS:-}" ]; then
  IFS=':' read -r -a DESTS <<< "$LINK_SKILLS_DESTS"
else
  DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")
fi

resolve_realpath() {
  python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$1"
}

REPO_REAL="$(resolve_realpath "$REPO")"

names=()
srcs=()

collect_from_root() {
  local search_root="$1"
  if [ ! -d "$search_root" ]; then
    return 0
  fi
  while IFS= read -r -d '' skill_md; do
    local src
    src="$(dirname "$skill_md")"
    names+=("$(basename "$src")")
    srcs+=("$src")
  done < <(find "$search_root" -mindepth 2 -maxdepth 4 -name SKILL.md -not -path '*/node_modules/*' -print0 | sort -z)
}

collect_from_root "$REPO/skills/core"
if [ "$INCLUDE_OPTIONAL" -eq 1 ]; then
  collect_from_root "$REPO/plugins"
fi

for DEST in "${DESTS[@]}"; do
  if [ -L "$DEST" ]; then
    resolved="$(resolve_realpath "$DEST")"
    case "$resolved" in
      "$REPO_REAL"|"$REPO_REAL"/*)
        echo "error: $DEST is a symlink into this repository ($resolved)." >&2
        echo "Remove it (rm \"$DEST\") and re-run so a standalone directory is created." >&2
        exit 1
        ;;
    esac
  fi

  mkdir -p "$DEST"

  if [ "${#names[@]}" -eq 0 ]; then
    continue
  fi

  for i in "${!names[@]}"; do
    name="${names[$i]}"
    src="${srcs[$i]}"
    target="$DEST/$name"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
      rm -rf "$target"
    fi

    ln -sfn "$src" "$target"
    echo "linked $name -> $src ($DEST)"
  done
done

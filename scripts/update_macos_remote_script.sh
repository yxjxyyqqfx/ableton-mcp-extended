#!/usr/bin/env bash
# Sync the AbletonMCP Remote Script from this fork into a macOS Ableton Live
# install, drop the stale __pycache__ so Live re-byte-compiles on next reload,
# and print a tiny verification summary.
#
# Fork-only convenience — NOT for upstream PR. Hardcoded to the OCP layout
# (workspace under /Users/user/code/ableton-mcp-fork on the host, Ableton Live
# 12 Beta installed under /Applications/...). Override via env vars.
#
# Usage:
#     bash scripts/update_macos_remote_script.sh
#     # or with overrides:
#     ABLETON_APP="/Applications/Ableton Live 12 Suite.app" \
#         bash scripts/update_macos_remote_script.sh
#
# Env overrides:
#     FORK_ROOT      — workspace root (default: /Users/user/code/ableton-mcp-fork)
#     ABLETON_APP    — .app bundle path (default: /Applications/Ableton Live 12 Beta.app)
#     SCRIPT_FOLDER  — folder name inside MIDI Remote Scripts (default: AbletonMCP)
#     DRY_RUN=1      — print actions without executing
#
# Exit codes:
#     0  success
#     1  source __init__.py not found
#     2  Ableton .app not found (or not the expected layout)
#     3  cp/rm failed

set -Eeuo pipefail

FORK_ROOT="${FORK_ROOT:-/Users/user/code/ableton-mcp-fork}"
ABLETON_APP="${ABLETON_APP:-/Applications/Ableton Live 12 Beta.app}"
SCRIPT_FOLDER="${SCRIPT_FOLDER:-AbletonMCP}"
DRY_RUN="${DRY_RUN:-0}"

SRC="${FORK_ROOT}/AbletonMCP_Remote_Script/__init__.py"
DEST_DIR="${ABLETON_APP}/Contents/App-Resources/MIDI Remote Scripts/${SCRIPT_FOLDER}"
DEST="${DEST_DIR}/__init__.py"
CACHE="${DEST_DIR}/__pycache__"

run() {
    if [[ "${DRY_RUN}" == "1" ]]; then
        printf '[dry-run] %s\n' "$*"
    else
        "$@"
    fi
}

err() {
    printf '\033[31merror:\033[0m %s\n' "$*" >&2
}

info() {
    printf '\033[36m=>\033[0m %s\n' "$*"
}

ok() {
    printf '\033[32mOK\033[0m %s\n' "$*"
}

info "Source: ${SRC}"
info "Dest  : ${DEST}"
info "Cache : ${CACHE}"
echo

if [[ ! -f "${SRC}" ]]; then
    err "Source __init__.py not found at ${SRC}"
    err "  set FORK_ROOT=/path/to/ableton-mcp-fork and re-run"
    exit 1
fi

if [[ ! -d "${ABLETON_APP}" ]]; then
    err "Ableton .app not found at ${ABLETON_APP}"
    err "  set ABLETON_APP=/Applications/Ableton\\ Live\\ 12\\ Suite.app (or your install)"
    exit 2
fi

if [[ ! -d "${DEST_DIR}" ]]; then
    err "MIDI Remote Scripts folder not found at ${DEST_DIR}"
    err "  is the SCRIPT_FOLDER name correct? (default: AbletonMCP)"
    exit 2
fi

# Snapshot the OLD file size/mtime for the summary
if [[ -f "${DEST}" ]]; then
    OLD_BYTES="$(wc -c <"${DEST}" | tr -d ' ')"
    OLD_MTIME="$(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "${DEST}" 2>/dev/null || date -r "${DEST}" '+%Y-%m-%d %H:%M:%S')"
else
    OLD_BYTES="(absent)"
    OLD_MTIME="(absent)"
fi

info "Copying __init__.py ..."
run cp "${SRC}" "${DEST}"

if [[ -d "${CACHE}" ]]; then
    info "Removing stale __pycache__ ..."
    run rm -rf "${CACHE}"
else
    info "No __pycache__ to remove (clean state)"
fi

# Verify the copy landed
if [[ "${DRY_RUN}" != "1" ]]; then
    NEW_BYTES="$(wc -c <"${DEST}" | tr -d ' ')"
    NEW_MTIME="$(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "${DEST}" 2>/dev/null || date -r "${DEST}" '+%Y-%m-%d %H:%M:%S')"
    NEW_LINES="$(wc -l <"${DEST}" | tr -d ' ')"
    SRC_BYTES="$(wc -c <"${SRC}" | tr -d ' ')"
    if [[ "${NEW_BYTES}" != "${SRC_BYTES}" ]]; then
        err "Copy size mismatch — source ${SRC_BYTES}, dest ${NEW_BYTES}"
        exit 3
    fi
    echo
    ok "Updated."
    printf '   Old:  %s bytes  @  %s\n' "${OLD_BYTES}" "${OLD_MTIME}"
    printf '   New:  %s bytes  @  %s  (%s lines)\n' "${NEW_BYTES}" "${NEW_MTIME}" "${NEW_LINES}"
fi

echo
info "Next: reload Control Surface in Ableton"
echo "   Settings (⌘,) → Link/Tempo/MIDI → Control Surface row with 'AbletonMCP':"
echo "       set to None  →  set back to AbletonMCP"
echo "   (or restart Ableton entirely if reload doesn't pick up changes)"
echo
info "Verify after reload:"
echo "   In Live's status bar look for:"
echo "       'AbletonMCP: Listening for commands on port 9877'"
echo
info "Smoke test from container:"
echo "   .venv/bin/python -m pytest tests/integration/test_live_smoke.py -v -m integration"

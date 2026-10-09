#!/usr/bin/env bash
# Run the bounded 384-block diagnostic with reversible per-executable WER minidumps.
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
	printf 'usage: %s RUNNER_OUTPUT DUMP_FOLDER RECEIPT_FOLDER [--registry-only]\n' "$0" >&2
	exit 2
fi

RUNNER_OUTPUT=$1
DUMP_FOLDER=$2
RECEIPT_FOLDER=$3
MODE=${4:-}
if [[ -n "$MODE" && "$MODE" != "--registry-only" ]]; then
	printf 'unsupported mode: %s\n' "$MODE" >&2
	exit 2
fi

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
ROOT_WINDOWS=$(cygpath -m "$ROOT")
DUMP_FOLDER_WINDOWS=$(cygpath -w "$DUMP_FOLDER")
WER_KEY='HKCU\Software\Microsoft\Windows\Windows Error Reporting\LocalDumps\godot.exe'
created_key=0
for directory in "$DUMP_FOLDER" "$RECEIPT_FOLDER"; do
	if [[ -d "$directory" && -n "$(find "$directory" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
		printf 'directory must be absent or empty: %s\n' "$directory" >&2
		exit 2
	fi
	mkdir -p "$directory"
done

# Never overwrite a developer's existing per-executable dump policy.
set +e
reg.exe query "$WER_KEY" > "$RECEIPT_FOLDER/pre-query.txt" 2>&1
pre_query_exit=$?
set -e
printf '%s\n' "$pre_query_exit" > "$RECEIPT_FOLDER/pre-query-exit.txt"
if [[ $pre_query_exit -eq 0 ]]; then
	printf 'refusing to replace existing registry key: %s\n' "$WER_KEY" >&2
	exit 3
fi

cleanup() {
	local run_exit=$?
	local post_query_exit
	trap - EXIT INT TERM

	if [[ $created_key -eq 1 ]]; then
		if ! reg.exe delete "$WER_KEY" //f > "$RECEIPT_FOLDER/delete.txt" 2>&1; then
			run_exit=1
		fi
	fi

	set +e
	reg.exe query "$WER_KEY" > "$RECEIPT_FOLDER/post-query.txt" 2>&1
	post_query_exit=$?
	set -e
	printf '%s\n' "$post_query_exit" > "$RECEIPT_FOLDER/post-query-exit.txt"
	if [[ $post_query_exit -eq 0 ]]; then
		printf 'WER key still exists after cleanup: %s\n' "$WER_KEY" >&2
		run_exit=1
	fi

	exit "$run_exit"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Git Bash requires doubled option slashes so MSYS does not rewrite reg.exe switches.
reg.exe add "$WER_KEY" //v DumpFolder //t REG_EXPAND_SZ \
	//d "$DUMP_FOLDER_WINDOWS" //f > "$RECEIPT_FOLDER/add-dump-folder.txt" 2>&1
created_key=1
reg.exe add "$WER_KEY" //v DumpType //t REG_DWORD //d 1 //f \
	> "$RECEIPT_FOLDER/add-dump-type.txt" 2>&1
reg.exe add "$WER_KEY" //v DumpCount //t REG_DWORD //d 2 //f \
	> "$RECEIPT_FOLDER/add-dump-count.txt" 2>&1
reg.exe query "$WER_KEY" > "$RECEIPT_FOLDER/configured-query.txt" 2>&1
printf '0\n' > "$RECEIPT_FOLDER/configured-query-exit.txt"

if [[ "$MODE" == "--registry-only" ]]; then
	exit 0
fi

GODOT=$(mise -C "$ROOT_WINDOWS" which godot)
cd "$ROOT"
timeout 300 python tools/s07_env/run.py \
	--godot "$GODOT" \
	--output "$RUNNER_OUTPUT" \
	--variants 384 \
	--warmup 1 \
	--duration 1

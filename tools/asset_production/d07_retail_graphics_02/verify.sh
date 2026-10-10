#!/usr/bin/env bash
# Reproduce this artwork delivery using only isolated, bounded pinned processes.
set -euo pipefail
NID=d07_retail_graphics_02
T="C:/tmp/ft/assets/$NID"
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
S="$(mise which gdstyle)"
mkdir -p "$T"
run_check() {
  local name="$1" code=0
  shift
  "$@" > "$T/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$T/$name.exit"
  printf '%s: %s\n' "$name" "$code"
  return "$code"
}
run_check author python "tools/asset_production/$NID/author.py"
run_check artwork-tests python -m unittest discover \
  -s "tools/asset_production/$NID" -p 'test_*.py' -v
run_check validate timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
run_check preview timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/preview.py"
run_check import timeout 300 "$G" --headless --path . --import
run_check normalize timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize
cp "$T/prefab.json" "$T/normalize.json"
# Import again so newly saved resource UIDs are registered before fresh-process loading.
run_check import-final timeout 300 "$G" --headless --path . --import
run_check fresh timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
run_check compile timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
run_check format timeout 60 "$S" fmt --check "tools/asset_production/$NID/check_prefab.gd"
run_check lint timeout 60 "$S" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
# Update the handoff if source/export numbers changed, then write/verify final receipts.
python "tools/asset_production/$NID/record.py" --write
python "tools/asset_production/$NID/record.py"

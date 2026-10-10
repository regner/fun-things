#!/usr/bin/env bash
# Reproduce the owned assembly/artwork checks without writing shared resources.
set -euo pipefail
export PYTHONIOENCODING=utf-8 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
NID=city_parking_furniture_02
TOOLS="tools/asset_production/$NID"
SCRATCH="C:/tmp/ft/assets/$NID"
BLENDER='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
GODOT="$(mise which godot)"
GDSTYLE="$(mise which gdstyle)"
mkdir -p "$SCRATCH"
run() {
    local name="$1"
    shift
    local result=0
    "$@" > "$SCRATCH/$name.log" 2>&1 || result=$?
    echo "$result" > "$SCRATCH/$name.exit"
    if [ "$result" != 0 ]; then
        cat "$SCRATCH/$name.log"
        exit "$result"
    fi
}
run author python "$TOOLS/author.py"
run artwork-tests python "$TOOLS/test_artwork.py"
run validate timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/validate.py"
run preview timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$BLENDER" \
    -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
    --python "$TOOLS/preview.py"
run import timeout 300 "$GODOT" --headless --path . --import
run normalize timeout 180 "$GODOT" --headless --editor --path . \
    --script "res://$TOOLS/check_prefab.gd" -- --normalize
cp "$SCRATCH/prefab.json" "$SCRATCH/normalize.json"
run import-final timeout 300 "$GODOT" --headless --path . --import
run fresh timeout 180 "$GODOT" --headless --path . --script "res://$TOOLS/check_prefab.gd"
run compile timeout 180 "$GODOT" --headless --path . --check-only \
    --script "res://$TOOLS/check_prefab.gd"
run format timeout 30 "$GDSTYLE" fmt --check "$TOOLS/check_prefab.gd"
run lint timeout 30 "$GDSTYLE" --max-line-length 100 --max-warnings 0 "$TOOLS/check_prefab.gd"
python "$TOOLS/record.py" --write

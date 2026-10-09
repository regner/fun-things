# Shared Blender/glTF export contract

`export_settings.json` is the shared glTF export contract for every production asset: collection
filter, GLB, Y-up, normals/UVs, no cameras/lights, no animations/skins/morphs unless an asset's own
export script overrides them deliberately. It is byte-identical to the accepted S01 pipeline settings
(archived at `prototypes/s01/tools/s01/export_settings.json`). Asset export scripts load this file;
change it only through a reviewed pipeline change that re-exports affected assets.

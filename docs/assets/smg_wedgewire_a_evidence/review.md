# Independent SMG static checkpoint review

9 October 2026. Read-only, clean-context audit by the requested Sol 6.1/high reviewer; no modelling, animation, source/scene authoring or gameplay implementation.

## Findings by severity

**No P0, P1, P2 or P3 asset defects found within the inspected static scope.** This is bounded technical evidence, not blanket production/gameplay acceptance. Environment failures and incomplete downstream acceptance are listed separately below.

The source and imported visual retain the selected C Wedgewire direction: broad coral tapered receiver, cyan roof/side bands, charcoal grip/magazine/stock and an open muzzle rim. I personally viewed `docs/concepts/assets-v1/smg/03_wedgewire.png` and all three actual evidence PNGs. Omitted small sights/details are documented simplifications, not a demonstrated brief violation. The approximately 18 px isolated native camera weapon does **not** establish equipped city recognition or distinction from other weapon families.

## Immutable scope and guidance

- Candidate and confirmed starting/final HEAD: `bc1075c985e11ced6c2c23f948808ebf482ba178`.
- Direct parent/concept base: `4bab6edadcaf655473f36836706efe2f4a8a6683`.
- Shared base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`; verified ancestry.
- Repository: `/home/regner/.paseo/worktrees/0u71f39f/brackett-smg`. Initial/final working tree clean.
- Compared all 53 changed paths against the concept base. Scope is one saved Blender source, two explicit GLBs/import sidecars, linked weapon wrapper, saved preview/inherited camera, four scripts with UID sidecars, export/authoring helpers and scoped concept/handoff/evidence records. No shared settings, gameplay, existing fixtures or collision changes.
- Read AGENTS.md and the project art-review skill; applicable canonical assets, art direction, world layout, scene structure, catalogue, S01 import/inheritance route, validation tooling/envelope, TODO and parallel content commissioning, then the SMG handoff and concept records. Regner's C selection and explicit static-marker allowance are authoritative. No new selection/reauthoring gate was imposed.
- Producer: SMG lead `c39c4577-4fa7-4fdf-9123-db3e81a3c554`. Player owns fit/clips; effects owns feedback; external integrator owns gameplay/world placement.

## Actual independent checks and evidence

All scratch work is in `/tmp/smg-independent-xir6orth`, with private XDG data/config/cache/runtime directories. Assets/scripts were extracted from the immutable candidate with `git show`; authored bytes were never installed back into the repository. No active editor or default MCP endpoint was contacted. No registry/service/configuration was changed.

1. **Manifest/source linkage:** checked all 20 committed `fingerprints.json` entries against candidate files, and all 15 asset-profile inputs after import/checks. Zero mismatches. Source `.gdignore` exists. Reverse consumer search confirms weapon GLB → `Visuals/Model` wrapper → preview `Weapon` → inherited game camera, and review-pad GLB → preview `ReviewPad/Model`. No other runtime consumer was found. Shared catalogue reconciliation remains the explicitly assigned integrator delta, not a second writer introduced here.
2. **Pinned source inspection and reexport:** `/usr/bin/blender` is 5.2.2 LTS, hash `d13f752e3b9c`. Opened the copied saved source; inspected datablocks without mutation; executed only the candidate `export.py`. No linked libraries/file images. Metric/unit scale1; declared weapon collection has 16 meshes/five empties, 3,748 triangles; review collection has two meshes/24 triangles; all inspected mesh faces already triangulated and modifiers baked. Measurement reference remains outside exported collections. Both outputs reproduce byte-for-byte, including the recorded export receipt/settings. Weapon SHA256 `0d02e28c081bd017a640c55325c93129be1e2b672396df608cdcdb672079158d`; pad SHA256 `180b118c83c099e493708a8eef06d6a928332ae859dad8d5565a32e69503984e`. Final process used `--factory-startup -noaudio --threads 1 --background <scratch blend> --python-exit-code 1 --python <read-only inspection wrapper> -- <scratch outputs> <inspection receipt>`; wrapper invokes `export.py` with runpy. Exit0. Exact argv/log: `blender-noaudio-final-command.json`, `blender-noaudio-final.log`; source facts: `source-inspection.json`; earlier comparison: `byte-comparison.json`.
3. **GLB structure/materials/normals:** decoded actual GLB JSON and normal buffers. Weapon has 16 meshes/21 nodes/five named opaque palette materials; pad has two meshes/two named materials. No skins, animations, images or extensions. All 2,989 weapon and 48 pad exported normals are finite/unit within 0.001. No copied arrays, generated visible meshes, detached imported-child overrides or editor helper attached to the production wrapper in saved scenes/scripts. `gltf-audit.json` and `*-gltf.json` retain decoded evidence. Normal validity is not exhaustive topology or shading certification.
4. **Fresh isolated asset import:** pinned Godot `4.8.dev7.official.c971f93e7`, `--headless --editor --import --quit` in an asset-only profile; exit0 and both imports created, inputs preserved. This run contains socket/listener errors and associated RichTextLabel null-image diagnostics; it is **not diagnostic-free**. Exact argv/log: `import-command.json`, `import.log`. Scratch profile uses compatibility/dummy headless rendering; it does not independently reproduce Forward+ pixels or full-project plugins.
5. **Production bounds/socket/contact checker:** ran copied `tools/smg_wedgewire_a/check_asset.gd`, exit0/no warnings/errors. AABB minimum `(-0.135,-0.131,-0.520)`, size `(0.270,0.344,0.800)` metres; 16 meshes/3,748 triangles. All five socket positions/identity bases match source markers; model root remains identity and imported ancestry intact. Contact errors: GripContact `7.45e-10 m`, SupportHand `4.47e-9 m`, Shoulder `1.19e-8 m`, below 1 mm. This measures authored surfaces, not human fit. `contract.log`, `checks.json`.
6. **Additional independent loaded-resource checks:** inspected/reloaded wrapper, preview and inherited camera without saving/replacing authored scenes. Actual UIDs match saved declarations: wrapper `cbp2jd2aa6boi`, preview `b0gjh38di3qvl`, inherited view `8put4g1rfcel`; inherited base scene exists. Verified linked identity review-pad instance, 18 total imported ArrayMesh instances, no collision shapes/objects, skeleton or animation player, weapon height1.3 m/unit scale, perspective game camera47 m/FOV42/vertical north-up/near0.1/far160. Exit0/no diagnostics. `independent-contract.log`, scratch `project/independent_audit.gd`.
7. **Explicit compilation/style:** all four owned GDScripts compiled individually with `--headless --check-only --script`, exit0/no diagnostics. Pinned gdstyle0.3.0 lint with repository `gdstyle.toml`/zero warnings and `fmt --check`: both exit0, four files already formatted. Purpose comments, tabs and two-empty-line function spacing inspected. `compile-0.log` through `compile-3.log`, `lint.log`, `format.log`, exact commands in `checks.json`.
8. **Retained producer receipts:** checked roundtrip hashes against actual immutable scenes/source; reviewed source/export, clean-profile, routing, final checker and capture logs. Producer `roundtrip.json` asserts close/reopen/save stability after final source reimport. Independent load/reload and unchanged bytes support saved ancestry, but this audit deliberately did not repeat an editor save/reopen or establish current active-editor synchronization. Viewed all three supplied real 1280×800 PNGs; capture receipts specify Forward+/Vulkan/GTX1070, 60 cap/VSync and saved camera transforms. No new graphical capture was taken.

## Environment diagnostics and bounded retest

Initial Blender export attempt timed out60 s; factory/single-thread retry exported both outputs and wrote the receipt, then timed out35 s during PipeWire/PulseAudio shutdown with Operation not permitted. An audio-disabled retry exited0 with identical outputs. The final log retains the known optional MeshOptimizer missing-library message; actual GLBs have no compression extension. One scratch inspection attempt failed because its reviewer-authored JSON serializer did not handle IDPropertyArray; corrected only that scratch serializer and reran successfully. These are not candidate geometry defects.

Independent Godot import logged `_sock == -1` / `ERR_CANT_CREATE` listeners plus associated `p_image.is_null()` diagnostics. Restricted execution is consistent with these listener failures, but the exact cause was not further investigated. The asset contract, extra resource checks and explicit compiles were diagnostic-free. Producer clean-profile evidence records a diagnostic-free import of the identical inputs; this audit does not erase its own failing diagnostics. Minimal remaining independent import check: technical integrator reruns the same isolated profile in an environment permitting Godot's editor listeners, retains full logs and verifies unchanged sidecars/scene UIDs. No asset fix is indicated by these environment errors.

## Handoff disposition and remaining acceptance

| Area | Disposition |
| --- | --- |
| Approved concept direction | Accepted by Regner; this review found no demonstrated static divergence requiring rejection |
| Rigid static source/export freshness, measured markers, linked wrapper/preview | Accepted **within bounded static technical scope** |
| Saved identities/inherited loading | Accepted for inspected saved resources; producer editor roundtrip receipt retained, independent editor roundtrip not rerun |
| Independent diagnostic-free clean import | Accepted for this isolated asset profile after the authorized escalated fresh import below; exit0/no diagnostics and unchanged inputs/UIDs |
| Full production/game acceptance | Pending; this review supplies no blanket acceptance |
| Player attachment, contact/bone fitting, holding/aim/reload/death clips and equipped city recognition | Pending player/integrator; next check is actual rig-mounted clip matrix and native camera captures in city conditions |
| Combat, physics muzzle use, VFX, world placement, multiplayer | Not applicable to this static checkpoint; integration acceptance remains pending respective owners |
| Weapon armature/skin/weapon clips, textures and additional LOD work | Not applicable to this rigid palette visual; default import LOD/shadow generation retained, no measured reason for extra LOD |
| Windows/Steam/Deck, packaged builds and sustained performance | Pending/unmeasured; no device or performance claim |

Concurrent dependency notice: coordinator reports `shared_humanoid/1.0.0` published at `3eccf8f691fe34132ee8504d10dfceda4f7e2bb6` on `art/brackett-player-character`, with `docs/assets/shared_humanoid_rig.md`. Candidate handoff lines115–117 predate that publication. Treat their “versioned rest rig … does not exist yet” clause as a concurrent documentation update for the lead's final receipt commit, not an immutable-source defect or equipped acceptance. Bone-to-grip/contact fitting and production clips remain pending. That other branch was not fetched, imported or reviewed here.

Final verdict: no observed blocking static-asset defect; reproducible source/exports and saved measured interfaces support the bounded technical checkpoint. The independent listener/import limitation is closed by the follow-up below. Final production acceptance remains pending downstream equipped/gameplay/device evidence. No source, scene, source identity, project setting or active editor was changed.

## Authorized listener-only follow-up — 9 October 2026

Reran only the same isolated candidate asset profile with `require_escalated`, using the private editor debugger listener `tcp://127.0.0.1:21607`. Escalation was allowed. No MCP endpoint was contacted; no active editor was used/stopped; reserved16650–16654,19650–19654 and20650–20654 were untouched. No modelling/spatial work, asset mutation, shared service/configuration change or broader re-audit occurred.

To require actual fresh imports, moved only this review's scratch `.godot` cache to `/tmp/smg-independent-xir6orth/initial-import-cache`, then launched the import with separate private `listener-followup-{data,config,cache,runtime}` XDG directories. The copied `project.godot` and all candidate inputs were unchanged.

Exact command:

```text
/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --path /tmp/smg-independent-xir6orth/project --headless --editor --debug-server tcp://127.0.0.1:21607 --import --quit
```

**Actual result:** exit0 in2.73 s, no ERROR/WARNING/SCRIPT ERROR diagnostics in the full retained stdout/stderr log. Both GLBs freshly imported to the same recorded imported `.scn` paths. All15 asset-profile inputs match their before-import bytes and the candidate fingerprints after import, including both `.glb.import` sidecars, all three scenes and four script UID sidecars. UID declarations/references are unchanged. This follow-up inspected persisted UID declarations; it did not rerun resource instantiation or an editor save/reopen.

Full log: `/tmp/smg-independent-xir6orth/listener-followup-import.log`.
Exact argv, exit, elapsed time, diagnostics, before/after SHA256 and UID snapshots, and generated imports: `/tmp/smg-independent-xir6orth/listener-followup-result.json`.
Read-only bounded runner: `/tmp/smg-independent-xir6orth/listener_import_followup.py`.

Disposition: **the independent diagnostic-free isolated-import limitation is closed.** Earlier restricted-import errors remain retained as historical environment failures; no candidate fix was necessary. The original bounded static technical verdict is supported with this additional clean-import evidence. Equipped recognition/fit/clips, city/gameplay/network/device acceptance and independently repeated editor save/reopen remain outside this follow-up and retain their original status.

## Durable receipt

Reviewer: Paseo agent `e5300248-3294-4767-95cf-4c85ad677370`,
`codex/gpt-6.1-sol`, high. The SMG lead copied this review after the independent
listener follow-up. [Retained reviewer evidence](independent-review-evidence.tar.gz)
contains the scratch top-level JSON/log receipts and independent check scripts;
original temporary paths above describe where those checks actually ran.
Implementation remains exactly candidate `bc1075c985e11ced6c2c23f948808ebf482ba178`.

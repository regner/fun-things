# M1-C4.1 HUD shell evidence

Captured 10 October 2026 on Windows 11 with the pinned Godot
`4.8.dev7.official.c971f93e7`, Forward+, and an NVIDIA RTX 4070 Laptop GPU.
The editor was not running and MCP editor tools were unavailable, so the saved HUD
scene was authored directly as text, imported with the pinned editor, and validated
through the canonical production checks.

Both images are from the saved Boot → standalone Match composition. The capture
runner injected Boot's `SessionService` through `LocalRig.bind_session`, retained the
normal controlled-player binding, rendered an exact-size `SubViewport`, and set
`Engine.max_fps = 60` before scene creation. The runner and logs remain outside the
repository under `C:/tmp/ft/lanes/m1-c4-1/`.

| Capture | Bytes | SHA-256 |
| --- | ---: | --- |
| [`hud-1920x1080.png`](hud-1920x1080.png) | 25,235 | `bf4f98099c799be2d4457f94d41157e49105b759faa9b737185b461aac32ad81` |
| [`hud-1280x800.png`](hud-1280x800.png) | 19,455 | `05b933983ac894cdbae9e751ebb9cf601f6425ee7df6cf677b108fe8079602ca` |

The first 1920×1080 window-resize capture attempt exposed an engine image-readback
crash after dynamic root-window resizing. No result was accepted from that run. The
bounded replacement used a fixed exact-size `SubViewport`; both accepted processes
exited 0 and reported their requested image dimensions and 60 FPS cap.

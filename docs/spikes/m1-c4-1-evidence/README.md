# M1-C4.1 HUD shell evidence

Captured 10 October 2026 on Windows 11 with the pinned Godot
`4.8.dev7.official.c971f93e7`, Forward+, and an NVIDIA RTX 4070 Laptop GPU.
The editor was not running and MCP editor tools were unavailable, so the saved HUD
scene was authored directly as text, imported with the pinned editor, and validated
through the canonical production checks.

Both images are from the saved Boot → standalone Match composition. The capture
runner injected Boot's `SessionService` through `LocalRig.bind_session`, retained the
normal controlled-player binding, rendered an exact-size `SubViewport`, and set
`Engine.max_fps = 60` before scene creation. No `PlayerLifecycle` exists yet, so the
captures intentionally hide the life row rather than presenting an actor-derived default.
The runner and logs remain outside the repository under `C:/tmp/ft/lanes/m1-c4-1/`.

| Capture | Bytes | SHA-256 |
| --- | ---: | --- |
| [`hud-1920x1080.png`](hud-1920x1080.png) | 22,185 | `b199827c693b0f61b00af30a24014affdd72f87ed0b31572b32654c559ff17cf` |
| [`hud-1280x800.png`](hud-1280x800.png) | 16,702 | `ef7f6fa2b6dc2deceed50f8d1b30134aa32e373826719fcfa0920ad5fbaed901` |

The first 1920×1080 window-resize capture attempt exposed an engine image-readback
crash after dynamic root-window resizing. No result was accepted from that run. The
bounded replacement used a fixed exact-size `SubViewport`; both accepted processes
exited 0 and reported their requested image dimensions and 60 FPS cap.

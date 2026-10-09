# Godot Road Generator provenance

- Project: Godot Road Generator by Moo-Ack! Productions (TheDuckCow)
- Upstream: <https://github.com/TheDuckCow/godot-road-generator>
- Version/tag: `0.9.4`
- Commit: `9d144dc4a28dd6bee870895d2b77d69174356281`
- Commit date: 2026-09-30
- Vendored: 2026-10-09
- Archive: `git archive --format=tar 9d144dc4a28dd6bee870895d2b77d69174356281`
- Archive SHA-256: `6bd2d4c013d2fb7a7946e02595c77deb7df6f02a8ba62698e6aec6715bcd8757`
- License: MIT; see [LICENSE](LICENSE).

Release 0.9.4 is the newest upstream tag observed on 2026-10-09. It was selected over
0.9.3 because it is the tagged Godot 4.8 compatibility hotfix and passed the RT-01
road construction, lane, custom-container, procedural-intersection, save/reload and
runtime preflight on the project's pinned Godot 4.8-dev7 engine.

The upstream files are unmodified. `PROVENANCE.md` is the only project-added file in
this directory, so there is no local vendor patch. The six failures seen with upstream's
bundled GUT 9.4.0 were type-assertion harness failures; the same 83 tests pass with the
project's GUT 9.7.1 when its newer automatic engine-error tracker is disabled. See
`docs/spikes/road-tool.md` for the test names and the separately disclosed diagnostics
that the newer tracker observes. Upgrades must select another exact tag/commit and
repeat the upstream-suite, preflight, export and owner editor checks.

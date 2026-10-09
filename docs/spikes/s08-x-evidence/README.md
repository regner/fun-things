# S08-X real-project export evidence

`godotsteam-removal-receipt.json` is the compact 9 October 2026 follow-up after owner
decision 17. It binds the clean import, four rebuilt packages, continued Steam-library
rejection and 60-capped Windows release smoke. Steam and unrelated `godot-ai.exe`
processes were present, so this is functional rather than quiet/performance evidence.
Full logs/builds are outside the repository under
`C:/tmp/ft/lanes/remove-godotsteam/`.

The remaining files are compact receipts for the 8 October 2026 Windows run. Full
build folders and complete export logs remain outside the repository at
`C:/tmp/ft/lanes/s08-x-review1/`.

- `template-archive.sha256`, `template-version.txt` and
  `template-members.sha256` bind the official archive and the four x86-64 members.
- `package-inspection.json` binds all four executables/PCKs, confirms PE/ELF
  formats, finds the main scene and S06 intersection, and reports no MCP,
  GodotSteam, `steam_api*` or `libsteam_api*` package/output members.
- `native-dependency-negative.json` is the expected failed inspection after a
  deliberate `steam_api64.dll` was added beside the Windows release executable.
  Focused tests also cover the descriptor, GDExtension libraries and all four
  checked-in Steamworks dependency basenames in pack and output paths.
- `windows-smoke.*` is the release launch receipt. The environment record reports
  no `steam.exe` and zero other Godot/exported-game processes before launch. The
  engine log reports D3D12 Forward+, a 1280x800 window, 30 frames capped at 60,
  successful saved-intersection loading, absent MCP/Steam runtime surfaces, and
  exit 0 without warnings or errors.
- `export-contention.txt` records zero other Godot processes before the final
  post-rebase exports. Timing is labelled quiet, but remains functional evidence,
  not a performance benchmark.
- `export-diagnostics.log` retains the known editor/export-process diagnostics:
  the MCP 4.8 compatibility warning and Godot headless editor teardown RID/ObjectDB
  messages. All four export commands exited 0 and package inspection passed. These
  diagnostics are not present in the exported Windows runtime log; they remain an
  editor/tooling follow-up rather than being hidden.

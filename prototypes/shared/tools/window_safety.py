"""Safety guards for repository-owned windowed Godot launches."""

from __future__ import annotations

from collections.abc import Sequence

SAFE_WINDOW_FPS = 60


def capped_window_arguments() -> list[str]:
    """Return the explicit Godot arguments required for a 60 FPS window cap."""
    return ["--max-fps", str(SAFE_WINDOW_FPS)]


def require_capped_window(command: Sequence[str]) -> None:
    """Reject a windowed command unless it contains exactly the approved FPS cap."""
    values = [command[index + 1] for index, value in enumerate(command[:-1])
              if value == "--max-fps"]
    if values != [str(SAFE_WINDOW_FPS)]:
        raise ValueError(f"windowed Godot requires exactly --max-fps {SAFE_WINDOW_FPS}")


def require_capped_modes(modes: Sequence[str]) -> None:
    """Reject withdrawn graphical modes, including the device-unsafe uncapped mode."""
    if not modes or any(mode != "capped60" for mode in modes):
        raise ValueError("only capped60 windowed measurement mode is permitted")

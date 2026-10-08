#!/usr/bin/env python3
"""Derive uplink held latency and host-motion apply gaps from retained S03-R baseline logs."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent / "baseline"


def load(name):
    rows = []
    for line in (HERE / name).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("S03R "):
            try:
                rows.append(json.loads(line[5:]))
            except json.JSONDecodeError:
                pass
    return rows


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(len(values) * q))]


client, host = load("client-stdout.log"), load("host-stdout.log")
sims = [r for r in host if r["event"] == "simulation" and r["pose"]["entity"] == 2]
uplink = []
for entry in (r for r in client if r["event"] == "input" and r["index"] <= 20):
    held = [s for s in sims if s["wall_ms"] >= entry["wall_ms"] and s["held"] == [
        entry["move"], entry["turn"]]]
    if held:
        uplink.append(held[0]["wall_ms"] - entry["wall_ms"])
applies = [r["wall_ms"] for r in client if r["event"] == "apply" and r["entity"] == 2]
gaps = [b - a for a, b in zip(applies, applies[1:])]
print(json.dumps({
    "uplink_input_to_host_held_ms": {"min": min(uplink), "max": max(uplink), "n": len(uplink)},
    "client_entity2_applies": len(applies),
    "host_entity2_ticks": len(sims),
    "apply_gap_ms": {"median": pct(gaps, 0.5), "p95": pct(gaps, 0.95), "max": max(gaps)},
}, indent=1))

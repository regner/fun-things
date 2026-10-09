extends Node3D
## Saved SMG feedback assembly that pulses muzzle and impact around a continuous tracer stream.

const SHOT_INTERVAL_SECONDS: float = 0.1

var _elapsed_seconds: float = 0.0

@onready var muzzle: GPUParticles3D = $Muzzle
@onready var impact: GPUParticles3D = $Impact


## Starts the saved tracer stream and aligns the first pulse across all four shooters.
func _ready() -> void:
	$Tracer.emitting = true
	pulse()


## Pulses at a fixed visual cadence without owning weapon simulation or hit outcomes.
func _process(delta: float) -> void:
	_elapsed_seconds += delta
	if _elapsed_seconds < SHOT_INTERVAL_SECONDS:
		return

	_elapsed_seconds = fmod(_elapsed_seconds, SHOT_INTERVAL_SECONDS)
	pulse()


## Restarts the two one-shot layers; the enclosing stress coordinator never reaches inside.
func pulse() -> void:
	muzzle.restart()
	impact.restart()

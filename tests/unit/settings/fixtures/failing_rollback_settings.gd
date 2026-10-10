extends LocalSettings
## Injects promotion and rollback rename failures through the production transaction seam.

var _promotion_failed: bool = false


## Lets preservation succeed, then fails promotion and its attempted rollback distinctly.
func _rename(source_path: String, destination_path: String) -> Error:
	if source_path.ends_with(".tmp"):
		_promotion_failed = true
		return ERR_CANT_CREATE
	if _promotion_failed and source_path.ends_with(".previous"):
		return ERR_CANT_OPEN
	return super._rename(source_path, destination_path)

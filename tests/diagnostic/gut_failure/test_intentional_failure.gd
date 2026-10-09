extends GutTest


## Supplies a deliberate failure used only by the negative-detection check.
func test_gut_reports_failure() -> void:
	assert_true(false, "intentional GUT failure for runner validation")

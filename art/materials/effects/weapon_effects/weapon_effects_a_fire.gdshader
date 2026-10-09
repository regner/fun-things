shader_type spatial;
render_mode cull_disabled;
// Original effect-family shader: preserve lifetime tint in both light and emission.
void fragment() {
	ALBEDO = COLOR.rgb;
	EMISSION = COLOR.rgb * 2.2;
	ROUGHNESS = 0.95;
}

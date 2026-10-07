shader_type spatial;

// A local camera-ray cone removes only building presentation around the controlled actor.
uniform vec4 base_color : source_color = vec4(1.0);
uniform vec3 camera_world;
uniform vec3 actor_world;
uniform float cone_radius = 0.0;
varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 ray = (world_position.xz - camera_world.xz)
		/ max(camera_world.y - world_position.y, 0.01);
	vec2 focus = (actor_world.xz - camera_world.xz)
		/ max(camera_world.y - actor_world.y, 0.01);
	if (world_position.y > 0.1 && length(ray - focus) < cone_radius) {
		discard;
	}
	ALBEDO = base_color.rgb;
	ROUGHNESS = 0.8;
}

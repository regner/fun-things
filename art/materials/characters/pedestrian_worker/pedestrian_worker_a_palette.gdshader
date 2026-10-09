shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;
instance uniform vec4 skin_color : source_color = vec4(0.71765, 0.49020, 0.32549, 1.0);
instance uniform vec4 jacket_color : source_color = vec4(0.92549, 0.63529, 0.24314, 1.0);
instance uniform vec4 yoke_color : source_color = vec4(0.19608, 0.42745, 0.75294, 1.0);
instance uniform vec4 trousers_color : source_color = vec4(0.28235, 0.34902, 0.42353, 1.0);
instance uniform vec4 cap_color : source_color = vec4(0.13333, 0.32157, 0.36471, 1.0);
instance uniform vec4 shirt_color : source_color = vec4(0.14902, 0.20000, 0.23137, 1.0);
instance uniform vec4 boots_color : source_color = vec4(0.12549, 0.16863, 0.19608, 1.0);
instance uniform vec4 trim_color : source_color = vec4(0.88627, 0.83922, 0.72549, 1.0);
instance uniform vec4 hair_color : source_color = vec4(0.22353, 0.17255, 0.14510, 1.0);

void fragment() {
 int region = int(round(COLOR.r * 8.0));
 vec3 swatch = skin_color.rgb;
 if (region == 1) { swatch = jacket_color.rgb; }
 else if (region == 2) { swatch = yoke_color.rgb; }
 else if (region == 3) { swatch = trousers_color.rgb; }
 else if (region == 4) { swatch = cap_color.rgb; }
 else if (region == 5) { swatch = shirt_color.rgb; }
 else if (region == 6) { swatch = boots_color.rgb; }
 else if (region == 7) { swatch = trim_color.rgb; }
 else if (region == 8) { swatch = hair_color.rgb; }
 ALBEDO = swatch;
 ROUGHNESS = 0.78;
 SPECULAR = 0.25;
}

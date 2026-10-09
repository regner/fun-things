"""Render the final saved source without rebuilding or resaving geometry."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_04-evidence'; s=bpy.context.scene
for variant in ['compact','broad']:
 for key in ['compact','broad']:
  col=bpy.data.collections['export_city_planting_04_'+key]; col.hide_render=key!=variant; col.hide_viewport=key!=variant
 s.camera=bpy.data.objects['hero_camera']; s.render.resolution_x=1100; s.render.resolution_y=900
 s.render.filepath=str(E/(variant+'_hero.png')); bpy.ops.render.render(write_still=True)
 s.camera=bpy.data.objects['project_vertical_47m_42deg']; s.render.resolution_x=1280; s.render.resolution_y=800
 s.render.filepath=str(E/(variant+'_project_camera.png')); bpy.ops.render.render(write_still=True)

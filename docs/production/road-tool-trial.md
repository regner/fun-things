# Road tool owner trial

Use Godot `4.8.dev7.official.c971f93e7`. This is a short editor-feel check of the
vendored Godot Road Generator 0.9.4. It does not ask you to bake anything: roads stay
live in the editor and the addon ships with the game.

Open this worktree as a separate project so another checkout's editor state is not
changed:

`C:/GameDev/git/ft-lanes/rt-01`

Allow about 15 minutes. Do not commit the trial scene.

## Checklist

1. Start the pinned Godot editor, import the project above, and confirm the **Roads**
   toolbar appears in the 3D editor.
2. Create a new **3D Scene**. Name its root `RoadTrial` and save it as
   `res://road_tool_trial.tscn`.
3. Add a `RoadManager` child. Select it, open **Roads**, and choose
   **RoadContainer**. Select the new container.
4. Switch the road toolbar to **Add and Connect Mode** (the add/connect button).
   Click three separated points on the 3D ground plane to create a curved road. Note
   how long the first visible road takes and whether point placement/snapping feels
   predictable.
5. Switch to **Select Road Mode**. Move the middle `RoadPoint` with the transform
   gizmo. Adjust its prior/next curve handles. Confirm the road refresh follows the
   edit without opening Blender or pressing a bake button.
6. With an end point selected, return to **Add and Connect Mode** and extend the road
   by two points. Select one of the new points and press Delete, then use the toolbar's
   **Delete & Dissolve Road Mode** on another point. Confirm both results are clear.
7. Select both ends of one section in turn. In the Inspector, change their lane
   count/directions and lane width so the section changes from two lanes to four lanes.
   Set the parent `RoadContainer`'s **Generate AI Lanes** on. Confirm geometry and lane
   paths update; note refresh delay or visual glitches.
8. Add a second `RoadContainer` from the **Roads** menu. Create two points near the
   first road's open end. In **Add and Connect Mode**, select one open point and click
   the compatible open point on the other road. Confirm the roads connect and remain
   editable.
9. Create two more branches into that connection. Use add/connect interactions to
   convert the joined point into a procedural `RoadIntersection`. Move one branch and
   confirm the intersection and turn lanes refresh.
10. Drag
    `res://addons/road-generator/custom_containers/4way_1x1.tscn` from the FileSystem
    into the scene as another child of `RoadManager`. Confirm its mesh, collision and
    authored `RoadLane` children appear. Move it and connect one trial road to a
    compatible connector if the connection hint appears.
11. Perform Undo and Redo after a point move, lane-width change, connection and delete.
    Confirm the scene and visible geometry return to the expected state each time.
12. Save. Close the scene tab, reopen `road_tool_trial.tscn`, and confirm road points,
    connections, generated geometry, intersection, custom container and lanes remain.
13. Open **Project > Project Settings > Plugins**. Disable **RoadGenerator** and note
    whether the scene remains loadable and whether the toolbar disappears cleanly.
    Re-enable it, reopen the scene if prompted, and confirm editing works again.
14. Close the editor normally. Record any freeze, crash, recovery dialog or shutdown
    diagnostic. Delete `road_tool_trial.tscn` (and its `.uid`, if present) afterward;
    do not commit either file.

## Record

Report approximate times for first road creation, moving one point, changing lanes,
connecting roads, making the intersection, and save/close/reopen. Also report:

- whether point/handle selection and snapping felt understandable;
- whether add/delete/connect and undo/redo behaved as expected;
- whether the custom container workflow looked usable for common junction prefabs;
- whether any edit unexpectedly rebuilt unrelated roads;
- whether plugin disable/re-enable was clean; and
- any crash, warning, visual corruption or lost edit, with the exact step.

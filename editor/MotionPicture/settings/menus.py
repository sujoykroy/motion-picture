from ..commons import DictList

TopMenuItem = m = DictList("menubar")
m.add(path="File/New/Icon", icon="file_new_icon", desc="Create New Icon",
      action_name="app.create_new_document", action_param="400x400")
m.add(path="File/New/Document", icon="file_new_document", desc="Create New Document",
      action_name="app.create_new_document", action_param="1280x720")

m.add(path="File/<Open>/Open", icon="file_open", desc="Open file",
      action_name="app.open_document", action_param="", accel="<Control>o")
m.add(path="File/<Open>/Open Recent", icon="file_open_recent", desc="Open from recent files",
      action_name="app.open_recent_document")
m.add(path="File/<Open>/Save", accel="<Control>s", icon="file_save", desc="Save file",
      action_name="win.save_document")
m.add(path="File/<Open>/Save As", accel="<Shift><Control>s", icon="file_save_as",
      action_name="win.save_as_document", desc="Save file as")
m.add(path="File/<Open>/Export as Image", icon="export_to_image",
      action_name="win.export", action_param="png", desc="Export as Image")

m.add(path="Edit/<UndoRedo>/Undo", accel="<Control>z",
      action_name="win.undo_redo", action_param="undo")
m.add(path="Edit/<UndoRedo>/Redo", accel="<Control>Y",
      action_name="win.undo_redo", action_param="redo")

m.add(path="Edit/Shape/Copy", icon="copy_shape", accel="<Control><Shift>c",
      action_name="win.copy_shape_action")
m.add(path="Edit/Shape/Paste", icon="paste_shape", accel="<Control><Shift>v",
      action_name="win.paste_shape_action")
m.add(path="Edit/Shape/Delete", icon="delete_shape",
      action_name="win.delete_shape")
m.add(path="Edit/Shape/Duplicate", icon="duplicate_shape", accel="<Control>b",
      action_name="win.duplicate_shape", action_param="")
m.add(path="Edit/Shape/Import", icon="import_shape",
      action_name="win.import_shape")

m.add(path="View/Zoom To Shape", icon="zoom_to_shape", accel="<Control>m",
      action_name="win.zoom_to_shape", action_param="")
m.add(path="View/Zoom To Canvas", icon="zoom_to_canvas", accel="<Control>1",
      action_name="win.zoom_to_canvas", action_param="")

m.add(path="Edit/Shape/<Linked>/Linked Duplicate", icon="linked_duplicate_shape",
      action_name="win.duplicate_shape", action_param="linked")
m.add(path="Edit/Shape/<Linked>/Update Linked Shapes", icon="update_linked_shapes",
      action_name="win.update_linked_shapes")

m.add(path="Edit/Shape/Flip/Flip X", icon="flip_x",
      action_name="win.flip_shape", action_param="x")
m.add(path="Edit/Shape/Flip/Flip Y", icon="flip_y",
      action_name="win.flip_shape", action_param="y")

m.add(path="Edit/<Layer>/Layer Up", icon="layer_up", desc="Move shape layer up",
      action_name="win.change_shape_depth", action_param="1", icon_scale=2.)
m.add(path="Edit/<Layer>/Layer Down", icon="layer_down", desc="Move shape layer down",
      action_name="win.change_shape_depth", action_param="-1", icon_scale=2.)
m.add(path="Edit/<Layer>/Layer Top", icon="layer_top", desc="Move shape layer to top",
      action_name="win.change_shape_depth", action_param="1000", icon_scale=2.)
m.add(path="Edit/<Layer>/Layer Bottom", icon="layer_bottom", desc="Move shape layer to bottom",
      action_name="win.change_shape_depth", action_param="-1000", icon_scale=2.)

m.add(path="Edit/TimeLine/Delete Slice", icon="delete_time_slice",
      action_name="win.delete_time_slice", desc="Delete Time Slice")
m.add(path="Edit/TimeLine/Move Prop Line Up", icon="move_prop_line_up",
      action_name="win.move_prop_time_line", desc="Move Prop Line Up", action_param="-1")
m.add(path="Edit/TimeLine/Move Prop Line Down", icon="move_prop_line_down",
      action_name="win.move_prop_time_line", desc="Move Prop Line Down", action_param="1")
m.add(path="Edit/TimeLine/Split Prop Line", icon="split_prop_line",
      action_name="win.split_prop_time_line", desc="Split Prop Line")

m.add(path="Edit/Points/Join", icon="join_points", desc="Join points together",
      action_name="win.join_points_of_shape")
m.add(path="Edit/Points/Break", icon="break_point", desc="Break point into two points",
      action_name="win.insert_break_in_shape", icon_scale = 1.5)
m.add(path="Edit/Points/Delete", icon="delete_point", desc="Delete point",
      action_name="win.delete_point_of_shape", icon_scale = 1.5)
m.add(path="Edit/Points/Freely Erase", action_state=False, icon="freely_eraser",
      action_name="win.freely_erase_points", desc="Freely erase points with breaks")
m.add(path="Edit/Points/Extend", icon="extend_point", desc="Extend point into new point",
      action_name="win.extend_point_of_shape")
m.add(path="Edit/Points/Center Anchor", icon="center_anchor",
      action_name="win.center_anchor", desc="Place anchor at center")
m.add(path="Edit/Points/Copy", icon="copy_points_as_shape",
      action_name="win.copy_points_as_shape", desc="Copy Points As Shape")

m.add(path="Edit/Document/Canvas Size", icon="canvas_size",
      action_name="win.change_canvas_size", desc="Change canvas size")
m.add(path="Edit/Document/Copy Child Shape Postions",
      icon="copy_child_shape_positions", icon_scale = 1.2,
      action_name="win.copy_child_shape_positions", desc="Copy Positions")
m.add(path="Edit/Document/Apply Saved Child Shape Postions",
      icon="apply_child_shape_positions", icon_scale = 1.2,
      action_name="win.apply_child_shape_positions", desc="Apply Positions")
m.add(path="Edit/Document/Fixed Border Size", icon="fixed_border", icon_scale = 2.,
      action_name="win.border_fixed", action_state=True, desc="Fixed Border")

m.add(path="Shapes/<New>/Rectangle", icon="rectangle",
      action_name="win.create_new_shape", action_state="rect")
m.add(path="Shapes/<New>/Oval", icon="oval",
      action_name="win.create_new_shape", action_state="oval")
m.add(path="Shapes/<New>/Polygon", icon="polygon",
      action_name="win.create_new_shape", action_state="polygon")
m.add(path="Shapes/<New>/Regular Convex Polygon", icon="regular_convex_polygon",
      action_name="win.create_new_shape", action_state="regular_convex_polygon")
m.add(path="Shapes/<New>/Curve", icon="curve",
      action_name="win.create_new_shape", action_state="curve")
m.add(path="Shapes/<New>/Image", icon="image",
      action_name="win.create_new_shape", action_state="image")
m.add(path="Shapes/<New>/Freehand", icon="freehand_shape",
      action_name="win.create_new_shape", action_state="freehand")
m.add(path="Shapes/<New>/Ring", icon="ring_shape",
      action_name="win.create_new_shape", action_state="ring")
m.add(path="Shapes/<New>/Text", icon="text_shape",
      action_name="win.create_new_shape", action_state="text")
m.add(path="Shapes/<New>/Audio", icon="audio",
      action_name="win.create_new_shape", action_state="audio")
m.add(path="Shapes/<New>/Movie", icon="video",
      action_name="win.create_new_shape", action_state="video")
m.add(path="Shapes/<New>/Camera", icon="camera",
      action_name="win.create_new_shape", action_state="camera")
m.add(path="Shapes/<New>/3D", icon="3d",
      action_name="win.create_new_shape", action_state="threed")
m.add(path="Shapes/<New>/Document", icon="new_document_shape",
      action_name="win.create_new_shape", action_state="document")
m.add(path="Shapes/<New>/Custom", icon="custom_shape",
      action_name="win.create_new_shape", action_state="custom")
m.add(path="Shapes/<New>/Curve Joiner", icon="curve_joiner",
      action_name="win.create_new_shape", action_state="curve_joiner")
m.add(path="Shapes/<New>/Mimic", icon="mimic",
      action_name="win.create_new_shape", action_state="mimic")
m.add(path="Shapes/<New>/Image Sequence", icon="image_seq", icon_scale=.8,
      action_name="win.create_new_shape", action_state="image_seq")

m.add(path="Shapes/Align/X", icon="x_align", desc="Align shapes along X-axis",
      action_name="win.align_shapes", action_param="x", icon_scale = 1.2)
m.add(path="Shapes/Align/Y", icon="y_align", desc="Align shapes along Y-axis",
      action_name="win.align_shapes", action_param="y", icon_scale = 1.2)
m.add(path="Shapes/Align/XY", icon="xy_align", desc="Align shapes along X-axis & Y-axis",
      action_name="win.align_shapes", action_param="xy", icon_scale = 2)
m.add(path="Shapes/Align/Center", icon="center_align", desc="Align shape to the center",
      action_name="win.align_shapes", action_param="center", icon_scale = 2)

m.add(path="Shapes/Group/Create", icon="create_shape_group", icon_scale=1.5,
      action_name="win.create_shape_group", desc="Combined shapes into group")
m.add(path="Shapes/Group/Break", icon="break_shape_group", icon_scale=1.5,
      action_name="win.break_shape_group", desc="Break shape group")
m.add(path="Shapes/Group/Merge", icon="merge_shapes", icon_scale=1.5,
      action_name="win.merge_shapes", desc="Merge shapes")

m.add(path="Shapes/Point Group/Create Point Group", icon="create_point_group", desc="Group points together",
      action_name="win.create_point_group")
m.add(path="Shapes/Point Group/Break Point Group", icon="break_point_group", desc="Break points together",
      action_name="win.break_point_group")
m.add(path="Shapes/Point Group/Lock Point Group", icon="lock_point_group", accel="<Control>p",
      action_name="win.lock_point_group", action_state=False, icon_scale=1.2)
m.add(path="Shapes/Point Group/Add Point to Point Group", icon="add_to_point_group",
      action_name="win.add_point_to_point_group", icon_scale=1.2)
m.add(path="Shapes/Point Group/Remove Point from Point Group", icon="remove_from_point_group",
      action_name="win.remove_point_from_point_group", icon_scale=1.2)
m.add(path="Shapes/Point Group/Rebuild", icon="rebuild_point_group",
      action_name="win.rebuild_point_group", icon_scale=1.2)
m.add(path="Shapes/Point Group/Break Into Singles", icon="break_into_singles",
      action_name="win.break_points_into_point_shapes", icon_scale=1.2)

m.add(path="Shapes/Convert To/Polygon", icon="convert_to_polygon", desc="Convert into Polygon",
      action_name="win.convert_shape_to", action_param="polygon", icon_scale=1.2)
m.add(path="Shapes/Convert To/Curve", icon="convert_to_curve", desc="Convert into Curve",
      action_name="win.convert_shape_to", action_param="curve", icon_scale=1.2)

m.add(path="Edit/Preferences/Hide Axis", icon="hide_axis",
      action_name="win.hide_axis", action_state=True, icon_scale=2.)
m.add(path="Edit/Preferences/Lock Movement/Shape", icon="lock_movement", desc="Lock Shape movement",
      action_name="win.lock_shape_movement", action_state=False, icon_scale = 1.5)
m.add(path="Edit/Preferences/Lock Movement/X", icon="x_only_movement", desc="Move along X-axis only",
      action_name="win.lock_xy_movement", action_state="x", accel="<Control>w")
m.add(path="Edit/Preferences/Lock Movement/Y", icon="y_only_movement", desc="Move along Y-axis only",
      action_name="win.lock_xy_movement", action_state="y", accel="<Control>e")
m.add(path="Edit/Preferences/Lock Guides", icon="lock_guides",
      action_name="win.lock_guides", action_state=False)
m.add(path="Edit/Preferences/Hide Guides", icon="hide_guides",
      action_name="win.hide_guides", action_state=False)
m.add(path="Edit/Preferences/Hide Control Points", icon="hide_control_points",
      action_name="win.hide_control_points", action_state=False, icon_scale=2.)
m.add(path="Edit/Preferences/Show All Time Lines", icon="show_all_time_lines",
      action_name="win.show_all_time_lines", action_state=True, icon_scale=1.2)
m.add(path="Edit/Preferences/Show Point Groups", icon="show_point_groups",
      action_name="win.show_point_groups", action_state=True, icon_scale=1.2)
m.add(path="Edit/Preferences/Lock Shape Selection", icon="lock_selection",
      action_name="win.lock_shape_selection", action_state=False, icon_scale=1.2)
m.add(path="Edit/Preferences/Hide Background Shapes", icon="hide_background_shapes",
      action_name="win.hide_background_shapes", action_state=False, icon_scale=1.2)

m.add(path="Edit/Preferences/Panel Layout/Drawing", icon="panel_drawing",
      desc = "Drawing Panel Layout",
      action_name="win.change_panel_layout", action_param="272/1017/614", icon_scale=3)
m.add(path="Edit/Preferences/Panel Layout/Animation", icon="panel_animation",
      desc = "Animation Panel Layout",
      action_name="win.change_panel_layout", action_param="294/679/444", icon_scale=3)
m.add(path="Windows/Camera Viewer", icon="camera_viewer", desc = "Camera Viewer",
      action_name="win.toggle_camera_viewer", action_state=False)

m.tool_rows = [
    ["File/<Open>", "File/New", "Edit/Shape", "View", "Edit/Preferences/Lock Movement",
     "Edit/Preferences", "Edit/Shape/<Linked>",
     "Edit/Preferences/Panel Layout"],
    ["Shapes/Group", "Shapes/Point Group", "Edit/<Layer>", "Edit/Shape/Flip",
     "Shapes/Align", "Shapes/Convert To", "Edit/Points"],
    ["Shapes/<New>", "Shapes/Pre-Drawn", "Edit/TimeLine", "Edit/Document", "Windows"]
]

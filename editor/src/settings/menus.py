from ..gui_utils.menu_builder import *

TopMenuItem = m = TopMenu("menubar")
m.add(path="File/New/Icon", icon="file_new_icon", desc="Create New Icon",
      action_name="app.create_new_document", action_param="400x400")
m.add(path="File/New/Document", icon="file_new_document", desc="Create New Document",
      action_name="app.create_new_document", action_param="400x300")

m.add(path="File/<Open>/Open", icon="file_open", desc="Open file",
      action_name="app.open_document", action_param="", accel="<Control>o")
m.add(path="File/<Open>/Open Recent")
m.add(path="File/<Open>/Save", accel="<Control>s", icon="file_save", desc="Save file",
      action_name="win.save_document")
m.add(path="File/<Open>/Save As", accel="<Shift><Control>s", icon="file_save_as",
      action_name="win.save_as_document", desc="Save file as")

m.add(path="Edit/<UndoRedo>/Undo", accel="<Control>z",
      action_name="win.undo_redo", action_param="undo")
m.add(path="Edit/<UndoRedo>/Redo", accel="<Control>Y",
      action_name="win.undo_redo", action_param="redo")
m.add(path="Edit/Shape/Copy", icon="copy_shape", accel="<Control>c",
      action_name="win.copy_shape_action")
m.add(path="Edit/Shape/Paste", icon="paste_shape", accel="<Control>v",
      action_name="win.paste_shape_action")
m.add(path="Edit/Shape/Delete", icon="delete_shape",
      action_name="win.delete_shape")
m.add(path="Edit/Shape/Duplicate", icon="duplicate_shape", accel="<Control>b",
      action_name="win.duplicate_shape")
m.add(path="Edit/Shape/Flip/Flip X", icon="flip_x",
      action_name="win.flip_shape", action_param="x")
m.add(path="Edit/Shape/Flip/Flip Y", icon="flip_y",
      action_name="win.flip_shape", action_param="y")
m.add(path="Edit/<Layer>/Layer Up", icon="layer_up", desc="Move shape layer up",
      action_name="win.change_shape_depth", action_param="1", icon_scale=2.)
m.add(path="Edit/<Layer>/Layer Down", icon="layer_down", desc="Move shape layer down",
      action_name="win.change_shape_depth", action_param="-1", icon_scale=2.)

m.add(path="Edit/TimeLine/Delete Slice", icon="delete_time_slice",
      action_name="win.delete_time_slice", desc="Delete Time Slice")

m.add(path="Edit/Points/Join", icon="join_points", desc="Join points together",
      action_name="win.join_points_of_shape")
m.add(path="Edit/Points/Break", icon="break_point", desc="Break point into two points",
      action_name="win.insert_break_in_shape", icon_scale = 1.5)
m.add(path="Edit/Points/Delete", icon="delete_point", desc="Delete point",
      action_name="win.delete_point_of_shape", icon_scale = 1.5)
m.add(path="Edit/Points/Extend", icon="extend_point", desc="Extend point into new point",
      action_name="win.extend_point_of_shape")

m.add(path="Shapes/<New>/Rectangle", icon="rectangle",
      action_name="win.create_new_shape", action_state="rect")
m.add(path="Shapes/<New>/Oval", icon="oval",
      action_name="win.create_new_shape", action_state="oval")
m.add(path="Shapes/<New>/Polygon", icon="polygon",
      action_name="win.create_new_shape", action_state="polygon")
m.add(path="Shapes/<New>/Curve", icon="curve",
      action_name="win.create_new_shape", action_state="curve")
m.add(path="Shapes/<New>/Image", icon="image",
      action_name="win.create_new_shape", action_state="image")
m.add(path="Shapes/<New>/Freehand", icon="freehand_shape",
      action_name="win.create_new_shape", action_state="freehand")


m.add(path="Shapes/Align/X", icon="x_align", desc="Align shapes along X-axis",
      action_name="win.align_shapes", action_param="x", icon_scale = 1.2)
m.add(path="Shapes/Align/Y", icon="y_align", desc="Align shapes along Y-axis",
      action_name="win.align_shapes", action_param="y", icon_scale = 1.2)
m.add(path="Shapes/Align/XY", icon="xy_align", desc="Align shapes along X-axis & Y-axis",
      action_name="win.align_shapes", action_param="xy", icon_scale = 2)

m.add(path="Shapes/Group/Create", icon="create_shape_group", icon_scale=1.5,
      action_name="win.create_shape_group", desc="Combined shapes into group")
m.add(path="Shapes/Group/Break", icon="break_shape_group", icon_scale=1.5,
      action_name="win.break_shape_group", desc="Break shape group")
m.add(path="Shapes/Group/Merge", icon="merge_shapes", icon_scale=1.5,
      action_name="win.merge_shapes", desc="Merge shapes")

m.add(path="Shapes/Convert To/Polygon", icon="convert_to_polygon", desc="Convert into Polygon",
      action_name="win.convert_shape_to", action_param="polygon", icon_scale=1.2)
m.add(path="Shapes/Convert To/Curve", icon="convert_to_curve", desc="Convert into Curve",
      action_name="win.convert_shape_to", action_param="curve", icon_scale=1.2)

m.add(path="Edit/Preferences/Lock Movement/Shape", icon="lock_movement", desc="Lock Shape movement",
      action_name="win.lock_shape_movement", action_state=False, icon_scale = 1.5)
m.add(path="Edit/Preferences/Lock Movement/X", icon="x_only_movement", desc="Move along X-axis only",
      action_name="win.lock_xy_movement", action_state="x", accel="<Control>w")
m.add(path="Edit/Preferences/Lock Movement/Y", icon="y_only_movement", desc="Move along Y-axis only",
      action_name="win.lock_xy_movement", action_state="y", accel="<Control>e")
m.add(path="Edit/Preferences/Lock Guides", icon="lock_guides",
      action_name="win.lock_guides", action_state=False)
m.add(path="Edit/Preferences/Hide Control Points", icon="hide_control_points",
      action_name="win.hide_control_points", action_state=False, icon_scale=2.)

m.tool_rows = [
    ["File/<Open>", "File/New", "Edit/Shape", "Edit/Preferences/Lock Movement",
     "Edit/TimeLine", "Edit/Preferences"],
    ["Shapes/Group", "Edit/<Layer>", "Edit/Shape/Flip", "Shapes/<New>", "Edit/Points",
     "Shapes/Align", "Shapes/Convert To", "Shapes/Pre-Drawn"],
]

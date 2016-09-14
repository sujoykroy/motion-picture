from ..gui_utils.menu_builder import *

TopMenuItem = m = TopMenu("menubar")
m.add(path="File/New/Icon",
      action_name="app.create_new_document", action_param="400x400")
m.add(path="File/New/Document",
      action_name="app.create_new_document", action_param="400x300")

m.add(path="File/<Open>/Open",
      action_name="app.open_document", action_param="")
m.add(path="File/<Open>/Open Recent")
m.add(path="File/<Open>/Save", accel="<Control>s",
      action_name="win.save_document")
m.add(path="File/<Open>/Save As", accel="<Shift><Control>s",
      action_name="win.save_as_document")

m.add(path="Edit/<UndoRedo>/Undo", accel="<Control>z",
      action_name="win.undo_redo", action_param="undo")
m.add(path="Edit/<UndoRedo>/Redo", accel="<Control>Y",
      action_name="win.undo_redo", action_param="redo")
m.add(path="Edit/Shape/Duplicate",
      action_name="win.duplicate_shape")
m.add(path="Edit/Shape/Delete",
      action_name="win.delete_shape")
m.add(path="Edit/Shape/Flip/Flip X", icon="flip_x",
      action_name="win.flip_shape", action_param="x")
m.add(path="Edit/Shape/Flip/Flip Y", icon="flip_y",
      action_name="win.flip_shape", action_param="y")
m.add(path="Edit/<Layer>/Layer Up",
      action_name="win.change_shape_depth", action_param="1")
m.add(path="Edit/<Layer>/Layer Down",
      action_name="win.change_shape_depth", action_param="-1")

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
m.add(path="Shapes/<New>/Curve", icon="curve",
      action_name="win.create_new_shape", action_state="curve")
m.add(path="Shapes/<New>/Polygon", icon="polygon",
      action_name="win.create_new_shape", action_state="polygon")
m.add(path="Shapes/<New>/Image", icon="image",
      action_name="win.create_new_shape", action_state="image")
#m.add(path="Shapes/<New>/Freehand", icon="image",
#      action_name="win.create_new_shape", action_state="freehand")


m.add(path="Shapes/Align/X",
      action_name="win.align_shapes", action_param="x")
m.add(path="Shapes/Align/Y",
      action_name="win.align_shapes", action_param="y")
m.add(path="Shapes/Align/XY",
      action_name="win.align_shapes", action_param="xy")

m.add(path="Shapes/Group/Create",
      action_name="win.create_shape_group")
m.add(path="Shapes/Group/Break",
      action_name="win.break_shape_group")
m.add(path="Shapes/Group/Merge",
      action_name="win.merge_shapes")

m.add(path="Shapes/Convert To/Polygon",
      action_name="win.convert_shape_to", action_param="polygon")
m.add(path="Shapes/Convert To/Curve",
      action_name="win.convert_shape_to", action_param="curve")

m.add(path="Edit/Preferences/Lock Movement/Shape", icon="lock_movement",
      action_name="win.lock_shape_movement", action_state=False, icon_scale = 1.5)
m.add(path="Edit/Preferences/Lock Movement/X", icon="x_only_movement",
      action_name="win.lock_xy_movement", action_state="x")
m.add(path="Edit/Preferences/Lock Movement/Y", icon="y_only_movement",
      action_name="win.lock_xy_movement", action_state="y")
m.add(path="Edit/Preferences/Lock Guides",
      action_name="win.lock_guides", action_state=False)
m.add(path="Edit/Preferences/Hide Control Points",
      action_name="win.hide_control_points", action_state=False)

m.tool_rows = [
    ["File/<Open>", "File/New", "Edit/Shape"],
    ["Shapes/Align", "Shapes/Group", "Shapes/Convert To"],
    ["Edit/Preferences/Lock Movement", "Edit/Shape/Flip", "Shapes/<New>", "Edit/Points"],
    ["Edit/<Layer>", "Shapes/Pre-Drawn", "Edit/Preferences"]
]

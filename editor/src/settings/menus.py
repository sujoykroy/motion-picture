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

m.add(path="Edit/Points/Join",
      action_name="win.join_points_of_shape")
m.add(path="Edit/Points/Break",
      action_name="win.insert_break_in_shape")
m.add(path="Edit/Points/Delete",
      action_name="win.delete_point_of_shape")
m.add(path="Edit/Points/Extend",
      action_name="win.extend_point_of_shape")

m.add(path="Shapes/<New>/Rectangle", icon="rectangle",
      action_name="win.create_new_shape", action_param="rect")
m.add(path="Shapes/<New>/Oval", icon="oval",
      action_name="win.create_new_shape", action_param="oval")
m.add(path="Shapes/<New>/Curve", icon="curve",
      action_name="win.create_new_shape", action_param="curve")
m.add(path="Shapes/<New>/Polygon", icon="polygon",
      action_name="win.create_new_shape", action_param="polygon")
m.add(path="Shapes/<New>/Image", icon="image",
      action_name="win.create_new_shape", action_param="image")

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

m.add(path="Shapes/Convert To/Polygon",
      action_name="win.convert_shape_to", action_param="polygon")
m.add(path="Shapes/Convert To/Curve",
      action_name="win.convert_shape_to", action_param="curve")

m.tool_rows = [
    ["File/<Open>", "File/New", "Edit/Shape", "Edit/Points"],
    ["Shapes/<New>", "Shapes/Align", "Shapes/Group", "Shapes/Convert To"]
]

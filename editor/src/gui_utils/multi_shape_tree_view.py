from gi.repository import Gtk
from ..shapes import Shape, MultiShape
from gi.repository.GdkPixbuf import Pixbuf

class MultiShapeTreeView(Gtk.TreeView):
    def __init__(self, on_shape_selected_callback, redraw_callback):
        Gtk.TreeView.__init__(self)
        self.on_shape_selected_callback = on_shape_selected_callback
        self.redraw_callback = redraw_callback
        self.append_column(Gtk.TreeViewColumn("Icon", Gtk.CellRendererPixbuf(), pixbuf=0))
        self.append_column(Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1))
        visible_renderer = Gtk.CellRendererToggle()
        visible_renderer.props.activatable = True
        visible_renderer.connect("toggled", self.visible_renderer_toggled)
        self.append_column(Gtk.TreeViewColumn("Visible", visible_renderer, active=2))

        self.get_selection().connect("changed", self.on_shape_selected)

        self.props.enable_tree_lines = True
        self.connect("row-activated", self.on_row_activated)

    def set_multi_shape(self, multi_shape):
        self.multi_shape = multi_shape
        self.rebuild()

    def rebuild(self):
        self.tree_model = Gtk.TreeStore(Pixbuf, str, bool, object)
        self.append_child_items(self.tree_model, self.multi_shape, None, depth=0)
        self.set_model(self.tree_model)

    def append_child_items(self, tree_model, parent_shape, parent_iter, depth):
        for shape in parent_shape.shapes:
            current_iter = tree_model.append(parent_iter,
                [shape.get_pixbuf(32,32), shape.get_name(), shape.visible, shape])
            if depth <   0 and isinstance(shape, MultiShape):
                self.append_child_items(tree_model, shape, current_iter, depth+1)


    def on_shape_selected(self, tree_selection):
        model, treeiter = tree_selection.get_selected()
        if treeiter:
            shape = self.tree_model.get_value(treeiter, 3)
            self.on_shape_selected_callback(shape)

    def visible_renderer_toggled(self, cell_renderer_toggle, path):
        treeiter = self.tree_model.get_iter(path)
        shape = self.tree_model.get_value(treeiter, 3)
        shape.visible = not self.tree_model.get_value(treeiter, 2)
        self.tree_model.set_value(treeiter, 2, shape.visible)
        self.redraw_callback()

    def on_row_activated(self, tree_view, path, column):
        treeiter = self.tree_model.get_iter(path)
        if not treeiter:
            return
        shape = self.tree_model.get_value(treeiter, 3)
        self.on_shape_selected_callback(shape, double_clicked=True)

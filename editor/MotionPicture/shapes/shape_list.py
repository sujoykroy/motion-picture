class ShapeList(object):
    def __init__(self, shape_list=None, unique=True):
        self.names = []
        self.items = []
        self.unique = unique
        if shape_list is not None:
            self.names.extend(shape_list.names)
            self.items.extend(shape_list.items)

    def clear(self, destroy_items):
        if destroy_items:
            for item in self.items:
                item.cleanup()
        del self.names[:]
        del self.items[:]

    def order_like(self, names):
        new_items = []
        new_names = []
        for name in names:
            if name not in self.names:
                continue
            index = self.names.index(name)
            new_items.append(self.items[index])
            new_names.append(name)
        del self.names[:]
        del self.items[:]
        self.names.extend(new_names)
        self.items.extend(new_items)

    def replace_or_add(self, old_shape, new_shape):
        if not self.contain(old_shape):
            self.add(new_shape)
            return
        if isinstance(old_shape, str):
            index = self.names.index(old_shape)
            old_shape = self.items[index]
        else:
            index = self.items.index(old_shape)
        self.items[index] = new_shape
        self.names[index] = new_shape.get_name()
        old_shape.transfer_network_to(new_shape)

    def add(self, shape):
        shape_name = shape.get_name()
        if not self.unique or (shape_name not in self.names):
            self.items.append(shape)
            self.names.append(shape_name)
        else:
            exception_text = "Attempt to append duplicate shape[{0}] in list.".format(shape._name)
            print(exception_text)
            #raise Exception(exception_text)

    def remove(self, shape):
        if type(shape) is str:
            index = self.names.index(shape)
        else:
            index = self.items.index(shape)
        del self.items[index]
        del self.names[index]

    def rename(self, old_name, new_name):
        shape = self.get_item_by_name(old_name)
        if new_name not in self.names:
            index = self.names.index(old_name)
            self.names[index] = new_name
            shape._name = new_name
            return True
        elif  shape.get_name() == new_name:
            return True
        return False

    def __iter__(self):
        #wrapping up self.items in list will prevent issue in shape deletion
        #within this iteration
        for shape in list(self.items):
            yield shape

    def __len__(self):
        return len(self.items)

    def reversed_list(self):
        for shape in reversed(self.items):
            yield shape

    def __getitem__(self, key):
        return self.items[self.names.index(key)]

    def get_at_index(self, index):
        return self.items[index]

    def contain(self, shape):
        if isinstance(shape, str):
            return (shape in self.names)
        return (shape in self.items)

    def get_item_by_name(self, name):
        if name not in self.names: return None
        return self.items[self.names.index(name)]

    def insert_at(self, index, shape):
        self.remove(shape)
        self.names.insert(index, shape.get_name())
        self.items.insert(index, shape)

    def change_index(self, name, index_offset):
        index = self.names.index(name)
        if index+index_offset<0 or index+index_offset>=len(self.names): return False
        self.names[index], self.names[index+index_offset] = \
                    self.names[index+index_offset], self.names[index]
        self.items[index], self.items[index+index_offset] = \
                    self.items[index+index_offset], self.items[index]
        return True

    def key_exists(self, key):
        return key in self.names

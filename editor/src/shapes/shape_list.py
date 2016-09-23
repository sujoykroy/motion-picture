from shape import Shape

class ShapeList(object):
    def __init__(self, shape_list=None):
        self.names = []
        self.items = dict()
        if shape_list is not None:
            self.names.extend(shape_list.names)
            for key,value in shape_list.items.items():
                self.items[key] = value

    def clear(self):
        del self.names[:]
        self.items.clear()

    def add(self, shape):
        if shape._name not in self.names:
            self.items[shape._name] = shape
            self.names.append(shape._name)
        else:
            raise Exception("Attempt to append duplicate shape[{0}] in list.".format(shape._name))

    def remove(self, shape):
        if type(shape) is str:
            del self.items[shape]
            self.names.remove(shape)
            return
        for key in self.items.keys():
            if self.items[key] == shape:
                del self.items[key]
                self.names.remove(key)
                break

    def rename(self, old_name, new_name):
        if new_name not in self.names:
            self.names[self.names.index(old_name)] = new_name
            shape = self.items[old_name]
            del self.items[old_name]
            self.items[new_name] = shape
            shape._name = new_name
            return True
        elif  self.items[new_name] == shape:
            return True
        return False

    def __iter__(self):
        for shape_name in self.names:
            yield self.items[shape_name]

    def __len__(self):
        return len(self.names)

    def reversed_list(self):
        for shape_name in reversed(self.names):
            yield self.items[shape_name]

    def __getitem__(self, key):
        return self.items[key]

    def get_at_index(self, index):
        return self.items[self.names[index]]

    def contain(self, shape):
        if (isinstance(shape, Shape)):
            return (shape.get_name() in self.names)
        return (shape in self.names)

    def get_item_by_name(self, name):
        if name not in self.names: return None
        return self.items[name]

    def change_index(self, name, index_offset):
        index = self.names.index(name)
        if index+index_offset<0 or index+index_offset>=len(self.names): return False
        self.names[index], self.names[index+index_offset] = \
                    self.names[index+index_offset], self.names[index]
        return True

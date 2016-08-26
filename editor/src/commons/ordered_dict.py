class OrderedDict(object):
    def __init__(self):
        self.items = dict()
        self.keys = []

    def add(self, key, item):
        if key not in self.keys:
            self.keys.append(key)
        self.items[key] = item

    def clear(self):
        del self.keys[:]
        self.items.clear()

    def insert_after(self, after_key, key, item):
        if after_key not in self.keys:
            self.add(key, item)
        else:
            index = self.keys.index(after_key)
            self.keys.insert(index+1, key)
            self.items[key] = item

    def remove(self, key):
        if key in self.keys():
            self.keys.remove(key)
        if key in self.items.keys():
            del self.items[key]

    def __len__(self):
        return len(self.keys)

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        for key in self.keys:
            yield self.items[key]

    def key_exists(self, key):
        return key in self.keys

    def get_item_at_index(self, index):
        if index>=len(self.keys) or index<0: return None
        return self.items[self.keys[index]]

    def get_last_item(self):
        return self.items[self.keys[-1]]

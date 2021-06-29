class ValueParser:
    @staticmethod
    def parse_int(value, default=None):
        if value is None:
            return default
        try:
            value = int(value)
        except ValueError:
            value = default
        return value

    @staticmethod
    def parse_float(value, default=None):
        if value is None:
            return default
        try:
            value = float(value)
        except ValueError:
            value = default
        return value

    @classmethod
    def find_in_paths(cls, ob, paths, default=None):
        for path_i, path in enumerate(paths):
            found = False
            if isinstance(ob, list):
                if path is list:
                    for sub_ob in ob:
                        found_ob = cls.find_in_paths(sub_ob, paths[path_i+1:], None)
                        if found_ob is not None:
                            ob = found_ob
                            found = True
                            break
                    if found:
                        break
                elif isinstance(path, int) and path < len(ob):
                    ob = ob[path]
                    found = True
                elif isinstance(path, str) and path == cls.FUNCTION_LENGTH:
                    ob = len(ob)
                    found = True
            elif isinstance(ob, dict):
                if isinstance(path, str) and path in ob:
                    ob = ob[path]
                    found = True
                elif hasattr(path, 'search'):
                    for key in ob.keys():
                        if not path.search(key):
                            break
                        ob = ob[key]
                        found = True
                        break
                elif hasattr(path, 'check') and path.check(ob):
                    ob = path.get_value(ob)
                    found = True
            elif isinstance(path, str) and hasattr(ob, path):
                ob = getattr(ob, path)
                if callable(ob):
                    ob = ob()
                found = True
            if not found:
                return default
        return ob

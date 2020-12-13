class Map(dict):
    def __init__(self, data: dict):
        super(Map, self).__init__(data)
        self.__parse(data)

    def __parse(self, value):
        for key, value in value.items():
            if isinstance(value, list):
                self[key] = self.__parse_list(value)
            elif isinstance(value, dict):
                self[key] = Map(value)
            else:
                self[key] = value

    @staticmethod
    def __parse_list(value: list) -> list:
        result = []

        for i in range(len(value)):
            if isinstance(value[i], dict):
                result.append(Map(value[i]))
            else:
                result.append(value[i])

        return result

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

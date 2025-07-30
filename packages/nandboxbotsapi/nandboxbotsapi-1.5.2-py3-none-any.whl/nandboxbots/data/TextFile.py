import json


class TextFile:
    __KEY_SIZE = "size"
    __KEY_ID = "id"

    size = None
    id = None

    def __init__(self, dictionary):
        self.size = int(dictionary[self.__KEY_SIZE]) if self.__KEY_SIZE in dictionary.keys() else None
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.size is not None:
            dictionary[self.__KEY_SIZE] = self.size
        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id

        return json.dumps(dictionary), dictionary

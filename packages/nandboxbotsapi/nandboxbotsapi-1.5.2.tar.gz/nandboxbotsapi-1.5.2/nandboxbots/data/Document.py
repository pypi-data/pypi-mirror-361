import json


class Document:
    __KEY_ID = "id"
    __KEY_NAME = "name"
    __KEY_SIZE = "size"

    id = None
    name = None
    size = None

    def __init__(self, dictionary):
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.name = str(dictionary[self.__KEY_NAME]) if self.__KEY_NAME in dictionary.keys() else None
        self.size = int(dictionary[self.__KEY_SIZE]) if self.__KEY_SIZE in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.size is not None:
            dictionary[self.__KEY_SIZE] = self.size

        return json.dumps(dictionary), dictionary

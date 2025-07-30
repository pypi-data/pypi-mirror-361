import json


class Data:
    __KEY_PATTERN = "pattern"
    __KEY_EXAMPLE = "example"
    __KEY_ID = "id"


    pattern = None
    example = None
    id = None
    def __init__(self, dictionary=None):
        if dictionary is None or dictionary == {}:
            return
        self.pattern = str(dictionary[self.__KEY_PATTERN]) if self.__KEY_PATTERN in dictionary.keys() else None
        self.example = str(dictionary[self.__KEY_EXAMPLE]) if self.__KEY_EXAMPLE in dictionary.keys() else None
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None

    def to_dict(self):
        return {
            self.__KEY_PATTERN: self.pattern,
            self.__KEY_EXAMPLE: self.example,
            self.__KEY_ID: self.id
        }

    def to_json_obj(self):

        dictionary = {}

        if self.pattern is not None:
            dictionary[self.__KEY_PATTERN] = self.pattern
        if self.example is not None:
            dictionary[self.__KEY_EXAMPLE] = self.example
        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id

        return json.dumps(dictionary), dictionary

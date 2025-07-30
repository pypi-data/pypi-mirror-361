import json


class Voice:
    __KEY_ID = "id"
    __KEY_DURATION = "duration"
    __KEY_SIZE = "size"

    id = None
    duration = None
    size = None

    def __init__(self, dictionary):
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.duration = int(dictionary[self.__KEY_DURATION]) if self.__KEY_DURATION in dictionary.keys() else None
        self.size = int(dictionary[self.__KEY_SIZE]) if self.__KEY_SIZE in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.duration is not None:
            dictionary[self.__KEY_DURATION] = self.duration
        if self.size is not None:
            dictionary[self.__KEY_SIZE] = self.size

        return json.dumps(dictionary), dictionary

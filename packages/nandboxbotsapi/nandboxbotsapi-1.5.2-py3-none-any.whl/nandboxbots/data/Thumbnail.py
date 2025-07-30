import json


class Thumbnail:
    __KEY_ID = "id"
    __KEY_WIDTH = "width"
    __KEY_HEIGHT = "height"

    id = None
    width = None
    height = None

    def __init__(self, dictionary):
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.width = int(dictionary[self.__KEY_WIDTH]) if self.__KEY_WIDTH in dictionary.keys() else None
        self.height = int(dictionary[self.__KEY_HEIGHT]) if self.__KEY_HEIGHT in dictionary.keys() else None

    def to_json_obj(self):
        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.width is not None:
            dictionary[self.__KEY_WIDTH] = self.width
        if self.height is not None:
            dictionary[self.__KEY_HEIGHT] = self.height

        return json.dumps(dictionary), dictionary

    def to_dict(self):
        return {
            self.__KEY_ID: self.id,
            self.__KEY_WIDTH: self.width,
            self.__KEY_HEIGHT: self.height
        }

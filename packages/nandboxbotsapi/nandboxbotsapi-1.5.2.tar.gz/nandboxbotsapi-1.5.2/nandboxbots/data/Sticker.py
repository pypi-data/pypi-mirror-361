import json

from nandboxbots.data.Thumbnail import Thumbnail


class Sticker:
    __KEY_ID = "id"
    __KEY_WIDTH = "width"
    __KEY_HEIGHT = "height"
    __KEY_SIZE = "size"
    __KEY_THUMBNAIL = "thumbnail"

    id = None
    width = None
    height = None
    thumbnail = None

    def __init__(self, dictionary):
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.width = int(dictionary[self.__KEY_WIDTH]) if self.__KEY_WIDTH in dictionary.keys() else None
        self.height = int(dictionary[self.__KEY_HEIGHT]) if self.__KEY_HEIGHT in dictionary.keys() else None
        self.size = int(dictionary[self.__KEY_SIZE]) if self.__KEY_SIZE in dictionary.keys() else None
        self.thumbnail = Thumbnail(dictionary.get(self.__KEY_THUMBNAIL, {}))

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.width is not None:
            dictionary[self.__KEY_WIDTH] = self.width
        if self.height is not None:
            dictionary[self.__KEY_HEIGHT] = self.height
        if self.size is not None:
            dictionary[self.__KEY_SIZE] = self.size
        if self.thumbnail is not None:
            _, thumbnail_dict = self.thumbnail.to_json_obj()
            dictionary[self.__KEY_THUMBNAIL] = thumbnail_dict

        return json.dumps(dictionary), dictionary

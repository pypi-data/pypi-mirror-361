import json


class Result:
    __KEY_ID = "id"
    __KEY_CAPTION = "caption"
    __KEY_TITLE = "title"
    __KEY_DESCRIPTION = "description"
    __KEY_URL = "url"
    __KEY_TYPE = "type"
    __KEY_THUMB_URL = "thumb_url"
    __KEY_WIDTH = "width"
    __KEY_HEIGHT = "height"

    id = None
    caption = None
    title = None
    description = None
    url = None
    type = None
    thumb_url = None
    width = None
    height = None

    def __init__(self, dictionary):
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.caption = str(dictionary[self.__KEY_CAPTION]) if self.__KEY_CAPTION in dictionary.keys() else None
        self.title = str(dictionary[self.__KEY_TITLE]) if self.__KEY_TITLE in dictionary.keys() else None
        self.description = str(dictionary[self.__KEY_DESCRIPTION]) if self.__KEY_DESCRIPTION in dictionary.keys() else None
        self.url = str(dictionary[self.__KEY_URL]) if self.__KEY_URL in dictionary.keys() else None
        self.type = str(dictionary[self.__KEY_TYPE]) if self.__KEY_TYPE in dictionary.keys() else None
        self.thumb_url = str(dictionary[self.__KEY_THUMB_URL]) if self.__KEY_THUMB_URL in dictionary.keys() else None
        self.width = int(dictionary[self.__KEY_WIDTH]) if self.__KEY_WIDTH in dictionary.keys() else None
        self.height = int(dictionary[self.__KEY_HEIGHT]) if self.__KEY_HEIGHT in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.caption is not None:
            dictionary[self.__KEY_CAPTION] = self.caption
        if self.title is not None:
            dictionary[self.__KEY_TITLE] = self.title
        if self.description is not None:
            dictionary[self.__KEY_DESCRIPTION] = self.description
        if self.url is not None:
            dictionary[self.__KEY_URL] = self.url
        if self.type is not None:
            dictionary[self.__KEY_TYPE] = self.type
        if self.thumb_url is not None:
            dictionary[self.__KEY_THUMB_URL] = self.thumb_url
        if self.width is not None:
            dictionary[self.__KEY_WIDTH] = self.width
        if self.height is not None:
            dictionary[self.__KEY_HEIGHT] = self.height

        return json.dumps(dictionary), dictionary

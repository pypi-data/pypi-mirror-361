import json


class PermanentUrl:
    __KEY_FILE = "file"
    __KEY_URL = "url"
    __KEY_PARAM1 = "param1"
    __KEY_APP_ID = "app_id"
    file = None
    url = None
    param1 = None
    app_id = None
    def __init__(self, dictionary):
        self.url = str(dictionary[self.__KEY_URL]) if self.__KEY_URL in dictionary.keys() else None
        self.file = str(dictionary[self.__KEY_FILE]) if self.__KEY_FILE in dictionary.keys() else None
        self.param1 = str(dictionary[self.__KEY_PARAM1]) if self.__KEY_PARAM1 in dictionary.keys() else None
        self.app_id = dictionary[self.__KEY_APP_ID] if self.__KEY_APP_ID in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.url is not None:
            dictionary[self.__KEY_URL] = self.url
        if self.file is not None:
            dictionary[self.__KEY_FILE] = self.file
        if self.param1 is not None:
            dictionary[self.__KEY_PARAM1] = self.param1
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id

        return json.dumps(dictionary), dictionary

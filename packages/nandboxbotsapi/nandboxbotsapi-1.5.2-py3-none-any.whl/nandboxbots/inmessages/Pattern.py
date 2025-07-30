import json
from nandboxbots.data.Data import Data

class Pattern:
    __KEY_DATA = "data"
    __KEY_CHAT_ID = "chat_id"
    __KEY_APP_ID = "app_id"
    __KEY_REFERENCE = "reference"
    app_id = None
    chat_id = None
    data=None
    def __init__(self, obj):
        self.app_id = int(obj[self.__KEY_APP_ID]) if self.__KEY_APP_ID in obj else 0
        self.reference = int(obj[self.__KEY_REFERENCE]) if self.__KEY_REFERENCE in obj else 0
        self.chat_id = int(obj[self.__KEY_CHAT_ID]) if self.__KEY_CHAT_ID in obj else 0
        self.data = []
        if self.__KEY_DATA in obj and isinstance(obj[self.__KEY_DATA], list):
            self.data = [Data(item) for item in obj[self.__KEY_DATA]]

    def to_json_obj(self):
        dictionary = {}

        if self.data:
            dictionary[self.__KEY_DATA] = [item.to_json_obj() for item in self.data]
        if self.app_id:
            dictionary[self.__KEY_APP_ID] = self.app_id
        if self.chat_id:
            dictionary[self.__KEY_CHAT_ID] = self.chat_id
        if self.reference:
            dictionary[self.__KEY_REFERENCE] = self.reference

        return json.dumps(dictionary), dictionary

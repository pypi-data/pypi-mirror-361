import json


class Contact:
    __KEY_NAME = "name"
    __KEY_PHONE_NUMBER = "phone_number"

    name = None
    phone_number = None

    def __init__(self, dictionary):
        self.name = str(dictionary[self.__KEY_NAME]) if self.__KEY_NAME in dictionary.keys() else None
        self.phone_number = str(dictionary[self.__KEY_PHONE_NUMBER]) if self.__KEY_PHONE_NUMBER in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.phone_number is not None:
            dictionary[self.__KEY_PHONE_NUMBER] = self.phone_number

        return json.dumps(dictionary), dictionary

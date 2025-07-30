import json


class WhiteListUser:
    __KEY_SIGNUP_USER = "signup_user"
    __KEY_TAGS = "tags"

    signup_user = None
    tags = []

    def __init__(self, dictionary=None):
        if dictionary is None or dictionary == {}:
            return
        self.signup_user = str(dictionary[self.__KEY_SIGNUP_USER]) if self.__KEY_SIGNUP_USER in dictionary.keys() else None
        self.tags = dictionary[self.__KEY_TAGS] if self.__KEY_TAGS in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.signup_user is not None:
            dictionary[self.__KEY_SIGNUP_USER] = self.signup_user
        if not self.tags == []:
            dictionary[self.__KEY_TAGS] = self.tags

        return json.dumps(dictionary), dictionary

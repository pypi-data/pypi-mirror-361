import json


class SignupUser:
    __KEY_ID = "id"
    __KEY_SIGNUP_USER = "signup_id"

    id = None
    signup_user = None

    def __init__(self, dictionary):
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.signup_user = str(dictionary[self.__KEY_SIGNUP_USER]) if self.__KEY_SIGNUP_USER in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.signup_user is not None:
            dictionary[self.__KEY_SIGNUP_USER] = self.signup_user

        return json.dumps(dictionary), dictionary

import json

from nandboxbots.data.Chat import Chat
from nandboxbots.data.SignupUser import SignupUser


class WhiteList:
    __KEY_WHITELIST = "whitelist"
    __KEY_EOP = "eop"
    __KEY_USERS = "signups"
    __KEY_APP_ID = "app_id"
    __KEY_REFERENCE = "reference"

    eop = None
    users = []
    app_id = None
    reference = None

    def __init__(self, whitelist_dict):

        self.eop = str(whitelist_dict[self.__KEY_EOP]) if self.__KEY_EOP in whitelist_dict.keys() else None

        users_arr_obj = whitelist_dict[self.__KEY_USERS] if self.__KEY_USERS in whitelist_dict.keys() else []
        self.users = [SignupUser({})] * len(users_arr_obj)
        self.app_id = whitelist_dict[self.__KEY_APP_ID] if self.__KEY_APP_ID in whitelist_dict.keys() else None
        self.reference = whitelist_dict[self.__KEY_REFERENCE] if self.__KEY_REFERENCE in whitelist_dict.keys() else None

        for i in range(len(users_arr_obj)):
            self.users[i] = SignupUser(users_arr_obj[i])

    def to_json_obj(self):

        dictionary = {}

        if self.users is not None:
            users_arr = []
            for i in range(len(self.users)):
                users_arr.append(self.users[i].to_json_obj())

            dictionary[self.__KEY_USERS] = users_arr


        if self.eop is not None:
            dictionary[self.__KEY_EOP] = self.eop
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference
        return json.dumps(dictionary), dictionary

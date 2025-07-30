import json

from nandboxbots.data.Chat import Chat
from nandboxbots.data.User import User


class ChatAdministrators:
    __KEY_CHAT_ADMINISTRATORS = "chatAdministrators"
    __KEY_ADMINISTRATORS = "administrators"
    __KEY_CHAT = "chat"
    __KEY_APP_ID = "app_id"

    administrators = []
    chat = None
    app_id = None

    def __init__(self, dictionary):
        self.app_id = dictionary[self.__KEY_APP_ID] if self.__KEY_APP_ID in dictionary.keys() else None

        chat_administrators_dict = dictionary[self.__KEY_CHAT_ADMINISTRATORS] if self.__KEY_CHAT_ADMINISTRATORS in dictionary.keys() else {}

        self.chat = Chat(chat_administrators_dict.get(self.__KEY_CHAT, {}))

        admin_arr_obj = chat_administrators_dict[self.__KEY_ADMINISTRATORS] if self.__KEY_ADMINISTRATORS in chat_administrators_dict.keys() else None
        if admin_arr_obj is not None:
            length = len(admin_arr_obj)
            admin = [User({})] * length
            for i in range(length):
                admin[i] = User(admin_arr_obj[i])

            self.administrators = admin

    def to_json_obj(self):

        dictionary = {}

        if self.administrators is not None:
            admins_arr = []
            for i in range(len(self.administrators)):
                admins_arr.append(self.administrators[i].to_json_obj())

            dictionary[self.__KEY_ADMINISTRATORS] = admins_arr

        if self.chat is not None:
            _, chat_dict = self.chat.to_json_obj()
            dictionary[self.__KEY_CHAT] = chat_dict
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id
        return json.dumps(dictionary), dictionary

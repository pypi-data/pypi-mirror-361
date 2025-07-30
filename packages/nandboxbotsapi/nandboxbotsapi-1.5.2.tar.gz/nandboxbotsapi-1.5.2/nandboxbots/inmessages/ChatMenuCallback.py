import json

from nandboxbots.data.ButtonQueryResult import ButtonQueryResult
from nandboxbots.data.Chat import Chat
from nandboxbots.data.User import User


class ChatMenuCallback:
    __KEY_CHAT_MENU_CALL_BACK = "chatMenuCallback"
    __KEY_DATE = "date"
    __KEY_NEXT_MENU = "next_menu"
    __KEY_METHOD = "method"
    __KEY_BUTTON_CALLBACK = "button_callback"
    __KEY_BUTTON_QUERY_RESULTS = "button_query_result"
    __KEY_CHAT = "chat"
    __KEY_FROM = "from"
    __KEY_MENU_REF = "menu_ref"
    __KEY_APP_ID = "app_id"


    date = None
    next_menu = None
    method = None
    button_callback = None
    button_query_result = None
    chat = None
    from_ = None
    menu_ref = None
    appId = None
    app_id = None

    def __init__(self, dictionary):
        self.app_id = dictionary[self.__KEY_APP_ID] if self.__KEY_APP_ID in dictionary.keys() else None
        chat_menu_callback_dict = dictionary[self.__KEY_CHAT_MENU_CALL_BACK] if self.__KEY_CHAT_MENU_CALL_BACK in dictionary.keys() else {}

        from_user = User(chat_menu_callback_dict.get(self.__KEY_FROM, {}))

        self.chat = Chat(chat_menu_callback_dict.get(self.__KEY_CHAT, {}))

        btn_query_result = ButtonQueryResult(chat_menu_callback_dict.get(self.__KEY_BUTTON_QUERY_RESULTS, {}))

        self.method = str(chat_menu_callback_dict[self.__KEY_METHOD]) if self.__KEY_METHOD in chat_menu_callback_dict.keys() else None
        self.menu_ref = str(chat_menu_callback_dict[self.__KEY_MENU_REF]) if self.__KEY_MENU_REF in chat_menu_callback_dict.keys() else None
        self.appId = str(chat_menu_callback_dict[self.__KEY_APP_ID]) if self.__KEY_APP_ID in chat_menu_callback_dict.keys() else None
        self.from_ = from_user
        self.button_query_result = btn_query_result
        self.button_callback = str(chat_menu_callback_dict[self.__KEY_BUTTON_CALLBACK]) if self.__KEY_BUTTON_CALLBACK in chat_menu_callback_dict.keys() else None
        self.next_menu = str(chat_menu_callback_dict[self.__KEY_NEXT_MENU]) if self.__KEY_NEXT_MENU in chat_menu_callback_dict.keys() else None
        self.date = int(chat_menu_callback_dict[self.__KEY_DATE]) if self.__KEY_DATE in chat_menu_callback_dict.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.date is not None:
            dictionary[self.__KEY_DATE] = self.date
        if self.from_ is not None:
            _, from_user_dict = self.from_.to_json_obj()
            dictionary[self.__KEY_FROM] = from_user_dict
        if self.chat is not None:
            _, chat_dict = self.chat.to_json_obj()
            dictionary[self.__KEY_CHAT] = chat_dict
        if self.method is not None:
            dictionary[self.__KEY_METHOD] = self.method
        if self.menu_ref is not None:
            dictionary[self.__KEY_MENU_REF] = self.menu_ref
        if self.appId is not None:
            dictionary[self.__KEY_APP_ID] = self.appId
        if self.button_callback is not None:
            dictionary[self.__KEY_BUTTON_CALLBACK] = self.button_callback
        if self.button_query_result is not None:
            _, btn_query_result_dict = self.button_query_result.to_json_obj()
            dictionary[self.__KEY_BUTTON_QUERY_RESULTS] = btn_query_result_dict
        if self.next_menu is not None:
            dictionary[self.__KEY_NEXT_MENU] = self.next_menu
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id
        return json.dumps(dictionary), dictionary

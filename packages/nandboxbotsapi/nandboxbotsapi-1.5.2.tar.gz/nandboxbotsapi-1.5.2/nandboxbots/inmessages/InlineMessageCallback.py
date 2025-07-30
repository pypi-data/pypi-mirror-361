import json

from nandboxbots.data.ButtonQueryResult import ButtonQueryResult
from nandboxbots.data.Chat import Chat
from nandboxbots.data.User import User


class InlineMessageCallback:
    __KEY_INLINE_MESSAGE_CALLBACK = "inlineMessageCallback"
    __KEY_MESSAGE_ID = "message_id"
    __KEY_MENU_REF = "menu_ref"
    __KEY_DATE = "date"
    __KEY_FROM = "from"
    __KEY_CHAT = "chat"
    __KEY_REFERENCE = "reference"
    __KEY_BUTTON_CALLBACK = "button_callback"
    __KEY_BUTTON_QUERY_RESULTS = "button_query_result"
    __KEY_APP_ID = "app_id"

    message_id = None
    menu_ref = None
    date = None
    reference = None
    from_ = None
    chat = None
    button_callback = None
    button_query_result = None
    app_id = None

    def __init__(self, dictionary):
        inline_message_dict = dictionary[self.__KEY_INLINE_MESSAGE_CALLBACK] if self.__KEY_INLINE_MESSAGE_CALLBACK in dictionary.keys() else {}

        from_user = User(inline_message_dict.get(self.__KEY_FROM, {}))

        self.chat = Chat(inline_message_dict.get(self.__KEY_CHAT, {}))

        btn_query_result = ButtonQueryResult(inline_message_dict.get(self.__KEY_BUTTON_QUERY_RESULTS, {}))
        self.message_id = str(inline_message_dict[self.__KEY_MESSAGE_ID]) if self.__KEY_MESSAGE_ID in inline_message_dict.keys() else None
        self.menu_ref = str(inline_message_dict[self.__KEY_MENU_REF]) if self.__KEY_MENU_REF in inline_message_dict.keys() else None
        self.reference = str(inline_message_dict[self.__KEY_REFERENCE]) if self.__KEY_REFERENCE in inline_message_dict.keys() else None
        self.from_ = from_user
        self.button_query_result = btn_query_result
        self.button_callback = str(inline_message_dict[self.__KEY_BUTTON_CALLBACK]) if self.__KEY_BUTTON_CALLBACK in inline_message_dict.keys() else None
        self.date = int(inline_message_dict[self.__KEY_DATE]) if self.__KEY_DATE in inline_message_dict.keys() else None
        self.app_id = dictionary[self.__KEY_APP_ID] if self.__KEY_APP_ID in dictionary.keys() else None

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
        if self.message_id is not None:
            dictionary[self.__KEY_MESSAGE_ID] = self.message_id
        if self.menu_ref is not None:
            dictionary[self.__KEY_MENU_REF] = self.menu_ref
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference
        if self.button_callback is not None:
            dictionary[self.__KEY_BUTTON_CALLBACK] = self.button_callback
        if self.button_query_result is not None:
            _, btn_query_result_dict = self.button_query_result.to_json_obj()
            dictionary[self.__KEY_BUTTON_QUERY_RESULTS] = btn_query_result_dict
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id
        return json.dumps(dictionary), dictionary


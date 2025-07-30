import json

from nandboxbots.data.Chat import Chat
from nandboxbots.data.User import User


class InlineSearch:
    __KEY_INLINE_SEARCH = "inlineSearch"
    __KEY_DATE = "date"
    __KEY_METHOD = "method"
    __KEY_CHAT = "chat"
    __KEY_FROM = "from"
    __KEY_SEARCH_ID = "search_id"
    __KEY_OFFSET = "offset"
    __KEY_KEYWORDS = "keywords"
    __KEY_APP_ID = "app_id"

    date = None
    method = None
    chat = None
    from_ = None
    search_id = None
    offset = None
    keywords = None
    app_id = None

    def __init__(self, dictionary):

        inline_search_dict = dictionary[self.__KEY_INLINE_SEARCH] if self.__KEY_INLINE_SEARCH in dictionary.keys() else {}

        from_user = User(inline_search_dict.get(self.__KEY_FROM, {}))

        self.chat = Chat(inline_search_dict.get(self.__KEY_CHAT, None))
        self.method = str(inline_search_dict[self.__KEY_METHOD]) if self.__KEY_METHOD in inline_search_dict.keys() else None
        self.from_ = from_user
        self.date = int(inline_search_dict[self.__KEY_DATE]) if self.__KEY_DATE in inline_search_dict.keys() else None
        self.search_id = int(inline_search_dict[self.__KEY_SEARCH_ID]) if self.__KEY_SEARCH_ID in inline_search_dict.keys() else None
        self.offset = str(inline_search_dict[self.__KEY_OFFSET]) if self.__KEY_OFFSET in inline_search_dict.keys() else None
        self.keywords = str(inline_search_dict[self.__KEY_KEYWORDS]) if self.__KEY_KEYWORDS in inline_search_dict.keys() else None
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
        if self.method is not None:
            dictionary[self.__KEY_METHOD] = self.method
        if self.search_id is not None:
            dictionary[self.__KEY_SEARCH_ID] = self.search_id
        if self.offset is not None:
            dictionary[self.__KEY_OFFSET] = self.offset
        if self.keywords is not None:
            dictionary[self.__KEY_KEYWORDS] = self.keywords
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id

        return json.dumps(dictionary), dictionary

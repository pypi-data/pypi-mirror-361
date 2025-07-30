import json

from nandboxbots.outmessages.OutMessage import OutMessage


class CreateChatOutMessage(OutMessage):
    __KEY_CHAT = "chat"
    __KEY_TYPE = "type"
    __KEY_TITLE = "title"
    __KEY_REFERENCE = "reference"
    __KEY_IS_PUBLIC = "isPublic"
    __KEY_TIMEZONE = "timezone"

    type = None
    title = None
    isPublic = None
    reference = None

    def __int__(self):
        self.method = "createChat"

    def to_json_obj(self):
        _, dictionary = super(CreateChatOutMessage, self).to_json_obj()
        chat_dict = {}
        if self.type is not None:
            if self.type == "Group":
                chat_dict[self.__KEY_TYPE] = "Group"
                chat_dict[self.__KEY_IS_PUBLIC] = self.isPublic
                chat_dict[self.__KEY_TIMEZONE] = "Africa/Cairo"
                chat_dict[self.__KEY_TITLE] = self.title

        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference

        dictionary[self.__KEY_CHAT] = chat_dict

        return json.dumps(dictionary), dictionary

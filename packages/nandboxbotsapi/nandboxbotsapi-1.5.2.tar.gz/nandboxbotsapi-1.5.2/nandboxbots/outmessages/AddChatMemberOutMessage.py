import json

from nandboxbots.outmessages.OutMessage import OutMessage


class AddChatMemberOutMessage(OutMessage):
    __KEY_CHAT_ID = "chat_id"
    __KEY_USER_ID = "user_id"

    chatId = None
    userId = None

    def __int__(self):
        self.method = "addChatMember"

    def to_json_obj(self):
        _, dictionary = super(AddChatMemberOutMessage, self).to_json_obj()

        if self.chatId is not None:
            dictionary[self.__KEY_CHAT_ID] = self.chatId
        if self.userId is not None:
            dictionary[self.__KEY_USER_ID] = self.userId

        return json.dumps(dictionary), dictionary

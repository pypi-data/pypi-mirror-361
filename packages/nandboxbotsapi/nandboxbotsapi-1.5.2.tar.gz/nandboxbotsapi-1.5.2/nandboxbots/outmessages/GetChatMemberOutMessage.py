import json

from nandboxbots.outmessages.OutMessage import OutMessage


class GetChatMemberOutMessage(OutMessage):
    __KEY_CHAT_ID  = "chat_id"
    __KEY_USER_ID = "user_id"
    user_id = None

    def __init__(self):
        super()
        self.method = "getChatMember"

    def to_json_obj(self):
        _, dictionary = super(GetChatMemberOutMessage, self).to_json_obj()

        if self.chat_id is not None:
            dictionary[self.__KEY_CHAT_ID] = self.chat_id
        if self.user_id is not None:
            dictionary[self.__KEY_USER_ID] = self.user_id

        return json.dumps(dictionary), dictionary
    
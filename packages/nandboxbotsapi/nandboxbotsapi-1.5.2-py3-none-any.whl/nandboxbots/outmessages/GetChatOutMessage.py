import json

from nandboxbots.outmessages.OutMessage import OutMessage


class GetChatOutMessage(OutMessage):
    __KEY_CHAT_ID = "chat_id"
    def __init__(self):
        self.method = "getChat"

    def to_json_obj(self):
        _, dictionary = super(GetChatOutMessage, self).to_json_obj()

        if self.chat_id is not None:
            dictionary[self.__KEY_CHAT_ID] = self.chat_id

        return json.dumps(dictionary), dictionary
    
import json

from nandboxbots.outmessages.OutMessage import OutMessage


class SetChatOutMessage(OutMessage):
    __KEY_CHAT = "chat"

    chat = None

    def __init__(self):
        self.method = "setChat"

    def to_json_obj(self):
        _, dictionary = super(SetChatOutMessage, self).to_json_obj()

        if self.chat is not None:
            dictionary[self.__KEY_CHAT] = self.chat.to_dict()

        return json.dumps(dictionary), dictionary

    
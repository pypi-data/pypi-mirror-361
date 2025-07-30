import json

from nandboxbots.outmessages.OutMessage import OutMessage


class SetChatMenuOutMessage(OutMessage):
    __KEY_MENU = "menus"

    menus = []

    def __init__(self):
        self.method = "setChatMenu"

    def to_json_obj(self):
        _, dictionary = super(SetChatMenuOutMessage, self).to_json_obj()

        if self.menus is not None:
            dictionary[self.__KEY_MENU] = self.menus

        return json.dumps(dictionary), dictionary

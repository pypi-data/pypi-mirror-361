import json

from nandboxbots.outmessages.OutMessage import OutMessage


class AddWhiteListOutMessage(OutMessage):
    __KEY_USERS = "signups"

    white_list_users = []

    def __init__(self):
        self.method = "addToWhitelist"

    def to_json_obj(self):
        _, dictionary = super(AddWhiteListOutMessage, self).to_json_obj()

        if self.white_list_users is not None:
            dictionary[self.__KEY_USERS] = self.white_list_users

        return json.dumps(dictionary), dictionary


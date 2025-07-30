import json

from nandboxbots.outmessages.OutMessage import OutMessage


class AddBlacklistPatternsOutMessage(OutMessage):
    __KEY_DATA = "patterns"

    data = []

    def __init__(self):
        self.method = "addBlacklistPatterns"

    def to_json_obj(self):
        _, dictionary = super(AddBlacklistPatternsOutMessage, self).to_json_obj()

        if self.data is not None:
            dictionary[self.__KEY_DATA] = self.data

        return json.dumps(dictionary), dictionary
    
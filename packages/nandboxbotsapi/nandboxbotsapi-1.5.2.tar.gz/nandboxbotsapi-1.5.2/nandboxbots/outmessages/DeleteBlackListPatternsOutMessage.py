import json

from nandboxbots.outmessages.OutMessage import OutMessage


class DeleteBlackListPatternsOutMessage(OutMessage):
    __KEY_PATTERN = "patterns"

    pattern = []
    def __init__(self):
        self.method = "removeBlacklistPatterns"

    def to_json_obj(self):
        _, dictionary = super(DeleteBlackListPatternsOutMessage, self).to_json_obj()

        if self.pattern is not None:
            dictionary[self.__KEY_PATTERN] = self.pattern

        return json.dumps(dictionary), dictionary
    
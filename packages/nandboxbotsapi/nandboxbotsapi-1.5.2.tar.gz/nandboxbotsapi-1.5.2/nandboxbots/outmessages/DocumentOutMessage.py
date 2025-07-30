import json

from nandboxbots.outmessages.OutMessage import OutMessage


class DocumentOutMessage(OutMessage):
    __KEY_DOCUMENT = "document"
    __KEY_NAME = "name"
    __KEY_SIZE = "size"

    document = None
    name = None
    size = None

    def __init__(self):
        self.method = "sendDocument"

    def to_json_obj(self):
        _, dictionary = super(DocumentOutMessage, self).to_json_obj()

        if self.document is not None:
            dictionary[self.__KEY_DOCUMENT] = self.document
        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.size is not None:
            dictionary[self.__KEY_SIZE] = self.size

        return json.dumps(dictionary), dictionary


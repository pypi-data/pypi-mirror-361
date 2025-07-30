import json

from nandboxbots.outmessages.OutMessage import OutMessage


class ContactOutMessage(OutMessage):
    __KEY_NAME = "name"
    __KEY_PHONE_NUMBER = "phone_number"

    name = None
    phone_number = None

    def __init__(self):
        self.method = "sendContact"

    def to_json_obj(self):
        _, dictionary = super(ContactOutMessage, self).to_json_obj()

        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.phone_number is not None:
            dictionary[self.__KEY_PHONE_NUMBER] = self.phone_number

        return json.dumps(dictionary), dictionary

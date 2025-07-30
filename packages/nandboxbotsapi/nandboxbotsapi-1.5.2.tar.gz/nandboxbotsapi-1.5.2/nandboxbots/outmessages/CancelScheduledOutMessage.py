import json

from nandboxbots.outmessages.OutMessage import OutMessage


class CancelScheduledOutMessage(OutMessage):
    __KEY_MESSAGE_ID = "message_id"

    message_id = None

    def __init__(self):
        self.method = "cancelMessageSchedule"

    def to_json_obj(self):
        _, dictionary = super(CancelScheduledOutMessage, self).to_json_obj()

        if self.message_id is not None:
            dictionary[self.__KEY_MESSAGE_ID] = self.message_id

        return json.dumps(dictionary), dictionary

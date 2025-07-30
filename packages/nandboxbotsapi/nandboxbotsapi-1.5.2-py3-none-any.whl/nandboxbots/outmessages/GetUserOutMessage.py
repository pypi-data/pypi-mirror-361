import json

from nandboxbots.outmessages.OutMessage import OutMessage


class GetUserOutMessage(OutMessage):
    __KEY_USER_ID = "user_id"

    user_id = None

    def __init__(self):
        self.method = "getUser"

    def to_json_obj(self):
        _, dictionary = super(GetUserOutMessage, self).to_json_obj()

        if self.user_id is not None:
            dictionary[self.__KEY_USER_ID] = self.user_id

        return json.dumps(dictionary), dictionary
    
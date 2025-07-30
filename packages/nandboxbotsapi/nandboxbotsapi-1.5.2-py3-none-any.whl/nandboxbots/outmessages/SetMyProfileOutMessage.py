import json

from nandboxbots.outmessages.OutMessage import OutMessage


class SetMyProfileOutMessage(OutMessage):
    __KEY_USER = "user"

    user = None

    def __init__(self):
        self.method = "setMyProfile"

    def to_json_obj(self):
        _, dictionary = super(SetMyProfileOutMessage, self).to_json_obj()

        if self.user is not None:
            dictionary[self.__KEY_USER] = self.user.to_dict()

        return json.dumps(dictionary), dictionary
    

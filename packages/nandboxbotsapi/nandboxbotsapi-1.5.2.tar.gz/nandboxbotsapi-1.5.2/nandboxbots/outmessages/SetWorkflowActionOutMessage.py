import json

from nandboxbots.outmessages.OutMessage import OutMessage


class SetWorkflowActionOutMessage(OutMessage):
    __KEY_USER_ID = "user_id"
    __KEY_REFERENCE = "reference"
    __KEY_SCREEN_ID = "screen_id"
    __KEY_NEXT_SCREEN = "next_screen"
    __KEY_VAPP_ID = "vapp_id"

    userId = None
    vappId = None
    screenId = None
    nextScreen = None
    reference = None

    def __int__(self):
        self.method = "setWorkflowAction"

    def to_json_obj(self):
        _, dictionary = super(SetWorkflowActionOutMessage, self).to_json_obj()

        if self.userId is not None:
            dictionary[self.__KEY_USER_ID] = self.userId
        if self.vappId is not None:
            dictionary[self.__KEY_VAPP_ID] = self.vappId
        if self.screenId is not None:
            dictionary[self.__KEY_SCREEN_ID] = self.screenId
        if self.nextScreen is not None:
            dictionary[self.__KEY_NEXT_SCREEN] = self.nextScreen
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference

        return json.dumps(dictionary), dictionary
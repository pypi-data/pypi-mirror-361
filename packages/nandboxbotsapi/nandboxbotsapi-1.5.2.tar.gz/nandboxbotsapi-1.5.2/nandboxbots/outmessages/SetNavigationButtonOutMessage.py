import json

from nandboxbots.outmessages.OutMessage import OutMessage


class SetNavigationButtonOutMessage(OutMessage):
    __KEY_NAVIGATION_BUTTONS = "navigation_button"

    navigation_button = ""

    def __init__(self):
        self.method = "setNavigationButton"

    def to_json_obj(self):
        _, dictionary = super(SetNavigationButtonOutMessage, self).to_json_obj()

        if self.navigation_button is not None:
            dictionary[self.__KEY_NAVIGATION_BUTTONS] = self.navigation_button

        return json.dumps(dictionary), dictionary
    

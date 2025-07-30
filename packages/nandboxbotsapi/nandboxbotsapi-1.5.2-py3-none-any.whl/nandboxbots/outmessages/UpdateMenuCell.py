import json

from nandboxbots.outmessages.OutMessage import OutMessage


class UpdateMenuCell(OutMessage):
    __KEY_USER_ID = "user_id"
    __KEY_MENU_ID = "menu_id"
    __KEY_CELLS = "cells"
    __KEY_APP_ID = "app_id"
    __KEY_DISABLE_NOTIFICATION = "disable_notification"

    userId = None
    appId = None
    menuId = None
    disableNotification = None
    cells = None

    def __init__(self):
        self.method = "updateMenuCell"

    def to_json_obj(self):
        _, dictionary = super(UpdateMenuCell, self).to_json_obj()

        if self.cells is not None:
            dictionary[self.__KEY_CELLS] = self.cells
        if self.userId is not None:
            dictionary[self.__KEY_USER_ID] = self.userId
        if self.appId is not None:
            dictionary[self.__KEY_APP_ID] = self.appId
        if self.menuId is not None:
            dictionary[self.__KEY_MENU_ID] = self.menuId
        if self.disableNotification is not None:
            dictionary[self.__KEY_DISABLE_NOTIFICATION] = self.disableNotification

        return json.dumps(dictionary), dictionary

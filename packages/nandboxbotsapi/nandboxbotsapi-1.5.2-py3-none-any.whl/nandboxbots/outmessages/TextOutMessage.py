import json
import logging
import traceback

from nandboxbots.outmessages.OutMessage import OutMessage

class TextOutMessage(OutMessage):
    __KEY_TEXT = "text"
    __KEY_BG_COLOR = "bg_color"

    text = None
    bg_color = None

    def __init__(self):
        self.method = "sendMessage"

    def to_json_obj(self):
        _, obj = super(TextOutMessage, self).to_json_obj()

        if self.text is not None:
            obj[self.__KEY_TEXT] = self.text
        if self.bg_color is not None:
            obj[self.__KEY_BG_COLOR] = self.bg_color

        return json.dumps(obj), obj


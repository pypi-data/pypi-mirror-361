import enum
import json

from nandboxbots.outmessages.OutMessage import OutMessage


class GifOutMessage(OutMessage):
    __KEY_PHOTO = "photo"
    __KEY_VIDEO = "video"

    class GifType(enum.Enum):
        PHOTO = 1
        VIDEO = 2

    gif = None
    gif_type = GifType.PHOTO

    def __init__(self, gif_type=None):
        self.gif_type = gif_type

        if gif_type == GifOutMessage.GifType.PHOTO:
            self.method = "sendPhoto"
        elif gif_type == GifOutMessage.GifType.PHOTO:
            self.method = "sendVideo"
        else:
            self.method = "sendPhoto"

    def to_json_obj(self):
        _, dictionary = super(GifOutMessage, self).to_json_obj()

        if self.gif is not None:
            if self.gif_type == GifOutMessage.GifType.PHOTO:
                dictionary[self.__KEY_PHOTO] = self.gif
            elif self.gif_type == GifOutMessage.GifType.VIDEO:
                dictionary[self.__KEY_VIDEO] = self.gif
            else:
                dictionary[self.__KEY_PHOTO] = self.gif

        return json.dumps(dictionary), dictionary


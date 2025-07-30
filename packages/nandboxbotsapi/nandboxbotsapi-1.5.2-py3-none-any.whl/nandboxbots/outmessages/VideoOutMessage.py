import json

from nandboxbots.outmessages.OutMessage import OutMessage


class VideoOutMessage(OutMessage):
    __KEY_VIDEO = "video"

    video = None

    def __init__(self):
        self.method = "sendVideo"

    def to_json_obj(self):
        _, dictionary = super(VideoOutMessage, self).to_json_obj()

        if self.video is not None:
            dictionary[self.__KEY_VIDEO] = self.video

        return json.dumps(dictionary), dictionary

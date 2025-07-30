import json

from nandboxbots.outmessages.OutMessage import OutMessage


class AudioOutMessage(OutMessage):
    __KEY_AUDIO = "audio"
    __KEY_PERFORMER = "performer"
    __KEY_TITLE = "title"

    audio = None
    performer = None
    title = None

    def __init__(self):
        self.method = "sendAudio"

    def to_json_obj(self):
        _, dictionary = super(AudioOutMessage, self).to_json_obj()

        if self.audio is not None:
            dictionary[self.__KEY_AUDIO] = self.audio
        if self.performer is not None:
            dictionary[self.__KEY_PERFORMER] = self.performer
        if self.title is not None:
            dictionary[self.__KEY_TITLE] = self.title

        return json.dumps(dictionary), dictionary

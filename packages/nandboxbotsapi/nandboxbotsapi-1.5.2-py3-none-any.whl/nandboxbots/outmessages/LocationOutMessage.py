import json

from nandboxbots.outmessages.OutMessage import OutMessage


class LocationOutMessage(OutMessage):
    __KEY_NAME = "name"
    __KEY_DETAILS = "details"
    __KEY_LONGITUDE = "longitude"
    __KEY_LATITUDE = "latitude"

    longitude = None
    latitude = None
    name = None
    details = None

    def __init__(self):
        self.method = "sendLocation"

    def to_json_obj(self):
        _, dictionary = super(LocationOutMessage, self).to_json_obj()

        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.details is not None:
            dictionary[self.__KEY_DETAILS] = self.details
        if self.latitude is not None:
            dictionary[self.__KEY_LATITUDE] = self.latitude
        if self.longitude is not None:
            dictionary[self.__KEY_LONGITUDE] = self.longitude

        return json.dumps(dictionary), dictionary


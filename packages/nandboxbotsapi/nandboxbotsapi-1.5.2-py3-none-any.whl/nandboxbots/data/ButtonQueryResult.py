import json


class ButtonQueryResult:
    __KEY_LATITUDE = "latitude"
    __KEY_LONGITUDE = "longitude"
    __KEY_CONTACT = "contact"

    latitude = None
    longitude = None
    contact = None

    def __init__(self, dictionary):
        self.latitude = str(dictionary[self.__KEY_LATITUDE]) if self.__KEY_LATITUDE in dictionary.keys() else None
        self.longitude = str(dictionary[self.__KEY_LONGITUDE]) if self.__KEY_LONGITUDE in dictionary.keys() else None
        self.contact = str(dictionary[self.__KEY_CONTACT]) if self.__KEY_CONTACT in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.latitude is not None:
            dictionary[self.__KEY_LATITUDE] = self.latitude
        if self.longitude is not None:
            dictionary[self.__KEY_LONGITUDE] = self.longitude
        if self.contact is not None:
            dictionary[self.__KEY_CONTACT] = self.contact

        return json.dumps(dictionary), dictionary


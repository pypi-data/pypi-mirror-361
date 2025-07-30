import json


class Location:
    __KEY_NAME = "name"
    __KEY_DETAILS = "details"
    __KEY_LONGITUDE = "longitude"
    __KEY_LATITUDE = "latitude"

    longitude = None
    latitude = None
    name = None
    details = None

    def __init__(self, dictionary):
        self.name = str(dictionary[self.__KEY_NAME]) if self.__KEY_NAME in dictionary.keys() else None
        self.details = str(dictionary[self.__KEY_DETAILS]) if self.__KEY_DETAILS in dictionary.keys() else None
        self.longitude = str(dictionary[self.__KEY_LONGITUDE]) if self.__KEY_LONGITUDE in dictionary.keys() else None
        self.latitude = str(dictionary[self.__KEY_LATITUDE]) if self.__KEY_LATITUDE in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.details is not None:
            dictionary[self.__KEY_DETAILS] = self.details
        if self.longitude is not None:
            dictionary[self.__KEY_LONGITUDE] = self.longitude
        if self.latitude is not None:
            dictionary[self.__KEY_LATITUDE] = self.latitude

        return json.dumps(dictionary), dictionary

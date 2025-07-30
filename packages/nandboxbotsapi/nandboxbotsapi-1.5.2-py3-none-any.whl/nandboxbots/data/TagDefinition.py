import json


class TagDefinition:
    __KEY_NAME = "name"
    __KEY_DESCRIPTION = "description"
    __KEY_ID = "id"
    __KEY_ISPRIVATE = "isPrivate"

    name = None
    description = None
    id = None
    is_private = None

    def __init__(self, dictionary):

        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.name = str(dictionary[self.__KEY_NAME]) if self.__KEY_NAME in dictionary.keys() else None
        self.description = str(dictionary[self.__KEY_DESCRIPTION]) if self.__KEY_DESCRIPTION in dictionary.keys() else None
        self.is_private = str(dictionary[self.__KEY_ISPRIVATE]) if self.__KEY_ISPRIVATE in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.description is not None:
            dictionary[self.__KEY_DESCRIPTION] = self.description
        if self.is_private is not None:
            dictionary[self.__KEY_ISPRIVATE] = self.is_private

        return json.dumps(dictionary), dictionary

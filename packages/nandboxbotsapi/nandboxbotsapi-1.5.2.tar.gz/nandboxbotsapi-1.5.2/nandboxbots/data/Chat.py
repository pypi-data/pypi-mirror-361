import json

from nandboxbots.data.TagDefinition import TagDefinition


class Chat:
    __KEY_ID = "id"
    __KEY_TITLE = "title"
    __KEY_NAME = "name"
    __KEY_TYPE = "type"
    __KEY_VERSION = "version"
    __KEY_LANGUAGE_CODE = "language_code"
    __KEY_REGIONS = "regions"
    __KEY_DESCRIPTION = "description"
    __KEY_PHOTO = "photo"
    __KEY_CATEGORY = "category"
    __KEY_MEMBER_COUNT = "member_count"
    __KEY_INVITE_LINK = "invite_link"
    __KEY_TAGS_DEFINITION = "tagsDefinition"
    __KEY_REFERENCE = "reference"

    id = None
    title = None
    name = None
    type = None
    version = None
    language_code = None
    regions = None
    description = None
    photo = None
    category = None
    member_count = None
    invite_link = None
    tags_definition = None
    reference = None

    def __init__(self, dictionary=None):
        if dictionary is None:
            dictionary = {}
        self.id = int(dictionary[self.__KEY_ID]) if (self.__KEY_ID in dictionary.keys() and dictionary[self.__KEY_ID] is not None) else None
        self.title = str(dictionary[self.__KEY_TITLE]) if self.__KEY_TITLE in dictionary.keys() else None
        self.name = str(dictionary[self.__KEY_NAME]) if self.__KEY_NAME in dictionary.keys() else None
        self.type = str(dictionary[self.__KEY_TYPE]) if self.__KEY_TYPE in dictionary.keys() else None
        self.version = str(dictionary[self.__KEY_VERSION]) if self.__KEY_VERSION in dictionary.keys() else None
        self.language_code = str(dictionary[self.__KEY_LANGUAGE_CODE]) if (self.__KEY_LANGUAGE_CODE in dictionary.keys() and dictionary[self.__KEY_LANGUAGE_CODE] is not None) else None
        self.regions = str(dictionary[self.__KEY_REGIONS]) if self.__KEY_REGIONS in dictionary.keys() else None
        self.description = str(dictionary[self.__KEY_DESCRIPTION]) if self.__KEY_DESCRIPTION in dictionary.keys() else None
        self.category = str(dictionary[self.__KEY_CATEGORY]) if self.__KEY_CATEGORY in dictionary.keys() else None
        self.member_count = int(dictionary[self.__KEY_MEMBER_COUNT]) if (self.__KEY_MEMBER_COUNT in dictionary.keys() and dictionary[self.__KEY_MEMBER_COUNT] is not None) else None
        self.invite_link = str(dictionary[self.__KEY_INVITE_LINK]) if self.__KEY_INVITE_LINK in dictionary.keys() else None
        self.reference = int(dictionary[self.__KEY_REFERENCE]) if (self.__KEY_REFERENCE in dictionary.keys() and dictionary[self.__KEY_REFERENCE] is not None) else None

        tags_arr_obj = dictionary.get(self.__KEY_TAGS_DEFINITION, None)
        if tags_arr_obj is not None:
            self.tags_definition = [None] * len(tags_arr_obj)
            for i in range(len(tags_arr_obj)):
                self.tags_definition[i] = TagDefinition(tags_arr_obj[i])

    def to_json_obj(self):

        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.title is not None:
            dictionary[self.__KEY_TITLE] = self.title
        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.type is not None:
            dictionary[self.__KEY_TYPE] = self.type
        if self.version is not None:
            dictionary[self.__KEY_VERSION] = self.version
        if self.language_code is not None:
            dictionary[self.__KEY_LANGUAGE_CODE] = self.language_code
        if self.regions is not None:
            dictionary[self.__KEY_REGIONS] = self.regions
        if self.description is not None:
            dictionary[self.__KEY_DESCRIPTION] = self.description
        if self.category is not None:
            dictionary[self.__KEY_CATEGORY] = self.category
        if self.member_count is not None:
            dictionary[self.__KEY_MEMBER_COUNT] = self.member_count
        if self.invite_link is not None:
            dictionary[self.__KEY_INVITE_LINK] = self.invite_link
        if self.photo is not None:
            dictionary[self.__KEY_PHOTO] = self.photo
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE]=self.reference

        return json.dumps(dictionary), dictionary

    def to_dict(self):
        return {
            self.__KEY_ID: self.id,
            self.__KEY_TITLE: self.title,
            self.__KEY_NAME: self.name,
            self.__KEY_TYPE: self.type,
            self.__KEY_VERSION: self.version,
            self.__KEY_LANGUAGE_CODE: self.language_code,
            self.__KEY_REGIONS: self.regions,
            self.__KEY_DESCRIPTION: self.description,
            self.__KEY_CATEGORY: self.category,
            self.__KEY_MEMBER_COUNT: self.member_count,
            self.__KEY_INVITE_LINK: self.invite_link,
            self.__KEY_PHOTO: self.photo,
            self.__KEY_REFERENCE: self.reference
        }

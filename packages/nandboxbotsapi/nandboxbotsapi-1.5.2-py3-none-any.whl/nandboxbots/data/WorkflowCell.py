import json


class WorkflowCell:
    __KEY_CELL_ID = "cell_id"
    __KEY_CALLBACK = "callback"
    __KEY_API_ID = "api_id"
    __KEY_CACHE = "cache"
    __KEY_NEXT_SCREEN = "next_screen"
    __KEY_URL = "url"
    __KEY_BG_COLOR = "bg_color"
    __KEY_LABEL = "label"
    __KEY_LABEL_COLOR = "label_color"
    __KEY_SUBLABEL = "sublabel"
    __KEY_SUBLABEL_COLOR = "sublabel_color"
    __KEY_HINT = "hint"
    __KEY_VALUE = "value"

    cellId = None
    callBack = None
    apiId = None
    cache = None
    nextScreen = None
    url = None
    bgColor = None
    label = None
    labelColor = None
    subLabel = None
    subLabelColor = None
    hint = None
    value = None

    def __init__(self, dictionary):
        self.cellId = str(dictionary[self.__KEY_CELL_ID]) if self.__KEY_CELL_ID in dictionary.keys() else None
        self.callBack = str(dictionary[self.__KEY_CALLBACK]) if self.__KEY_CALLBACK in dictionary.keys() else None
        self.apiId = int(dictionary[self.__KEY_API_ID]) if self.__KEY_API_ID in dictionary.keys() else None
        self.cache = bool(dictionary[self.__KEY_CACHE]) if self.__KEY_CACHE in dictionary.keys() else None
        self.nextScreen = str(
            dictionary[self.__KEY_NEXT_SCREEN]) if self.__KEY_NEXT_SCREEN in dictionary.keys() else None
        self.url = str(dictionary[self.__KEY_URL]) if self.__KEY_URL in dictionary.keys() else None
        self.bgColor = str(dictionary[self.__KEY_BG_COLOR]) if self.__KEY_BG_COLOR in dictionary.keys() else None
        self.label = str(dictionary[self.__KEY_LABEL]) if self.__KEY_LABEL in dictionary.keys() else None
        self.labelColor = str(
            dictionary[self.__KEY_LABEL_COLOR]) if self.__KEY_LABEL_COLOR in dictionary.keys() else None
        self.subLabel = str(dictionary[self.__KEY_SUBLABEL]) if self.__KEY_SUBLABEL in dictionary.keys() else None
        self.subLabelColor = str(
            dictionary[self.__KEY_SUBLABEL_COLOR]) if self.__KEY_SUBLABEL_COLOR in dictionary.keys() else None
        self.hint = str(dictionary[self.__KEY_HINT]) if self.__KEY_HINT in dictionary.keys() else None
        self.value = str(dictionary[self.__KEY_VALUE]) if self.__KEY_VALUE in dictionary.keys() else None

    def to_json_obj(self):
        dictionary = {}
        if self.cellId is not None:
            dictionary[self.__KEY_CELL_ID]= self.cellId
        if self.callBack is not None:
            dictionary[self.__KEY_CALLBACK]= self.callBack
        if self.apiId is not None:
            dictionary[self.__KEY_API_ID]= self.apiId
        if self.cache is not None:
            dictionary[self.__KEY_CACHE]= self.cache
        if self.nextScreen is not None:
            dictionary[self.__KEY_NEXT_SCREEN]= self.nextScreen
        if self.url is not None:
            dictionary[self.__KEY_URL]= self.url
        if self.bgColor is not None:
            dictionary[self.__KEY_BG_COLOR]= self.bgColor
        if self.label is not None:
            dictionary[self.__KEY_LABEL]= self.label
        if self.labelColor is not None:
            dictionary[self.__KEY_LABEL_COLOR]= self.labelColor
        if self.subLabel is not None:
            dictionary[self.__KEY_SUBLABEL]= self.subLabel
        if self.subLabelColor is not None:
            dictionary[self.__KEY_SUBLABEL_COLOR]= self.subLabelColor
        if self.hint is not None:
            dictionary[self.__KEY_HINT]= self.hint
        if self.value is not None:
            dictionary[self.__KEY_VALUE]= self.value

        return dictionary

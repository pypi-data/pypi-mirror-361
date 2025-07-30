import json


class MessageAck:
    __KEY_ACK = "ack"
    __KEY_MESSAGE_ID = "message_id"
    __KEY_DATE = "date"
    __KEY_REFERENCE = "reference"
    message_id = None
    date = None
    reference = None
    def __init__(self, dictionary):

        ack_dict = dictionary[self.__KEY_ACK] if self.__KEY_ACK in dictionary.keys() else {}

        self.message_id = str(ack_dict[self.__KEY_MESSAGE_ID]) if self.__KEY_MESSAGE_ID in ack_dict.keys() else None
        self.reference = str(ack_dict[self.__KEY_REFERENCE]) if self.__KEY_REFERENCE in ack_dict.keys() else None
        self.date = int(ack_dict[self.__KEY_DATE]) if self.__KEY_DATE in ack_dict.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.date is not None:
            dictionary[self.__KEY_DATE] = self.date
        if self.message_id is not None:
            dictionary[self.__KEY_MESSAGE_ID] = self.message_id
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference

        return json.dumps(dictionary), dictionary

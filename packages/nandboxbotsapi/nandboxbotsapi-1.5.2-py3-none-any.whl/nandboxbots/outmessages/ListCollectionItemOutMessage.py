import json
from nandboxbots.outmessages.OutMessage import OutMessage


class ListCollectionItemOutMessage(OutMessage):
    def __init__(self):
        super().__init__()  # Initialize the parent class
        self.method = "listCollections"

    def to_json_obj(self):
        _, dictionary = super(ListCollectionItemOutMessage, self).to_json_obj()
        return json.dumps(dictionary), dictionary

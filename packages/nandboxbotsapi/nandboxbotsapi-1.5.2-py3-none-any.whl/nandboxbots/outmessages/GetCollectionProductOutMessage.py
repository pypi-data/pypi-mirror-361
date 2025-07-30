from nandboxbots.outmessages.OutMessage import OutMessage
import json

class GetCollectionProductOutMessage(OutMessage):
    def __init__(self):
        super().__init__()
        self.method = "getCollectionProduct"
        self.id = None  # Assuming `id` should be defined

    def to_json_obj(self):
        _, dictionary = super().to_json_obj()
        if self.id:
            dictionary['id'] = self.id
        return json.dumps(dictionary), dictionary
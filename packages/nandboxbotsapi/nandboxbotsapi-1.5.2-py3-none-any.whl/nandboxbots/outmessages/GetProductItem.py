# Assuming OutMessage class is imported or defined elsewhere
from nandboxbots.outmessages.OutMessage import OutMessage
import json

class GetProductItemOutMessage(OutMessage):
    def __init__(self):
        super().__init__()
        self.method = "getProductItem"
        self.id = None
        self.app_id = None
        self.reference =None

    def to_json_obj(self):
        _, dictionary = super().to_json_obj()
        if self.id:
            dictionary['id'] = self.id
        if self.reference:
            dictionary["ref"]=self.reference
        return json.dumps(dictionary),  dictionary

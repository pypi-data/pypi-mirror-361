import json
from nandboxbots.data.Category import Category

class ListCollectionItemResponse:
    def __init__(self, category_list):
        # Directly initializing categories from the list of dictionaries
        self.categories = [Category(category_dict) for category_dict in category_list.collections]
        self.reference = category_list.reference
        self.business_channel_id = category_list.business_channel_id

    def to_json_obj(self):
        # Returns a dictionary suitable for converting to JSON
        return {
            'collections': [category.to_json_obj() for category in self.categories]
        }

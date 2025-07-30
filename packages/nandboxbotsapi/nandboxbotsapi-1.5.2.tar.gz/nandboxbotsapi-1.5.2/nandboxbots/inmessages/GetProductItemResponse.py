import json

from nandboxbots.data.ProductItem import ProductItem


class GetProductItemResponse:
    def __init__(self, obj):
        self.productItem = ProductItem(obj.data) if obj.data else None
        self.app_id = obj.app_id
        self.reference = obj.reference
    def to_json_obj(self):
        obj = {}
        if self.productItem:
            obj['productItem'] = self.productItem.to_json_obj()
        return obj

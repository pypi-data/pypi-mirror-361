from nandboxbots.data.CollectionProduct import CollectionProduct

class GetCollectionProductResponse:
    def __init__(self, obj_list):
        self.collection_products = [CollectionProduct(item) for item in obj_list["products"]]
        self.app_id = obj_list["app_id"]
        self.reference = obj_list["reference"]
    def to_json_obj(self):
        return [product.to_json_obj() for product in self.collection_products]

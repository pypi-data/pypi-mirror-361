import json

class Image:
    def __init__(self, dictionary):
        self.width = dictionary.get('width', None)
        self.url = dictionary.get('url', None)
        self.height = dictionary.get('height', None)

    def to_json_obj(self):
        dictionary = {}
        if self.width is not None:
            dictionary['width'] = self.width
        if self.url is not None:
            dictionary['url'] = self.url
        if self.height is not None:
            dictionary['height'] = self.height
        return dictionary

class CollectionProduct:
    def __init__(self, obj):
        self.id = obj.get('id', None)
        self.name = obj.get('name', None)
        self.price = obj.get('price', None)
        self.status = obj.get('status', None)
        self.app_id = obj.get('app_id', None)
        self.business_channel_id = obj.get('business_channel_id', None)
        self.category = obj.get('category', None)

        self.image = [Image(img) for img in obj.get('image', [])]

    def to_json_obj(self):
        obj = {}
        if self.id is not None:
            obj['id'] = self.id
        if self.name is not None:
            obj['name'] = self.name
        if self.price is not None:
            obj['price'] = self.price
        if self.status is not None:
            obj['status'] = self.status

        if self.app_id is not None:
            obj['app_id'] = self.app_id
        if self.business_channel_id is not None:
            obj['business_channel_id'] = self.business_channel_id
        if self.category is not None:
            obj['category'] = self.category

        if self.image is not None:
            obj['image'] = [img.to_json_obj() for img in self.image]
        return obj

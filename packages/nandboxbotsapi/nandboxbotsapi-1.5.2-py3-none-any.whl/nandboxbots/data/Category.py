import json

from nandboxbots.data.Image import Image
class Category:
    def __init__(self, dictionary):
        self.id = dictionary.get('id')
        self.name = dictionary.get('name')
        self.description = dictionary.get('description')
        self.category = dictionary.get('category')
        self.date = dictionary.get('date')
        self.version = dictionary.get('version')
        self.status = dictionary.get('status')
        self.images = [Image(img) for img in dictionary.get('image', [])]

    def to_json_obj(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'date': self.date,
            'version': self.version,
            'status': self.status,
            'image': [img.to_json_obj() for img in self.images]
        }

class Image:
    def __init__(self, dictionary):
        self.width = dictionary.get('width')
        self.url = dictionary.get('url')
        self.height = dictionary.get('height')

    def to_json_obj(self):
        return {
            'width': self.width,
            'url': self.url,
            'height': self.height
        }

import json

from nandboxbots.outmessages.OutMessage import OutMessage


class ArticleOutMessage(OutMessage):
    __KEY_URL = "url"
    __KEY_TITLE = "title"
    __KEY_DESCRIPTION = "description"
    __KEY_PHOTO = "photo"
    __KEY_PHOTO_URL = "photo_url"

    url = None
    title = None
    description = None
    photo = None
    photo_url = None

    def __init__(self):
        self.method = "sendArticle"

    def to_json_obj(self):
        _, dictionary = super(ArticleOutMessage, self).to_json_obj()

        if self.url is not None:
            dictionary[self.__KEY_URL] = self.url
        if self.title is not None:
            dictionary[self.KEY_TIILE] = self.title
        if self.description is not None:
            dictionary[self.__KEY_DESCRIPTION] = self.description
        if self.photo is not None:
            dictionary[self.__KEY_PHOTO] = self.photo
        if self.photo_url is not None:
            dictionary[self.__KEY_PHOTO_URL] = self.photo_url

        return json.dumps(dictionary), dictionary

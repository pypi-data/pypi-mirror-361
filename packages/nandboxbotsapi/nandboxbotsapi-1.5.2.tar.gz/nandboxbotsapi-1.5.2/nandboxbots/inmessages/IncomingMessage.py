import json
import logging

from nandboxbots.data.Article import Article
from nandboxbots.data.Audio import Audio
from nandboxbots.data.Chat import Chat
from nandboxbots.data.Contact import Contact
from nandboxbots.data.Document import Document
from nandboxbots.data.Gif import Gif
from nandboxbots.data.Location import Location
from nandboxbots.data.Photo import Photo
from nandboxbots.data.Sticker import Sticker
from nandboxbots.data.TextFile import TextFile
from nandboxbots.data.User import User
from nandboxbots.data.Video import Video
from nandboxbots.data.Voice import Voice
from nandboxbots.data.WhiteListUser import WhiteListUser


class IncomingMessage:
    __KEY_MESSAGE = "message"
    __KEY_MESSAGE_ID = "message_id"
    __KEY_TYPE = "type"
    __KEY_FROM_ADMIN = "from_admin"
    __KEY_DATE = "date"
    __KEY_TEXT = "text"
    __KEY_LOCATION = "location"
    __KEY_CONTACT = "contact"
    __KEY_DOCUMENT = "document"
    __KEY_FROM = "from"
    __KEY_CHAT = "chat"
    __KEY_REFERENCE = "reference"
    __KEY_SENT_TO = "sent_to"
    __KEY_PHOTO = "photo"
    __KEY_GIF = "gif"
    __KEY_VIDEO = "video"
    __KEY_AUDIO = "audio"
    __KEY_VOICE = "voice"
    __KEY_CAPTION = "caption"
    __KEY_STICKER = "sticker"
    __KEY_REPLY_TO_MESSAGE_ID = "reply_to_message_id"
    __KEY_TEXT_FILE = "text_file"
    __KEY_STATUS = "status"
    __KEY_CHAT_SETTINGS = "chat_settings"
    __KEY_BG_COLOR = "bg_color"
    __KEY_WHITELIST_USER = "users"
    __KEY_ARTICLE = "article"
    __KEY_URL = "url"
    __KEY_SCHEDULE_DATE = "schedule_date"
    __KEY_TAGS= "tags"
    __KEY_APP_ID = "app_id"

    message_id = None
    type = None
    date = None
    reference = None
    from_ = None
    reply_to_message_id = None
    caption = None
    from_admin = None
    chat = None
    text = None
    location = None
    contact = None
    sent_to = None
    photo = None
    gif = None
    voice = None
    video = None
    audio = None
    document = None
    sticker = None
    text_file = None
    status = None
    chat_settings = None
    bg_color = None
    article = None
    url = None
    white_list_user = None
    tag = None
    schedule_date = None
    tags=None
    app_id = None

    def __init__(self, dictionary):
        msg_dict = dictionary[self.__KEY_MESSAGE]

        from_user = User(msg_dict.get(self.__KEY_FROM, {}))
        sent_to_user = User(msg_dict.get(self.__KEY_SENT_TO, {}))

        self.chat = Chat(msg_dict.get(self.__KEY_CHAT, {}))
        self.location = Location(msg_dict.get(self.__KEY_LOCATION, {}))
        self.contact = Contact(msg_dict.get(self.__KEY_CONTACT, {}))
        self.document = Document(msg_dict.get(self.__KEY_DOCUMENT, {}))
        self.photo = Photo(msg_dict.get(self.__KEY_PHOTO, {}))
        self.gif = Gif(msg_dict.get(self.__KEY_GIF, {}))
        self.voice = Voice(msg_dict.get(self.__KEY_VOICE, {}))
        self.video = Video(msg_dict.get(self.__KEY_VIDEO, {}))
        self.audio = Audio(msg_dict.get(self.__KEY_AUDIO, {}))
        self.article = Article(msg_dict.get(self.__KEY_ARTICLE, {}))
        self.sticker = Sticker(msg_dict.get(self.__KEY_STICKER, {}))
        self.text_file = TextFile(msg_dict.get(self.__KEY_TEXT_FILE, {}))
        self.text = str(msg_dict[self.__KEY_TEXT]) if self.__KEY_TEXT in msg_dict.keys() else None
        self.message_id = str(msg_dict[self.__KEY_MESSAGE_ID]) if self.__KEY_MESSAGE_ID in msg_dict.keys() else None
        self.date = int(str(msg_dict[self.__KEY_DATE])) if self.__KEY_DATE in msg_dict.keys() else None
        self.reference = int(str(msg_dict[self.__KEY_REFERENCE])) if self.__KEY_REFERENCE in msg_dict.keys() else None
        self.from_ = from_user
        self.sent_to = sent_to_user
        self.from_admin = int(msg_dict[self.__KEY_FROM_ADMIN]) if self.__KEY_FROM_ADMIN in msg_dict.keys() else None
        self.type = str(msg_dict[self.__KEY_TYPE]) if self.__KEY_TYPE in msg_dict.keys() else None
        self.caption = str(msg_dict[self.__KEY_CAPTION]) if self.__KEY_CAPTION in msg_dict.keys() else None
        self.url = str(msg_dict[self.__KEY_URL]) if self.__KEY_URL in msg_dict.keys() else None
        self.reply_to_message_id = str(msg_dict[self.__KEY_REPLY_TO_MESSAGE_ID]) if self.__KEY_REPLY_TO_MESSAGE_ID in msg_dict.keys() else None
        self.status = str(msg_dict[self.__KEY_STATUS]) if self.__KEY_STATUS in msg_dict.keys() else None
        self.chat_settings = int(msg_dict[self.__KEY_CHAT_SETTINGS]) if self.__KEY_CHAT_SETTINGS in msg_dict.keys() else None
        self.bg_color = str(msg_dict[self.__KEY_BG_COLOR]) if self.__KEY_BG_COLOR in msg_dict.keys() else None
        self.white_list_user = WhiteListUser(msg_dict.get(self.__KEY_WHITELIST_USER, {}))
        self.schedule_date = int(str(msg_dict[self.__KEY_SCHEDULE_DATE]))if self.__KEY_SCHEDULE_DATE in msg_dict.keys() else None
        self.app_id = dictionary[self.__KEY_APP_ID] if self.__KEY_APP_ID in dictionary.keys() else None
        self.tags= msg_dict[self.__KEY_TAGS] if self.__KEY_TAGS in msg_dict.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.type is not None:
            dictionary[self.__KEY_TYPE] = self.type
        if self.date is not None:
            dictionary[self.__KEY_DATE] = self.date
        if self.from_ is not None:
            _, from_dict = self.from_.to_json_obj()
            dictionary[self.__KEY_FROM] = from_dict
        if self.chat is not None:
            _, chat_dict = self.chat.to_json_obj()
            dictionary[self.__KEY_CHAT] = chat_dict
        if self.message_id is not None:
            dictionary[self.__KEY_MESSAGE_ID] = self.message_id
        if self.from_admin is not None:
            dictionary[self.__KEY_FROM_ADMIN] = self.from_admin
        if self.status is not None:
            dictionary[self.__KEY_STATUS] = self.status
        if self.sent_to is not None:
            _, sent_to_dict = self.sent_to.to_json_obj()
            dictionary[self.__KEY_SENT_TO] = sent_to_dict
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference
        if self.caption is not None:
            dictionary[self.__KEY_CAPTION] = self.caption
        if self.url is not None:
            dictionary[self.__KEY_URL] = self.url
        if self.reply_to_message_id is not None:
            dictionary[self.__KEY_REPLY_TO_MESSAGE_ID] = self.reply_to_message_id
        if self.text is not None:
            dictionary[self.__KEY_TEXT] = self.text
        if self.location is not None:
            _, location_dict = self.location.to_json_obj()
            dictionary[self.__KEY_LOCATION] = location_dict
        if self.contact is not None:
            _, contact_dict = self.contact.to_json_obj()
            dictionary[self.__KEY_CONTACT] = contact_dict
        if self.document is not None:
            _, document_dict = self.document.to_json_obj()
            dictionary[self.__KEY_DOCUMENT] = document_dict
        if self.photo is not None:
            _, photo_dict = self.photo.to_json_obj()
            dictionary[self.__KEY_PHOTO] = photo_dict
        if self.gif is not None:
            _, gif_dict = self.gif.to_json_obj()
            dictionary[self.__KEY_GIF] = gif_dict
        if self.voice is not None:
            _, voice_dict = self.voice.to_json_obj()
            dictionary[self.__KEY_VOICE] = voice_dict
        if self.video is not None:
            _, video_dict = self.video.to_json_obj()
            dictionary[self.__KEY_VIDEO] = video_dict
        if self.audio is not None:
            _, audio_dict = self.audio.to_json_obj()
            dictionary[self.__KEY_AUDIO] = audio_dict
        if self.article is not None:
            _, article_dict = self.article.to_json_obj()
            dictionary[self.__KEY_ARTICLE] = article_dict
        if self.sticker is not None:
            _, sticker_dict = self.sticker.to_json_obj()
            dictionary[self.__KEY_STICKER] = sticker_dict
        if self.text_file is not None:
            _, text_file_dict = self.text_file.to_json_obj()
            dictionary[self.__KEY_TEXT_FILE] = text_file_dict
        if self.bg_color is not None:
            dictionary[self.__KEY_BG_COLOR] = self.bg_color
        if self.white_list_user is not None:
            _, white_list_user_dict = self.white_list_user.to_json_obj()
            dictionary[self.__KEY_WHITELIST_USER] = white_list_user_dict
        if self.schedule_date is not None:
            dictionary[self.__KEY_SCHEDULE_DATE] = self.schedule_date
        if self.tags is not None:
            dictionary[self.__KEY_TAGS] = self.tags
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id
        logging.info("to " + str(dictionary))

        return json.dumps(dictionary), dictionary

    def is_msg_with_type(self, msg_type):
        return msg_type == self.type

    def is_video_msg(self):
        return self.is_msg_with_type("video")

    def is_text_msg(self):
        return self.is_msg_with_type("text")

    def is_photo_msg(self):
        return self.is_msg_with_type("photo")

    def is_audio_msg(self):
        return self.is_msg_with_type("audio")

    def is_location_msg(self):
        return self.is_msg_with_type("location")

    def is_voice_msg(self):
        return self.is_msg_with_type("voice")

    def is_gif_msg(self):
        return self.is_msg_with_type("gif")

    def is_sticker_msg(self):
        return self.is_msg_with_type("sticker")

    def is_text_file_msg(self):
        return self.is_msg_with_type("text_file")

    def is_document_msg(self):
        return self.is_msg_with_type("document")

    def is_contact_msg(self):
        return self.is_msg_with_type("contact")

    def is_article_msg(self):
        return self.is_msg_with_type("article")

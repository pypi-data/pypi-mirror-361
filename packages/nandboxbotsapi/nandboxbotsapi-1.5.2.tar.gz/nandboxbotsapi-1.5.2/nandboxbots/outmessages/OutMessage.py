import json


class OutMessage:
    WEB_PREVIEW_DISABLE = 1
    WEB_PREVIEW_HIDE_LINK = 2
    WEB_PREVIEW_INSTANCE_VIEW = 3
    WEB_PREVIEW_INSTANCE_WITHOUT_LINK = 4

    __KEY_METHOD = "method"
    __KEY_CHAT_ID = "chat_id"
    __KEY_REFERENCE = "reference"
    __KEY_TO_USER_ID = "to_user_id"
    __KEY_REPLAY_TO_MESSAGE_ID = "reply_to_message_id"
    __KEY_WEB_PAGE_PREVIEW = "web_page_preview"
    __KEY_DISABLE_NOTIFICATION = "disable_notification"
    __KEY_CAPTION = "caption"
    __KEY_ECHO = "echo"
    __KEY_MENU_REF = "menu_ref"
    __KEY_INLINE_MENU = "inline_menu"
    __KEY_CHAT_SETTINGS = "chat_settings"
    __KEY_STYLE = "style"
    __KEY_SCHEDULE_DATE = "schedule_date"
    __KEY_TAGS ="tags"
    __KEY_APP_ID = "app_id"


    method = None
    chat_id = None
    reference = None
    to_user_id = None
    reply_to_message_id = None
    web_page_preview = None
    disable_notification = None
    caption = None
    echo = None
    menu_ref = None
    inline_menus = None
    chat_settings = None
    schedule_date = None
    tags=None
    app_id = None


    def to_json_obj(self):
        obj = {}

        if self.method is not None:
            obj[self.__KEY_METHOD] = self.method
        if self.chat_id is not None:
            obj[self.__KEY_CHAT_ID] = self.chat_id
        if self.reference is not None:
            obj[self.__KEY_REFERENCE] = self.reference
        if self.to_user_id is not None:
            obj[self.__KEY_TO_USER_ID] = self.to_user_id
        if self.reply_to_message_id is not None:
            obj[self.__KEY_REPLAY_TO_MESSAGE_ID] = self.reply_to_message_id
        if self.web_page_preview is not None:
            obj[self.__KEY_WEB_PAGE_PREVIEW] = self.web_page_preview
        if self.disable_notification is not None:
            obj[self.__KEY_DISABLE_NOTIFICATION] = self.disable_notification
        if self.caption is not None:
            obj[self.__KEY_CAPTION] = self.caption
        if self.echo is not None:
            obj[self.__KEY_ECHO] = self.echo
        if self.menu_ref is not None:
            obj[self.__KEY_MENU_REF] = self.menu_ref
        if self.inline_menus is not None:
            obj[self.__KEY_INLINE_MENU] = self.inline_menus
        if self.chat_settings is not None:
            obj[self.__KEY_CHAT_SETTINGS] = self.chat_settings
        if self.schedule_date is not None:
            obj[self.__KEY_SCHEDULE_DATE] = self.schedule_date
        if self.tags is not None:
            obj[self.__KEY_TAGS] = self.tags
        if self.app_id is not None:
            obj[self.__KEY_APP_ID] = self.app_id

        return json.dumps(obj), obj

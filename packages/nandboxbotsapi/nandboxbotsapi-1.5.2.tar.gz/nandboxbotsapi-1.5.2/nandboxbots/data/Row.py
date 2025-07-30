# import json
#
# from nandboxbots.data.Button import Button
#
#
# class Row:
#     __KEY_BUTTONS = "buttons"
#     __KEY_ROW_ORDER = "row_order"
#
#     buttons = []
#     row_order = None
#
#     def __init__(self, *args):
#
#         if len(args) == 0:
#             return  # empty constructor
#         elif len(args) == 1:
#             if isinstance(args[0], Button):
#                 self.buttons.append(args[0])
#             elif isinstance(args[0], list):
#                 self.buttons = args[0]
#             elif isinstance(args[0], dict):
#                 dictionary = args[0]
#                 buttons_arr = dictionary[self.__KEY_BUTTONS] if self.__KEY_BUTTONS in dictionary.keys() else []
#                 self.buttons = []
#
#                 for i in range(len(buttons_arr)):
#                     _, btn_dict = Button(buttons_arr[i]).to_json_obj()
#                     self.buttons.append(btn_dict)
#
#                 self.row_order = dictionary[self.__KEY_ROW_ORDER] if self.__KEY_ROW_ORDER in dictionary.keys() else None
#
#     def to_json_obj(self):
#
#         dictionary = {}
#
#         if self.row_order is not None:
#             dictionary[self.__KEY_ROW_ORDER] = self.row_order
#         if self.buttons is not None:
#             buttons_arr = []
#             for i in range(len(self.buttons)):
#                 buttons_arr.append(self.buttons[i])
#             dictionary[self.__KEY_BUTTONS] = buttons_arr
#
#         return json.dumps(dictionary), dictionary

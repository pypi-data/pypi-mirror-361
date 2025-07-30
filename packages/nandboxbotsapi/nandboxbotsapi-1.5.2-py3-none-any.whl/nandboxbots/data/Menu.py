# import json
#
# from nandboxbots.data.Row import Row
#
#
# class Menu:
#     __KEY_MENU_REF = "menu_ref"
#     __KEY_ROWS = "rows"
#
#     menu_ref = None
#     rows = []
#
#     def __init__(self, dictionary=None):
#         if dictionary is None or dictionary == {}:
#             return
#
#         rows_arr = dictionary[self.__KEY_ROWS]
#         self.rows = []
#         for i in range(len(rows_arr)):
#             _, row_dict = Row(rows_arr[i]).to_json_obj()
#             self.rows.append(row_dict)
#         self.menu_ref = str(dictionary[self.__KEY_MENU_REF]) if self.__KEY_MENU_REF in dictionary.keys() else None
#
#     def to_json_obj(self):
#
#         dictionary = {}
#
#         if self.menu_ref is not None:
#             dictionary[self.__KEY_MENU_REF] = self.menu_ref
#         if self.rows is not None:
#             rows_arr = []
#             for i in range(len(self.rows)):
#                 rows_arr.append(self.rows[i])
#             dictionary[self.__KEY_ROWS] = rows_arr
#
#         return json.dumps(dictionary), dictionary

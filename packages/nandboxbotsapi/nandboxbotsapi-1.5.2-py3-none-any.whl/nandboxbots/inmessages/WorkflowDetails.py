import json

from nandboxbots.data.WorkflowCell import WorkflowCell


class WorkflowDetails:
    __KEY_WORKFLOW_DETAILS = "WorkflowDetails"
    __KEY_WORKFLOW_CELL = "WorkflowCell"

    __KEY_REFERENCE = "reference"
    __KEY_SCREEN_ID = "screen_id"
    __KEY_USER_ID = "user_id"
    __KEY_VAPP_ID = "vapp_id"
    __KEY_APP_ID = "app_id"

    workflowCell = []
    screenId = None
    userId = None
    vappId = None
    reference = None
    app_id = None

    def __init__(self, dictionary):
        workflow_details_dict = dictionary[
            self.__KEY_WORKFLOW_DETAILS] if self.__KEY_WORKFLOW_DETAILS in dictionary.keys() else {}
        workflow_cell_arr_obj = workflow_details_dict[
            self.__KEY_WORKFLOW_CELL] if self.__KEY_WORKFLOW_CELL in workflow_details_dict.keys() else None
        if workflow_cell_arr_obj is not None:
            length = len(workflow_cell_arr_obj)
            workflowCells = [WorkflowCell({})] * length
            for i in range(length):
                workflowCells[i] = WorkflowCell(workflow_cell_arr_obj[i])

            self.workflowCell = workflowCells
        self.userId = dictionary[self.__KEY_USER_ID] if self.__KEY_USER_ID in dictionary.keys() else None
        self.screenId = dictionary[self.__KEY_SCREEN_ID] if self.__KEY_SCREEN_ID in dictionary.keys() else None
        self.vappId = dictionary[self.__KEY_VAPP_ID] if self.__KEY_VAPP_ID in dictionary.keys() else None
        self.reference = dictionary[self.__KEY_REFERENCE] if self.__KEY_REFERENCE in dictionary.keys() else None
        self.app_id = dictionary[self.__KEY_APP_ID] if self.__KEY_APP_ID in dictionary.keys() else None

    def to_json_obj(self):
        dictionary = {}
        if self.workflowCell is not None:
            workflow_cell_arr = []
            for i in range(len(self.workflowCell)):
                workflow_cell_arr.append(self.workflowCell[i].to_json_obj())

            dictionary[self.__KEY_WORKFLOW_CELL] = workflow_cell_arr

        if self.userId is not None:
            dictionary[self.__KEY_USER_ID] = self.userId
        if self.screenId is not None:
            dictionary[self.__KEY_SCREEN_ID] = self.screenId
        if self.vappId is not None:
            dictionary[self.__KEY_VAPP_ID] = self.vappId
        if self.reference is not None:
            dictionary[self.__KEY_REFERENCE] = self.reference
        if self.app_id is not None:
            dictionary[self.__KEY_APP_ID] = self.app_id
        return json.dumps(dictionary), dictionary

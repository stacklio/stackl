from task import Task, logger

class DocumentTask(Task):

    @property
    def valid_subtasks(self):
        return [ 
        "PUT_DOCUMENT",    # PUT: Create or Update (Overwrite) the document
        "POST_DOCUMENT",  # POST: Create the document
        "DELETE_DOCUMENT"
        ] 

    def __init__(self, task_data):
        super(DocumentTask, self).__init__(task_data)

    def _load_json_object(self,json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'document_task'
        self.document = json_obj.get('document', None)   
        given_subtasks_list = json_obj.get('subtasks', [None])
        if all(subtasks in self.valid_subtasks for subtasks in given_subtasks_list):
            self.subtasks = given_subtasks_list
        else:
            logger.log("[DocumentTask] The given DocumentTask contains invalid subtasks")
            raise Exception("The given DocumentTasks contains invalid subtasks")

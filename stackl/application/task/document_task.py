from task import Task, logger

class DocumentTask(Task):
    @property
    def valid_subtypes(self):
        return [
            "GET_DOCUMENT",  # GET: To get a document
            "COLLECT_DOCUMENT",  # GET: To collect all documents of certain parameters
            "PUT_DOCUMENT",  # PUT: Create or update (overwrite) the document
            "POST_DOCUMENT",  # POST: Create the document
            "DELETE_DOCUMENT"
        ]

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'document_task'
        self.document = json_obj.get('document', None)
        subtype = json_obj.get('subtype', [None])
        if subtype in self.valid_subtypes:
            self.subtype = subtype
        else:
            logger.info(
                "[DocumentTask] The given DocumentTask has an invalid subtype")
            raise Exception("The given DocumentTask has an invalid subtype")

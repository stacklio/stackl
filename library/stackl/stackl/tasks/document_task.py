from typing import Any

from pydantic import validator

from .task import Task


class DocumentTask(Task):
    topic = "document_task"
    document: Any = None
    subtype: str = None

    @validator('subtype')
    def valid_subtypes(cls, subtype):
        subtypes = [
            "GET_DOCUMENT",  # GET: To get a document
            "COLLECT_DOCUMENT",  # GET: To collect all documents of certain parameters
            "PUT_DOCUMENT",  # PUT: Create or update (overwrite) the document
            "POST_DOCUMENT",  # POST: Create the document
            "DELETE_DOCUMENT"
        ]
        if subtype not in subtypes:
            raise ValueError("subtype for DocumentTask not valid")
        return subtype

import logging

from flask import request
from flask_restplus import Api
from flask_restplus import Resource

logger = logging.getLogger(__name__)
from task.request_task import RequestTask

api = Api(
    version='2',
    title='STACKL API',
    description='Swagger UI for STACKL',
    default='types',
    default_label='Operations related to STACKL types'
)


class StacklApiResource(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super(StacklApiResource, self).__init__(api, args, kwargs)
        logger.info("[StacklApiResource] API request received. Request environ: {0}".format(request.environ))
        self.request_task = RequestTask(request.environ)


# Ordering is important: internal dependencies are imported last
from api.document_api import api as document_api
from api.about_api import api as about_api
from api.stack_api import api as stack_api
from api.item_api import api as item_api
from api.user_api import api as user_api

# Ordering matters for display
api.add_namespace(document_api)
api.add_namespace(stack_api)
api.add_namespace(item_api)
api.add_namespace(about_api)
api.add_namespace(user_api)

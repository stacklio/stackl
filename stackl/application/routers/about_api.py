from flask_restplus import Namespace, Resource

from utils.general_utils import get_hostname

api = Namespace('about', description='Info about STACKL')


@api.route('', strict_slashes=False)
class About(Resource):
    def get(self):
        """Returns hostname of the REST API instance"""
        return get_hostname()

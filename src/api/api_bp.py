from flask import Blueprint
from flask_restful import Api

api_blueprint = Blueprint('api_blueprint', __name__)
api = Api(api_blueprint)

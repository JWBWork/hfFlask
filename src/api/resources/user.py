from src.logging import logger
from src.api import api
from src.database import User as db_User
from src.bcrypt import bcrypt
from flask import request
from flask_restful import Resource


class User(Resource):
	def get(self):
		auth_header = request.headers.get('Authorization')
		if auth_header:
			try:
				auth_token = auth_header.split(" ")[1]
			except IndexError:
				return {
					'status': 'fail',
					'message': 'Bearer token malformed'
				}, 401
			resp = db_User.decode_auth_token(auth_token)
			if isinstance(resp, str):
				return {
					'status': 'fail',
					'message': resp
				}, 401
			else:
				user = db_User.query.filter_by(id=resp).first()
				return {
					'status': 'success',
					'data': {
						'user_id': user.id,
						'email': user.email,
						'admin': user.admin,
						'registered_on': user.registered_on
					}
				}, 200
		else:
			return {
				'status': 'fail',
				'message': 'Invalid auth provided'
			}, 401


api.add_resource(User, '/user')
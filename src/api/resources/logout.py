from src.logging import logger
from src.api import api
from src.database import db, User, BlacklistToken
from src.bcrypt import bcrypt
from flask import request
from flask_restful import Resource


class Logout(Resource):
	def post(self):
		auth_header = request.headers.get('Authorization')
		if auth_header:
			auth_token = auth_header.split(" ")[1]
			resp = User.decode_auth_token(auth_token)
			if isinstance(resp, str):
				return {
					'status': 'fail',
					'message': resp
				}, 401
			else:
				blacklisted_token = BlacklistToken(token=auth_token)
				try:
					db.session.add(blacklisted_token)
					db.session.commit()
					return {
						'status': 'success',
						'message': 'Successfully logged out'
					}, 200
				except Exception as e:
					logger.error(e)
					return {
						'status': 'fail',
						'message': e
					}
		else:
			return {
				'status': 'fail',
				'message': 'Invalid auth provided'
			}, 401


api.add_resource(Logout, '/logout')

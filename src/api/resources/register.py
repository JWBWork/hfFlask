from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
from src.database import db, User


class Register(Resource):
	def post(self):
		data = request.json
		if data is None:
			return {
				'status': 'fail',
				'message': 'No data passed'
			}, 400

		try:
			user = User.query.filter_by(
				email=data.get('email'),
				username=data.get('username')
			)
			if user:
				return {
					'status': 'fail',
					'message': 'Username/Email Already exist!'
				}, 401
			user = User(
				email=data.get('email'),
				username=data.get('username'),
				password=data.get('password'),
			)
			db.session.add(user)
			db.session.commit()
			auth_token = user.encode_auth_token(user.id)
			return {
				'status': 'success',
				'message': 'Successfully registered',
				'auth_token': auth_token.decode()
			}, 201
		except Exception as e:
			logger.error(e)
			return {
				'status': 'fail',
				'message': 'An error has occurred',
			}, 401


api.add_resource(Register, '/login')


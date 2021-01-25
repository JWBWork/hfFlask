from src.logging import logger
from src.api import api
from src.database import User
from src.bcrypt import bcrypt
from flask import request
from flask_restful import Resource


class Login(Resource):
	def post(self):
		data = request.json
		logger.info(f'Login Post data {data} [{type(data)}]')
		if data is None:
			return {
				'status': 'fail',
				'message': 'No data passed'
			}, 400

		try:
			# user = User.query.filter_by(
			# 	email=data.get('email'),
			# 	username=data.get('username')
			# ).first()
			user = User.query.filter(
				(User.username == data.get('username')) | (User.email == data.get('email'))
			).first()
			logger.info(f'Login Post user query result: {user}')
			if user and bcrypt.check_password_hash(user.password, data.get('password')):
				auth_token = user.encode_auth_token(user.id)
				if auth_token:
					return {
						'status': 'success',
						'message': 'Success',
						'user': user.resp_dict(include_private=True),
						# 'user': user.resp_dict(),
						'auth_token': auth_token.decode()
					}, 200
			else:
				return {
					'status': 'fail',
					'message': 'Username or Password are invalid!'
				}, 401
		except Exception as e:
			logger.error(e)
			return {
				'status': 'fail',
				'message': 'An error has occurred',
			}, 401


api.add_resource(Login, '/login')


from src.logging import logger
from flask import request
from src.database import db, User


def authenticated(func):
	def authenticate(*args, **kwargs):
		auth_header = request.headers.get('Authorization')
		if auth_header:
			auth_token = auth_header.split(" ")[1]
			decode_response = User.decode_auth_token(auth_token)
			if isinstance(decode_response, str):
				return {
					'status': 'fail',
					'message': decode_response
				}, 401
			else:
				try:
					return func(*args, **kwargs)
				except Exception as e:
					return {
						'status': 'fail',
						'message': f'An error has occurred: {e}'
					}, 401
		else:
			return {
				'status': 'fail',
				'message': 'Invalid auth provided'
			}, 401
	return authenticate


def check_auth(request):
	auth_header = request.headers.get('Authorization')
	if auth_header:
		auth_token = auth_header.split(" ")[1]
		decode_response = User.decode_auth_token(auth_token)
		if isinstance(decode_response, str):
			return False
		else:
			return True
	else:
		return False

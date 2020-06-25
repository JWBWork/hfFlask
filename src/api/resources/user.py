from src.logging import logger
from src.api import api
from src.api.auth import check_auth, authenticated
from src.database import db, User as db_User
from src.bcrypt import bcrypt
from src.aws import s3
from flask import request
from flask_restful import Resource


class User(Resource):
	def get(self):
		authenticated = check_auth(request)
		try:
			data = dict(request.args)
			logger.info(f"User get data[{type(data)}]: {data}")
			user = db_User.query.filter_by(**data).first()
			if authenticated:
				# TODO: return more if authenticated
				return {
					'status': 'success',
					'user': user.resp_dict()
					# {
					# 	'id': user.id,
					# 	'username': user.username,
					# 	'email': user.email,
					# 	'admin': user.admin,
					# 	'bio': user.bio,
					# 	'created': str(user.created),
					# 	'avi_url': user.avi_url()
					# },
				}, 200
			else:
				return {
					'status': 'success',
					'user': user.resp_dict()
					# {
					# 	'id': user.id,
					# 	'username': user.username,
					# 	'email': user.email,
					# 	'admin': user.admin,
					# 	'bio': user.bio,
					# 	'created': str(user.created),
					# 	'avi_url': user.avi_url()
					# }
				}, 200
		except Exception as e:
			logger.error(e)
			return {
				'status': 'fail',
				'message': 'An error has occurred',
			}, 401

	@authenticated
	def post(self):
		data = request.form
		logger.info(f"/user post data[{type(data)}]: {data}")
		user = db_User.query.filter(
			db_User.id == data['userId']
		).first()
		if 'aviFile' in request.files.keys():
			avi_file = request.files['aviFile']
			avi_s3_name = f"user-{data['userId']}-avi"
			s3.upload_file(
				avi_file, s3.bucket_name,
				object_name=avi_s3_name
			)
			user.avi_s3_name = avi_s3_name
		if 'bio' in data.keys():
			user.bio = data["bio"]
		db.session.add(user)
		db.session.commit()
		return {
			'status': 'success',
			'message': 'profile updated',
			'user': user.resp_dict()
			# {
			# 	'id': user.id,
			# 	'username': user.username,
			# 	'email': user.email,
			# 	'admin': user.admin,
			# 	'bio': user.bio,
			# 	'created': str(user.created),
			# 	'avi_url': user.avi_url()
			# },
		}, 200


api.add_resource(User, '/user')

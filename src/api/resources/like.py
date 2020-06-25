from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
from src.database import db, Like as dbLike, User
from src.api.auth import authenticated


class Like(Resource):
	@authenticated
	def post(self):
		data = request.json
		logger.info(f"Like post data[{type(data)}]: {data}")
		like = dbLike.query.filter(
			dbLike.user_id == data['user_id'],
			dbLike.post_id == data['post_id'],
		).first()
		if not like:
			like = dbLike(
				user_id=data['user_id'],
				post_id=data['post_id'],
				value=data['value']
			)
		else:
			like.value = data['value']
		db.session.add(like)
		db.session.commit()
		return {
			'status': 'success',
			'message': 'post retrieved',
		}, 200


api.add_resource(Like, '/like')

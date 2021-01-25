from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
from src.database import db, UserFollow as dbUserFollow
from src.api.auth import authenticated


class UserFollow(Resource):
	@authenticated
	def post(self):
		data = request.json
		logger.info(f'User follow data: [{type(data)}]: {data}')
		if data['cmd'] == 'follow':
			follow = dbUserFollow.query.filter(
				dbUserFollow.follower_id == data['follower_id'],
				dbUserFollow.followed_id == data['followed_id'],
			).first()
			if not follow:
				follow = dbUserFollow(
					follower_id=data['follower_id'],
					followed_id=data['followed_id'],
				)
				db.session.add(follow)
		else:
			if data['cmd'] == 'unfollow':
				dbUserFollow.query.filter(
					dbUserFollow.follower_id == data['follower_id'],
					dbUserFollow.followed_id == data['followed_id'],
				).delete()
		db.session.commit()
		return {
			'status': 'success',
			'message': 'follow succesful'
		}, 200


api.add_resource(UserFollow, '/follow')

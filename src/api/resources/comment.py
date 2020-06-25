from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
from src.database import db, User, Post as dbPost, Comment as dbComment


class Comment(Resource):
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
				data = request.json
				logger.info(f"Comment post data[{type(data)}]: {data}")
				if data is None:
					return {
						'status': 'fail',
						'message': 'No data passed'
					}, 400
				else:
					try:
						post_id = data['postId']
						author_id = data['authorId']
						comment = data['comment']
						post = dbPost.query.filter(
							dbPost.id == post_id
						).first()
						new_comment = dbComment(
							post_id=post_id,
							author_id=author_id,
							body=comment
						)
						post.comments.append(new_comment)
						db.session.add(new_comment)
						db.session.add(post)
						db.session.commit()
						return {
							'status': 'success',
							'message': 'comment submitted',
						}, 200
					except Exception as e:
						logger.error(e)
						return {
							'status': 'fail',
							'message': 'An error has occurred',
						}, 401
		else:
			return {
				'status': 'fail',
				'message': 'Invalid auth provided'
			}, 401


api.add_resource(Comment, '/comment')

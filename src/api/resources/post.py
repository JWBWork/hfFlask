from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
import uuid
import json
from src.database import db, Post as dbPost, Tag as dbTag, User as dbUser, UserFollow as dbUserFollow
from src.aws import s3


class Post(Resource):
	"""
	Peoples art that they post to their pages
	"""
	def post(self):
		data = request.form
		logger.info(f"Post post data[{type(data)}]: {data}")
		user_id = data['user_id']
		s3_name = f"{user_id}-{data['title'].replace(' ', '-')}-{str(uuid.uuid4().hex)}.png"
		image_file = request.files['image']
		# TODO: remove and change image upload to frontend?
		#  Will have to deal with cloudfront at some point anyways...
		s3.upload_file(
			image_file, s3.bucket_name,
			object_name=s3_name
		)
		# s3_url = f"https://{s3.bucket_name}.s3.amazonaws.com/{s3_name}"
		post = dbPost(
			author_id=user_id,
			title=data['title'],
			desc=data.get('description'),
			s3_name=s3_name,
			# s3_url=s3_url
		)
		db.session.add(post)
		tags = request.form['tags'].split(',')
		for tag in tags:
			db_tag = dbTag.query.filter(
				dbTag.name == tag
			).first()
			if not db_tag:
				db_tag = dbTag(name=tag)
			post.tags.append(db_tag)
			db.session.add(db_tag)
		db.session.commit()
		return {
			'status': 'success',
			'message': 'post uploaded',
			# TODO: implement to json function in post database class
			'post': post.resp_dict()
		}, 200

	def get(self):
		data = request.args
		logger.info(f"Post get data[{type(data)}]: {data}")
		try:
			if 'id' in data:
				logger.info('REQUEST BY ID')
				posts = [dbPost.query.get(data['id']),]
			elif 'feed' in data:
				feed_query = json.loads(data['feed'])
				posts = [post for _, post in dbUserFollow.query.filter(
					dbUserFollow.follower_id == feed_query['userId']
				).join(
					dbPost, dbUserFollow.followed_id == dbPost.author_id
				).add_entity(
					dbPost
				).all()]
			else:
				posts = dbPost.query.join(
					dbUser, dbUser.id == dbPost.author_id
				).filter_by(
					# **{'id': data.get('id')}
				).add_entity(
					dbUser
				)
				if data:
					posts = posts.filter_by(
						**{'id': data.get('author_id')}
					)
				posts = [post for post, user in posts.all()]
			posts = [post.resp_dict() for post in posts]
			return {
				'status': 'success',
				'message': 'post retrieved',
				'posts': posts
			}, 200
		except Exception as e:
			logger.error(e)
			return {
					'status': 'fail',
					'message': 'An error has occurred',
				}, 401


api.add_resource(Post, '/post')

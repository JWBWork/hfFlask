from src.logging import logger
from src.api import api
from src.database import db, Post as dbPost, User as dbUser, Tag as dbTag
from flask import request
from flask_restful import Resource
from sqlalchemy import or_
import re


class Search(Resource):
	def get(self):
		query = dict(request.args)['searchQuery']
		split_query = query.split()
		tags = [w.replace('#', '') for w in split_query if w.startswith('#')]
		usernames = [w.replace('@', '') for w in split_query if w.startswith('@')]
		terms = [r.strip() for r in ' '.join(
			[w for w in split_query if not (w.startswith('@') or w.startswith('#'))]
		).split(',') if r.strip()]
		posts = []
		for term in terms:
			logger.warning(f'term: {term}')
			term_posts = dbPost.query.filter(or_(
				dbPost.title.like(f'%{term}%'),
				dbPost.desc.like(f'%{term}%')
			)).all()
			posts += [post.resp_dict() for post in term_posts]
		for tag in tags:
			logger.warning(f'tag: {tag}')
			tag_posts = dbPost.query.filter(dbPost.tags.any(
				dbTag.name == tag
			)).all()
			posts += [post.resp_dict() for post in tag_posts]
		for username in usernames:
			logger.warning(f'username: {username}')
			user_posts = dbPost.query.join(
				dbUser, dbPost.author_id == dbUser.id
			).add_columns(dbUser.username).filter(
				dbUser.username == username
			).all()
			posts += [post.resp_dict() for post, _ in user_posts]
		return {
			'status': 'success',
			'posts': posts
		}, 200


api.add_resource(Search, '/search')


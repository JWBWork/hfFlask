from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
from src.database import db, Tag as dbTag


class Tag(Resource):
	def get(self):
		data = request.args
		print(f'TAG GET DATA: {data}')
		tags = dbTag.query.filter(
			dbTag.name.like(f'%{data["text"]}%')
		).all()
		print(tags)
		return {
			'status': 'success',
			'tags': [tag.name for tag in tags]
		}, 200


api.add_resource(Tag, '/tag')

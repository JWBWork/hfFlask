from src.aws import s3
from src.api import api
from flask import request
from flask_restful import Resource
from pprint import pprint


class Image(Resource):
	def post(self):
		title = request.form['title']
		tags = request.form['tags'].split(',')
		image_file = request.files['image']
		pprint([title, tags, image_file])
		# Todo: upload object_name with random variable and upload
		s3.upload_file(
			image_file, 'jwbwork-dev',
			object_name=f"{title}-{image_file.filename}"
		)
		return {
			'status': 200,
			'body': ';)'
		}

	def get(self):
		return {
			'status': 200,
			'body': ';)'
		}


api.add_resource(Image, '/image')


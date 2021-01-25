from src.logging import logger
from src.api import api
from flask import request
from flask_restful import Resource
from datetime import datetime
# from src.database import db, Message as dbMessage, MessageMap as dbMessageMap, User as dbUser
from src.api.auth import authenticated

# TODO: mocking messages to sockets, any of this used anywhere?
class Message(Resource):
	@authenticated
	def post(self):
		pass
		# data = request.json
		# logger.info(f'Message post data [{type(data)}]: {data}')
		# py_datetime = datetime.strptime(data['timestamp'], "%a, %d %b %Y %H:%M:%S %Z")
		# msg = dbMessage(
		# 	body=data['body'],
		# 	timestamp=py_datetime
		# )
		# db.session.add(msg)
		# msg_map = dbMessageMap(
		# 	message_id=msg.id,
		# 	from_id=data['from_id'],
		# 	to_id=data['to_id']
		# )
		# db.session.add(msg_map)
		# db.session.commit()
		# return {
		# 	'status': 'success',
		# 	'message': 'message saved'
		# }

	@authenticated
	def get(self):
		pass
		# data = request.args
		# logger.info(f'Messages get data[{type(data)}]: {data}')
		# from_messages = db.aliased(dbMessage)
		# to_messages = db.aliased(dbMessage)
		# from_user = db.aliased(dbUser)
		# to_user = db.aliased(dbUser)
		# maps = dbMessageMap.query.filter(
		# 	dbMessageMap.from_id == data['from_id']
		# ).join(
		# 	from_messages, from_messages.id == dbMessageMap.message_id
		# ).add_entity(from_messages).join(
		# 	to_messages, to_messages.id == dbMessageMap.message_id
		# ).add_entity(to_messages).join(
		# 	from_user, from_user.id == dbMessageMap.from_id
		# ).add_entity(from_user).join(
		# 	to_user, to_user.id == dbMessageMap.to_id
		# ).add_entity(to_user).all()
		# if maps:
		# 	logger.info('Got maps to convert!')
		# 	# convert to serializable
		# 	pass
		# return {
		# 	'status': 'success',
		# 	'messages': maps
		# }, 200


api.add_resource(Message, '/message')

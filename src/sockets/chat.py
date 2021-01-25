from src.logging import logger
from . import socketio
from flask_socketio import emit, join_room, leave_room
from src.database import db, User as dbUser, Chat as dbChat, Message as dbMessage
from flask import request
import datetime

CHAT_NAMESPACE = '/socket'


@socketio.on('auth', namespace=CHAT_NAMESPACE)
def user_auth(data):
	logger.warning(f'User {data["userId"]} attempting auth')
	decode_response = dbUser.decode_auth_token(data["authToken"])
	ip = request.remote_addr
	join_room(ip)
	if data["userId"] == decode_response:
		logger.warning('AUTHENTICATED :D')
		user = dbUser.query.filter(
			dbUser.id == decode_response
		).first()
		if user:
			for chat in user.chats:
				join_room(chat.room_name)
			user.last_ip = ip
			db.session.add(user)
			db.session.commit()
		emit('user_connected', {
			'message': 'connected',
			'chats': [chat.resp_dict(exceptID=decode_response) for chat in user.chats],
		}, room=ip)
	else:
		emit('reject', {'message': 'Please log back in!'}, room=ip)
		logger.warning('NOT AUTHENTICATED >:(')
		return False


@socketio.on('open_room', namespace=CHAT_NAMESPACE)
def open_room(data):
	logger.warning(f'Open room: {data}')
	uids = data['userIds']
	uids.sort()
	logger.warning(f'uids: {uids}')
	room_name = ''.join(str(uid) for uid in uids)
	chat = dbChat.query.filter(
		dbChat.room_name==room_name
	).first()
	if not chat:
		chat = dbChat(
			room_name=room_name
		)
	db.session.add(chat)
	user_dicts, user_ips = [], []
	for id in uids:
		user = dbUser.query.filter(
			dbUser.id == id
		).first()
		user_dicts.append(user.resp_dict(follows=False))
		user.chats.append(chat)
		user_ips.append(user.last_ip)
		db.session.add(user)
	db.session.commit()
	join_room(room_name)
	ip = request.remote_addr
	user_ips.append(ip)
	ips = set(user_ips)
	for ip in ips:
		if ip:
			emit('room_opened', {
				'chat': chat.resp_dict(exceptID=data['fromId'])
			}, room=ip)


@socketio.on('message', namespace=CHAT_NAMESPACE)
def message(data):
	logger.warning(f'new message data! {data}')
	message = dbMessage(
		body=data['body'],
		timestamp=datetime.datetime.fromtimestamp(data['timestamp']/1e3),
		author_id=data['authorId']
	)
	db.session.add(message)
	chat = dbChat.query.filter(
		dbChat.room_name == data['roomName']
	).first()
	if chat:
		chat.messages.append(message)
		db.session.add(chat)
	db.session.commit()
	emit('message', data, room=data['roomName'])


@socketio.on('disconnect', namespace=CHAT_NAMESPACE)
def user_disconnect():
	print('CLIENT DISCONNNECT')



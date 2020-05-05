from src.database import db
from src.bcrypt import bcrypt
from flask import current_app
from datetime import datetime, timedelta
import jwt


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(25), unique=True, nullable=False)
	username = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	created = db.Column(db.DateTime, nullable=False)
	admin = db.Column(db.Boolean, nullable=False, default=False)

	def __init__(self, email, username, password, admin=False):
		self.email = email
		self.username = username
		self.password = bcrypt.generate_password_hash(
			password, current_app.config.get('BCRYPT_LOG_ROUNDS')
		).decode()
		self.created = datetime.utcnow()
		self.admin = admin

	def encode_auth_token(self, user_id):
		try:
			payload = {
				'exp': datetime.utcnow() + timedelta(days=0, seconds=10),
				'iat': datetime.utcnow(),
				'sub': user_id
			}
			return jwt.encode(
				payload, current_app.get('SECRET_KEY'), algorithm='HS256'
			)
		except Exception as e:
			return e

	@staticmethod
	def decode_auth_token(auth_token):
		try:
			payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
			is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
			if is_blacklisted_token:
				return "Token is blacklisted - please log in again"
			else:
				return payload['sub']
		except jwt.ExpiredSignatureError:
			return 'Signiture expired. Please log in again.'
		except jwt.InvalidTokenError:
			return 'Invalid token. Please log in again.'


class BlacklistToken(db.Model):
	__tablename__ = 'blacklist_tokens'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	token = db.Column(db.String(500), unique=True, nullable=False)
	blacklisted_on = db.Column(db.DateTime, nullable=False)

	def __init__(self, token):
		self.token = token
		self.blacklisted_on = datetime.utcnow()

	def __repr__(self):
		return f'<BlacklistToken id: {self.id} token: {self.token}>'

	@staticmethod
	def check_blacklist(auth_token):
		res = BlacklistToken.query.filter_by(
			token=str(auth_token)
		).first()
		return True if res else False


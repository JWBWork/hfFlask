from src.database import db
from src.bcrypt import bcrypt
from src.aws import s3
from flask import current_app
from datetime import datetime, timedelta
import jwt
import json


class User(db.Model):
	# __tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(25), unique=True, nullable=False)
	username = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	created = db.Column(db.DateTime, nullable=False)
	admin = db.Column(db.Boolean, nullable=False, default=False)
	posts = db.relationship('Post', backref='author', lazy=True)
	comments = db.relationship('Comment', backref='author', lazy=True)
	likes = db.relationship('Like', backref='user', lazy=True)
	bio = db.Column(db.Text, nullable=True)
	avi_s3_name = db.Column(db.String, unique=True, nullable=True)

	def __init__(self, email, username, password, admin=False):
		self.email = email
		self.username = username
		self.password = bcrypt.generate_password_hash(
			password, current_app.config.get('BCRYPT_LOG_ROUNDS')
		).decode()
		self.created = datetime.utcnow()
		self.admin = admin

	def __repr__(self):
		return f"<User id: {self.id} username: '{self.username}'"

	def avi_url(self):
		url = f"https://{s3.bucket_name}.s3.amazonaws.com/{self.avi_s3_name}" if self.avi_s3_name else None
		return url

	def resp_dict(self):
		return {
			'id': self.id,
			'username': self.username,
			'created': str(self.created),
			'bio': self.bio,
			'avi': self.avi_url()
		}

	def encode_auth_token(self, user_id):
		try:
			payload = {
				'exp': datetime.utcnow() + timedelta(days=0, minutes=30, seconds=0),
				'iat': datetime.utcnow(),
				'sub': user_id
			}
			return jwt.encode(
				payload, current_app.config.get('SECRET_KEY'), algorithm='HS256'
			)
		except Exception as e:
			raise e

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


class UserFollow(db.Model):
	pass


tags = db.Table(
	'tags',
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
	db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)


class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String, nullable=False)

	def __repr__(self):
		return f"<Tag id:{self.id} name:{self.name}>"


class Post(db.Model):
	# __tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	comments = db.relationship('Comment', backref='Post', lazy=True)
	likes = db.relationship('Like', backref='Post', lazy=True)
	tags = db.relationship(
		'Tag', secondary=tags, lazy='subquery',
		backref=db.backref('posts', lazy=True),
	)
	title = db.Column(db.String, unique=False)
	desc = db.Column(db.Text, unique=False)  # TODO:Check limit and create character limit?
	s3_name = db.Column(db.String, unique=True, nullable=False)
	# TODO replace this with a method to return url with s3 name?
	s3_url = db.Column(db.String, unique=True, nullable=False)

	def resp_dict(self):
		get_user = lambda id: User.query.get(id)
		post_author = User.query.get(self.author_id)
		return {
			'id': self.id,
			'title': self.title,
			'author_id': self.author_id,
			's3_url': self.s3_url,
			'description': self.desc,
			'author_username': post_author.username,
			'author_avi': post_author.avi_url(),
			'comments': [
				{
					'body': comment.body,
					'author_id': comment.author_id,
					'avi': get_user(comment.author_id).avi_url(),
					'username': get_user(comment.author_id).username,
				} for comment in self.comments
			],
			'likes': [
				{
					'value': like.value,
					'user_id': like.user_id,
					'avi': get_user(like.user_id).avi_url(),
					'username': get_user(like.user_id).username
				} for like in self.likes
			]
		}


class Comment(db.Model):
	# __tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	body = db.Column(db.Text)  # TODO:Check limit and create character limit?


class BlacklistToken(db.Model):
	# __tablename__ = 'blacklist_tokens'
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


class Like(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	value = db.Column(db.Boolean, nullable=True)

	def __repr__(self):
		return f"<Like id:{self.id} user_id:{self.user_id} value:{self.value}>"

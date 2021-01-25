import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from src.logging import logger
from pprint import pformat, pprint

bucket_name = 'jwbwork-dev'

def create_bucket(bucket_name, region=None):
	"""Create an S3 bucket in a specified region

	If a region is not specified, the bucket is created in the S3 default
	region (us-east-1).

	:param bucket_name: Bucket to create
	:param region: String region to create bucket in, e.g., 'us-west-2'
	:return: True if bucket created, else False
	"""

	# Create bucket
	try:
		if region is None:
			s3_client = boto3.client('s3')
			s3_client.create_bucket(Bucket=bucket_name)
		else:
			s3_client = boto3.client('s3', region_name=region)
			location = {'LocationConstraint': region}
			s3_client.create_bucket(Bucket=bucket_name,
									CreateBucketConfiguration=location)
	except ClientError as e:
		logger.error(e)
		return False
	return True


def upload_file(file, bucket_name, object_name):
	# f = file.read()
	# s3 = boto3.client('s3')
	# s3.upload_fileobj(file, bucket_name, object_name)
	config = TransferConfig()
	config.use_threads = False
	s3 = boto3.resource('s3')
	bucket = s3.Bucket(bucket_name)
	bucket.upload_fileobj(file, object_name, Config=config)


def delete_file(bucket_name, file_key):
	s3 = boto3.resource('s3')
	s3.Object(bucket_name, file_key).delete()


def bucket_files(bucket_name):
	s3 = boto3.resource('s3')
	my_bucket = s3.Bucket(bucket_name)
	return my_bucket.objects.all()


def bucket_file_urls(bucket_name):
	files = bucket_files(bucket_name)
	s3 = boto3.client('s3')
	gen_url = lambda key: s3.generate_presigned_url(
		'get_object',
		Params={
			'Bucket': bucket_name,
			'Key': key,
		},
		ExpiresIn=3600
	)
	urls = [gen_url(file.key) for file in files]
	return urls


def bucket_file_url(bucket_name, file_key):
	s3 = boto3.client('s3')
	url = s3.generate_presigned_url(
		'get_object',
		Params={
			'Bucket': bucket_name,
			'Key': file_key,
		},
		ExpiresIn=3600
	)
	return url


def test():
	bucket_name = 'jwbwork-dev'
	urls = bucket_file_urls(bucket_name)
	print(urls)


if __name__ == '__main__':
	test()

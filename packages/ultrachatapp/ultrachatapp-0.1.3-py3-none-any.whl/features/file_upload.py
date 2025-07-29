# File uploads  
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

class S3Uploader:
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket_name: str, region: str = "us-east-1"):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.bucket_name = bucket_name
    
    def upload_file(self, file_path: str, s3_key: str) -> str:
        """Uploads a file to S3 and returns its URL"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            file_url = f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{s3_key}"
            print(f"File {file_path} uploaded to {file_url}")
            return file_url
        except FileNotFoundError:
            print("The file was not found")
            return ""
        except NoCredentialsError:
            print("Credentials not available")
            return ""
        except ClientError as e:
            print(f"Client error: {e}")
            return ""

    def upload_file_object(self, file_obj, s3_key: str, content_type: str = "application/octet-stream") -> str:
        """Uploads a file-like object to S3 and returns its URL"""
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_key, ExtraArgs={"ContentType": content_type})
            file_url = f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{s3_key}"
            print(f"File uploaded to {file_url}")
            return file_url
        except NoCredentialsError:
            print("Credentials not available")
            return ""
        except ClientError as e:
            print(f"Client error: {e}")
            return ""

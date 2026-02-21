import boto3
import os
from .storage import StorageProvider


class S3Storage(StorageProvider):

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET")
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )

    def upload(self, file_data: bytes, filename: str, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=file_data,
            ContentType=content_type,
        )

        return f"https://{self.bucket}.s3.amazonaws.com/{filename}"

    def delete(self, filename: str) -> None:
        self.client.delete_object(
            Bucket=self.bucket,
            Key=filename,
        )

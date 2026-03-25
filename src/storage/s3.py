import boto3
from botocore.exceptions import NoCredentialsError


# LocalStack S3 endpoint (for local testing)
S3_ENDPOINT = "http://localhost:4566"
S3_BUCKET_NAME = "book-pipeline-bucket"


def create_s3_client():
   return boto3.client(
       's3',
       endpoint_url=S3_ENDPOINT,  # LocalStack endpoint
       aws_access_key_id='test', 
       aws_secret_access_key='test', 
   )


def upload_file_to_s3(file_path, file_name):
   s3 = create_s3_client()
  
   try:
       s3.upload_file(file_path, S3_BUCKET_NAME, file_name)
       print(f"Successfully uploaded {file_name} to {S3_BUCKET_NAME}")
   except FileNotFoundError:
       print(f"The file {file_path} was not found.")
   except NoCredentialsError:
       print("Credentials not available.")


# Example usage
if __name__ == "__main__":
   file_path = "data/raw/api/books_page_1.json"
   file_name = "books_page_1.json"  # The name to use in S3 bucket


   upload_file_to_s3(file_path, file_name)
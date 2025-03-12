import os
from dotenv import load_dotenv
import boto3
import json
from botocore.exceptions import ClientError

if not os.getenv("APP_ENV"):
    load_dotenv()

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")

    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

else:
    secret_name = "secret/ticketing/user"
    region_name = "ap-northeast-2"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    
    secret_data = json.loads(secret)

    JWT_SECRET_KEY = secret_data["JWT_SECRET_KEY"]
    JWT_ALGORITHM = secret_data["JWT_ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_MINUTES = secret_data["ACCESS_TOKEN_EXPIRE_MINUTES"]

    REDIS_HOST = secret_data["REDIS_HOST"]
    REDIS_PORT = secret_data["REDIS_PORT"]

    db_secret_name = "secret/ticketing/rds"  # DB용 보안 암호 이름
    
    try:
        db_secret_response = client.get_secret_value(
            SecretId=db_secret_name
        )
    except ClientError as e:
        raise e
    
    db_secret = db_secret_response['SecretString']
    db_secret_data = json.loads(db_secret)
    
    # DB 관련 정보 설정
    DB_USER = db_secret_data["username"]
    DB_PASS = db_secret_data["password"]
    DB_HOST = db_secret_data["host"]
    DB_NAME = db_secret_data["dbInstanceIdentifier"]
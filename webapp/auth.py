import os
import json
import boto3
from fastapi import HTTPException, Request

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
APP_SECRET_ID = os.environ.get("APP_SECRET_ID")


def load_token():
    if "APP_BEARER_TOKEN" in os.environ:
        return os.environ["APP_BEARER_TOKEN"]

    if APP_SECRET_ID:
        sm = boto3.client("secretsmanager", region_name=AWS_REGION)
        resp = sm.get_secret_value(SecretId=APP_SECRET_ID)
        data = json.loads(resp["SecretString"])
        return data.get("bearer_token")

    raise RuntimeError("Bearer token not found")


BEARER_TOKEN = load_token()


def require_token(request: Request):
    # Check Authorization header: "Bearer <token>"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        if token == BEARER_TOKEN:
            return

    # Fallback to cookie
    cookie_token = request.cookies.get("auth_token")
    if cookie_token and cookie_token == BEARER_TOKEN:
        return

    raise HTTPException(status_code=401, detail="Unauthorized")
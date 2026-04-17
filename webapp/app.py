from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import boto3
import uuid
import os

app = FastAPI(
    title="Three-Tier Demo App",
    description="Designed and Deployed by Moges K",
    version="1.0.0"
)


# Auth (Swagger Authorize button)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SAMPLE_TOKEN = "sample-token-123"

def verify_token(token: str = Depends(oauth2_scheme)):
    if token != SAMPLE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    return token

@app.post("/token")
def generate_token():
    return {"access_token": SAMPLE_TOKEN, "token_type": "bearer"}


# AWS Setup

AWS_REGION = os.getenv("AWS_REGION")
UPLOADS_BUCKET = os.getenv("UPLOADS_BUCKET")
METADATA_TABLE = os.getenv("METADATA_TABLE")

s3 = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(METADATA_TABLE)


# Upload File → S3 + DynamoDB

@app.post("/upload-file")
def upload_file(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    file_id = str(uuid.uuid4())
    key = f"uploads/{file_id}-{file.filename}"

    # Upload to S3
    s3.upload_fileobj(file.file, UPLOADS_BUCKET, key)

    # Store metadata
    item = {
        "id": file_id,
        "filename": file.filename,
        "s3_key": key,
    }
    table.put_item(Item=item)

    return {"message": "File uploaded", "id": file_id, "s3_key": key}


# List Items

@app.get("/items")
def list_items(token: str = Depends(verify_token)):
    response = table.scan()
    return response.get("Items", [])


# Get Single Item

@app.get("/items/{item_id}")
def get_item(item_id: str, token: str = Depends(verify_token)):
    response = table.get_item(Key={"id": item_id})
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Item not found")
    return response["Item"]


# Health Check

@app.get("/health")
def health():
    return {
        "message": "Hi all Evangadi Team, this FastAPI app is working fine.",
        "status": "ok"
    }
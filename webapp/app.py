import os
import uuid
import datetime
import boto3

from fastapi import FastAPI, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import require_token

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
UPLOADS_BUCKET = os.environ.get("UPLOADS_BUCKET")
METADATA_TABLE = os.environ.get("METADATA_TABLE")

session = boto3.Session(region_name=AWS_REGION)
s3 = session.client("s3")
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(METADATA_TABLE)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, token: str = Form(...)):
    # Simple login: token must match bearer token
    from auth import BEARER_TOKEN

    if token != BEARER_TOKEN:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid token"},
        )
    response = RedirectResponse(url="/upload", status_code=302)
    response.set_cookie("auth_token", token, httponly=True)
    return response


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, _=Depends(require_token)):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
def upload_file(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    _=Depends(require_token),
):
    item_id = str(uuid.uuid4())
    s3_key = f"uploads/{item_id}/{file.filename}"

    s3.upload_fileobj(file.file, UPLOADS_BUCKET, s3_key)

    table.put_item(
        Item={
            "id": item_id,
            "name": name,
            "description": description,
            "filename": file.filename,
            "s3_key": s3_key,
            "bucket": UPLOADS_BUCKET,
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
        }
    )

    return RedirectResponse("/items", status_code=302)


@app.get("/items", response_class=HTMLResponse)
def list_items(request: Request, _=Depends(require_token)):
    resp = table.scan()
    items = resp.get("Items", [])
    items.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

    return templates.TemplateResponse(
        "items.html",
        {"request": request, "items": items},
    )
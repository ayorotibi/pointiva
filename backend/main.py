import json
import shutil
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

from fastapi import (
    FastAPI, 
    UploadFile, 
    File, 
    Form, 
    HTTPException, 
    status,
    Depends 
)

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from schemas import (
    DashboardResponse,
    Wallet,
    Upload,
    UploadCreateResponse,
    UploadStatusResponse,
    FeaturedMoment
)

from fake_db import (
    FAKE_USER,
    FAKE_WALLET,
    FAKE_FEATURED,
    create_upload,
    get_upload,
    list_uploads_for_user,
    UPLOADS
)

import threading
import time

def simulate_moderation(upload_id):
    time.sleep(3)  # simulate processing
    upload = get_upload(upload_id)
    if upload:
        upload["status"] = "approved"

def require_admin(user: dict):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


app = FastAPI(title="Pointiva Demo Backend")

@app.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(current_user: dict = Depends(get_current_user)):
    return DashboardResponse(
        user=FAKE_USER,
        wallet=Wallet(**FAKE_WALLET),
        uploads=[Upload(**u) for u in UPLOADS],
        featured=[FeaturedMoment(**f) for f in FAKE_FEATURED]
    )


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
        "full_name": user.get("full_name", user["username"])
    }


# POST/Upload Accept file + save it
@app.post("/upload", response_model=UploadCreateResponse)
async def upload_file(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    metadata_dict = json.loads(metadata)

    file_location = f"storage/uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Attach username to upload
    upload = create_upload(file.filename, current_user["username"])
    upload["metadata"] = metadata_dict

    threading.Thread(target=simulate_moderation, args=(upload["id"],)).start()

    return UploadCreateResponse(
        id=upload["id"],
        status=upload["status"],
        filename=file.filename
    )



#GET/Upload/{id} - Check Status
@app.get("/upload/{upload_id}", response_model=UploadStatusResponse)
def check_upload(upload_id: int):
    upload = get_upload(upload_id)
    if not upload:
        return {"id": upload_id, "status": "not_found", "message": "Upload does not exist"}

    return UploadStatusResponse(
        id=upload["id"],
        status=upload["status"],
        submitted=upload["submitted"]
    )


# GET/Uploads - List all uploads
@app.get("/uploads", response_model=List[Upload])
def list_uploads(current_user: dict = Depends(get_current_user)):
    user_uploads = list_uploads_for_user(current_user["username"])
    return [Upload(**u) for u in user_uploads]

# admin endpoint to list ALL uploads
@app.get("/admin/uploads", response_model=List[Upload])
def admin_list_uploads(current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    return [Upload(**u) for u in UPLOADS]

# approve endpoints
@app.post("/admin/approve/{upload_id}")
def admin_approve(upload_id: int, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    upload = get_upload(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    upload["status"] = "approved"
    return {"message": "Upload approved", "id": upload_id}

# reject endpoints
@app.post("/admin/reject/{upload_id}")
def admin_reject(upload_id: int, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    upload = get_upload(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    upload["status"] = "rejected"
    return {"message": "Upload rejected", "id": upload_id}



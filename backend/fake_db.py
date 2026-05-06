import time

FAKE_USER = {
    "id": 1,
    "display_name": "Ayo",
    "username": "ayo_creator",
    "city": "Penarth",
    "role": "admin"
}

FAKE_WALLET = {
    "available_points": 1240,
    "pending_points": 300,
    "lifetime_earnings": 25000
}

FAKE_FEATURED = [
    {"id": 99, "title": "Campus Life Moment", "creator": "Sam", "location": "Cardiff"}
]

# SINGLE SOURCE OF TRUTH
UPLOADS = []
UPLOAD_COUNTER = 1

def create_upload(filename, username):
    global UPLOAD_COUNTER
    upload = {
        "id": UPLOAD_COUNTER,
        "filename": filename,
        "status": "submitted",
        "submitted": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": {},
        "user": username
    }
    UPLOADS.append(upload)
    UPLOAD_COUNTER += 1
    return upload

def get_upload(upload_id):
    return next((u for u in UPLOADS if u["id"] == upload_id), None)

def list_uploads_for_user(username):
    return [u for u in UPLOADS if u["user"] == username]

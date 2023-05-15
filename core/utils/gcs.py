import mimetypes
import time

import requests
from google.cloud import storage
from google.oauth2.service_account import Credentials

from core.config import config

creds_dict = {
    "type": "service_account",
    "project_id": config.GOOGLE_PROJECT_ID,
    "private_key_id": config.GOOGLE_PRIVATE_KEY_ID,
    "private_key": config.GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
    "client_email": config.GOOGLE_CLIENT_EMAIL,
    "client_id": config.GOOGLE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{config.GOOGLE_CLIENT_EMAIL_ID}%40{config.GOOGLE_PROJECT_ID}.iam.gserviceaccount.com",
}
creds = Credentials.from_service_account_info(info=creds_dict)


class GCStorage:
    def __init__(self):
        self.client = storage.Client(credentials=creds)
        self.bucket = self.client.get_bucket(config.GCS_BUCKET_NAME)

    def upload_file(self, file, path):
        type, _ = mimetypes.guess_type(file.filename)
        file_path = path + str(int(time.time())) + "-" + file.filename
        blob = self.bucket.blob(file_path)
        blob.upload_from_file(file.file, content_type=type)
        return file_path

    def get_file(self, path) -> bytes:
        req = requests.get(path)
        return req.content

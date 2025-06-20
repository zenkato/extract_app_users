import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from .exceptions import FileUploadError, ConfigurationError

class GoogleDriveUploader:
    """ファイルをGoogle Driveにアップロードする責務を持つクラス。"""
    def __init__(self, token_file: str, creds_file: str, scopes: list[str]):
        if not os.path.exists(creds_file):
             raise ConfigurationError(f"認証情報ファイルが見つかりません: {creds_file}")
        self.token_file = token_file
        self.creds_file = creds_file
        self.scopes = scopes
        self.service = self._get_service()

    def _get_service(self) -> Resource:
        """認証を行い、Google Drive APIサービスを取得する。"""
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, self.scopes)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)

    def upload(self, file_path: str, folder_id: str) -> str:
        """指定されたファイルを指定されたフォルダIDにアップロードし、ファイルIDを返す。"""
        if not os.path.exists(file_path):
            raise FileUploadError(f"アップロード対象のファイルが見つかりません: {file_path}")
            
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, mimetype='text/csv')

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')

        except HttpError as e:
            raise FileUploadError(f"Google Driveへのアップロード中にAPIエラーが発生しました: {e}") from e
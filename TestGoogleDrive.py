from g_drive_service import GoogleDriveService
import io
from googleapiclient.http import MediaIoBaseDownload
def getFileListFromGDrive():
    selected_fields="files(id,name,webViewLink)"
    selected_field="id, name, webViewLink"
    g_drive_service=GoogleDriveService().build()
    list_file=g_drive_service.files().list(fields=selected_fields).execute()
    
    for file in list_file.get("files", []):
        print(f"Found file: {file.get('name')}, {file.get('id')}")
        file_id = file.get('id')
    #request_file = g_drive_service.files().export_media(fileId="1m8Wx26f62IOPYgnfFDCS5RsbphIsBLdC", mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.text/csv').execute()   
    request_file = g_drive_service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request_file)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')
    
    file_retrieved: str = file.getvalue()
    with open(f"downloaded_file.csv", 'wb') as f:
        f.write(file_retrieved)
    f.close()
    #downloader = MediaIoBaseDownload(file, request_file)

    #return {"files":list_file.get("files")}



# you'll require to install python, below modules
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# please change the bel
file_name = 'YOUR_FILE_NAME'
file_id = 'YOUR_FILE_ID'

creds = Credentials.from_authorized_user_file('YOUR_CREDENTIALS_JSON_FILE.json')
service = build('drive', 'v3', credentials=creds)


def get_file_id_by_name(file_name):
    response = service.files().list(q=f"name='{file_name}'").execute()
    files = response.get('files', [])
    if not files:
        print('File not found.')
        return None
    else:
        return files[0]['id']

def download_file(file_id):
    file = service.files().get(fileId=file_id).execute()
    file_name = file['name']
    request = service.files().get_media(fileId=file_id)
    fh = open(file_name, 'wb')
    downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")


def main():
    # if you do not have file id
    file_id = get_file_id_by_name(file_name)
    if file_id:
        download_file(file_id)
    else:
        print("File ID could not be retrieved.")

    # if you have the file id uncomment the below code and comment the above code in main function
    # download_file(file_id)
    
        
if __name__ == "__main__":
    main()







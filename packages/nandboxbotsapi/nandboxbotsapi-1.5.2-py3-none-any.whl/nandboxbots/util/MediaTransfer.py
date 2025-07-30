import datetime
import os

import requests
import ntpath
import mimetypes


def download_file(token, media_file_id, saving_dir_path, saving_file_name, download_server_url):
    savingDirPath = saving_dir_path if saving_dir_path is not None else os.curdir
    saving_file_name = media_file_id if saving_file_name is None else saving_file_name
    mediaFileFullPath = f'{savingDirPath}/{saving_file_name}'
    headers = {
        'Content-Type': 'application/json',
        'X-TOKEN': token
    }
    downloadStartTime = datetime.datetime.now()
    r = requests.get(download_server_url + media_file_id, allow_redirects=True, headers=headers, timeout=30000)
    downloadEndTime = datetime.datetime.now()
    print(r)
    open(mediaFileFullPath, 'wb').write(r.content)
    print(f'Downloaded file {media_file_id} took around {(downloadEndTime - downloadStartTime) / 1000} seconds')
    print('File saved locally successfully')


def upload_file(token, media_file_full_path, upload_server_url):
    file_name = ntpath.basename(media_file_full_path)
    content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
    headers = {
        'Content-Type': content_type,
        'X-TOKEN': token

    }
    uploadStartTime = datetime.datetime.now()
    r = requests.put(url=f"{upload_server_url}{file_name}", allow_redirects=True, headers=headers, timeout=40000,
                     data=open(media_file_full_path, 'rb'))
    uploadEndTime = datetime.datetime.now()
    print(f'Uploaded file {file_name} took around {(uploadEndTime - uploadStartTime) / 1000} seconds')

    file_id = r.json()["file"]
    print(file_id)

    return file_id


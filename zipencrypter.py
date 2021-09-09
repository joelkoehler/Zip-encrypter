import glob
import os
import shutil
from pathlib import Path
import pyzipper
from mediafire import (MediaFireApi, MediaFireUploader)

def copy(src, dest):

    for file_path in glob.glob(os.path.join(src, '**', ext_cat), recursive=True):
        new_path = os.path.join(dest, os.path.basename(file_path))
        shutil.copy(file_path, new_path)

def zip_encrypt(folder_path):
    if os.path.exists('ZippedFolder.zip'):
        os.remove('ZippedFolder.zip')

    parent_folder = os.path.dirname(folder_path)
    contents = os.walk(folder_path)
    try:
        zip_file = pyzipper.AESZipFile('ZippedFolder.zip','w',compression=pyzipper.ZIP_DEFLATED,encryption=pyzipper.WZ_AES)
        zip_file.pwd=b'PASSWORD'
        for root, folders, files in contents:
            # Include all subfolders, including empty ones.
            for folder_name in folders:
                absolute_path = os.path.join(root, folder_name)
                relative_path = absolute_path.replace(parent_folder + '\\',
                                                      '')
                print ("Adding '%s' to archive." % absolute_path)
                zip_file.write(absolute_path, relative_path)
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                relative_path = absolute_path.replace(parent_folder + '\\',
                                                      '')
                print ("Adding '%s' to archive." % absolute_path)
                zip_file.write(absolute_path, relative_path)

        #print ("'%s' created successfully." % output_path)

    except IOError as message:
        print (message)
        sys.exit(1)
    except OSError as message:
        print(message)
        sys.exit(1)
    except zipfile.BadZipfile as message:
        print (message)
        sys.exit(1)
    finally:
        zip_file.close()


# --------- main! -----------

# choose file type
print("------------------------------------------------------------")
print("                        zipencrypter                        ")
print("                                                            ")
print("       This program will zip all files of a specified       ")
print("         type and upload it to my mediafire account         ")
print("                                                            ")
print("Place this file in your desired root folder before running!!")
print("------------------------------------------------------------")

ext = input("Enter a file type to collect (example: \'.txt\'): ")
ext_cat = '*' + ext

# create folder, gather, zip
if os.path.exists('collect'):
    try:
        shutil.rmtree('collect')
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    os.makedirs('collect')
copy('.', 'collect')
zip_encrypt('collect')

# ----- UPLOAD -----

api = MediaFireApi()
uploader = MediaFireUploader(api)
session = api.user_get_session_token(
    email='REPLACEME',
    password='REPLACEME',
    app_id='REPLACEME')
api.session = session
response = api.user_get_info()
print(response['user_info']['display_name'])

fd = open('ZippedFolder.zip', 'rb')
result = uploader.upload(fd, 'ZippedFolder.zip', folder_key='REPLACEME')
print(api.file_get_info(result.quickkey))

# ----- CLEANUP -----
try:
    shutil.rmtree('collect')
except OSError as e:
    print("Error: %s - %s." % (e.filename, e.strerror))

if os.path.exists('ZippedFolder.zip'):
    os.remove('ZippedFolder.zip')

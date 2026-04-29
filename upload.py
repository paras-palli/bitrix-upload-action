import requests
import sys
import os

# WEBHOOK_URL = "https://appdid.bitrix24.in/rest/1/vo655lj3kdbvvi07/"
WEBHOOK_URL = "https://appdid.bitrix24.in/rest/1/0uuncsb6q92xhe0k/"

MESSAGE_GRP_ID = os.environ.get('MESSAGE_GRP_ID')
FOLDER_ID = os.environ.get("INPUT_FOLDER_ID")
FILE_NAME = os.environ.get("INPUT_FILE_NAME")
FILE_PATH = os.environ.get("INPUT_FILE_PATH")


def bitrix_call(method, payload):
    url = f"{WEBHOOK_URL}{method}.json"
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print(url)
        print(response.json())
        print(f"HTTP Error: {response.status_code}")
        sys.exit(1)

    result = response.json()

    if "error" in result:
        print("Bitrix Error:", result)
        sys.exit(1)

    return result


# --- Get-files
files = bitrix_call("disk.folder.getchildren", {"id": FOLDER_ID})

# --- Delete all
try:
    if "result" in files and len(files["result"]) > 0:
        for file in files["result"]:
            file_id = file["ID"]
            print(f"Deleting file ID: {file_id}")
            bitrix_call("disk.file.delete", {"id": file_id})
    else:
        print("No files found.")
except Exception as e:
    print(f"An error occurred during deletion: {e}")
    sys.exit(1)


# --- Upload new file (Multipart Method) 
try:
    # Step 1: Request the upload URL
    upload_config = bitrix_call("disk.folder.uploadfile", {"id": FOLDER_ID})
    upload_url = upload_config["result"]["uploadUrl"]

    # Step 2: Upload the binary file using multipart/form-data
    with open(FILE_PATH, "rb") as file_data:
        files = {'file': (FILE_NAME, file_data)}
        response = requests.post(upload_url, files=files)

    if response.status_code != 200:
        print(f"Upload failed with status: {response.status_code}")
        print(response.text)
        sys.exit(1)

except Exception as e:
    print(f"An error occurred during upload: {e}")
    sys.exit(1)


# --- Bitrix Message
repo_name = os.getenv("GITHUB_REPOSITORY")
project_name = repo_name.split("/")[-1]

message_payload = {
    "DIALOG_ID": f"chat{MESSAGE_GRP_ID}",
    "MESSAGE": f"[b]New Build Alert![/b]\n[b]{project_name}[/b]\nThe latest {FILE_NAME} have been uploaded to the Drive.",
}

bitrix_call("im.message.add", message_payload)

print("Upload successful!")
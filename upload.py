import requests
import base64
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


# Get files
files = bitrix_call("disk.folder.getchildren", {"id": FOLDER_ID})

# Delete all
if "result" in files and len(files["result"]) > 0:
    for file in files["result"]:
        file_id = file["ID"]
        print(f"Deleting file ID: {file_id}")
        bitrix_call("disk.file.delete", {"id": file_id})
else:
    print("No files found.")

# Upload new file
with open(FILE_PATH, "rb") as f:
    base64_content = base64.b64encode(f.read()).decode("utf-8")

upload_payload = {
    "id": FOLDER_ID,
    "data": {"NAME": FILE_NAME},
    "fileContent": [FILE_NAME, base64_content]
}

bitrix_call("disk.folder.uploadfile", upload_payload)

# Bitrix Message
repo_name = os.getenv("GITHUB_REPOSITORY")

message_payload = {
    "DIALOG_ID": f"chat{MESSAGE_GRP_ID}",
    "MESSAGE": f"[b]New Build Alert![/b]\n[b]{repo_name}[/b]\nThe latest {FILE_NAME} have been uploaded to the Drive."
}

bitrix_call("im.message.add", message_payload)

print("Upload successful!")
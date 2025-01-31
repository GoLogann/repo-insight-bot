import os
import shutil
from urllib.parse import urlparse
import chardet


def convert_to_txt(file_path, txt_path):
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())

        if result['confidence'] < 0.5:
            print(f"Deleting unreadable file: {file_path}")
            os.remove(file_path)
            return

        shutil.copyfile(file_path, txt_path)
        os.remove(file_path)

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return

def find_and_convert_in_dir(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".txt"):
                continue

            file_path = os.path.join(root, file)
            base = os.path.splitext(file_path)[0]
            txt_path = base + '.txt'
            if not os.path.exists(txt_path):
                convert_to_txt(file_path, txt_path)

def is_repo_downloaded(repo_url):
    repo_name = extract_repo_name(repo_url)
    repo_dir = os.path.join("./data", repo_name)
    return os.path.isdir(repo_dir)


def extract_repo_name_and_owner(repo_url: str) -> str:
    path = urlparse(repo_url).path
    return path.strip("/")

def extract_repo_name(repo_url: str) -> str:
    path = urlparse(repo_url).path
    path = path.strip("/")

    if path.endswith(".git"):
        path = path[:-4]

    repo_name = path.split("/")[-1]

    return repo_name

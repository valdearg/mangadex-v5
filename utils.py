import json
import os
import re
import urllib
import html

import requests


def check_downloaded(chapter_id):
    with open('downloaded.txt') as file:
        if chapter_id in file.read():
            return True
        else:
            return False


def clean_filename(filename):
    filename = filename.replace("...", "")
    filename = filename.replace("/", "／")
    filename = filename.replace(":", "")
    filename = filename.replace("<", "")
    filename = filename.replace("|", "")
    filename = filename.replace(">", "")
    filename = filename.replace(r'\\', '')
    filename = filename.replace('  ', ' ')
    filename = filename.replace('*', '')
    filename = filename.replace('?', '')
    filename = filename.replace('"', '')
    filename = filename.rstrip()
    filename = re.sub(r'[\s+]', ' ', filename)
    filename = filename.replace('  ', ' ')
    filename = filename.replace('´', '')
    filename = filename.replace("\\", "")
    filename = html.unescape(filename)

    return filename


def func_login():
    auth = {
        "username": "valdearg",
        "password": "RpfiPqHiyNRX3H@?b!CQ&?KkB9enGnN!tP$nGJBL"
    }

    auth_response = requests.post(
        url="https://api.mangadex.org/auth/login", json=auth)
    token = auth_response.json()["token"]["session"]

    with open('.mdauth', 'w') as f:
        json.dump(auth_response.json(), f)

    return token


def check_login(sess):

    headers = {}
    headers["Authorization"] = "Bearer " + sess

    url = "https://api.mangadex.org/auth/check"

    response = requests.get(url, headers=headers)
    req = response.text

    jsonText = json.loads(req)

    result = jsonText['result']

    if result == "ok":
        print("Logged in still")
    else:
        print("Expired session, logging in again")
        sess = func_login()

    return sess

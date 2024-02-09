import json
import os
import re
import urllib
import html
import pandas as pd
import csv

import requests


def check_downloaded(chapter_id):
    with open('downloaded.txt') as file:
        if chapter_id in file.read():
            return True
        else:
            return False


def check_downloaded_new(chapter_id, version):
    data = pd.read_csv("downloaded.csv", sep="$", header=None)

    version = str(version)

    for manga in data.values:
        if manga[0] == chapter_id and manga[1] == version:
            #print(f"Found existing chater download: {version} for ID: {chapter_id}")
            return True

    return False



def clean_filename(filename):
    filename = filename.replace("...", "")
    filename = filename.replace("..", "")
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

    if filename.endswith('.'):
        filename = filename[:-1]

    return filename


def func_login():
    auth = {
        "username": "valdearg",
        "password": "RpfiPqHiyNRX3H@?b!CQ&?KkB9enGnN!tP$nGJBL"
    }

    auth_response = requests.post(
        url="https://api.mangadex.org/auth/login", json=auth)

    if auth_response.status_code != 200:
        print(f"Error with MangaDex, response from API: {auth_response.status_code} exiting")
        if os.path.exists('running'):
            os.remove('running')
        quit()
        
    token = auth_response.json()["token"]["session"]

    with open('.mdauth', 'w') as f:
        json.dump(auth_response.json(), f)

    return token

def func_login_client_id():
    auth = {
        "grant_type": "password",
        "username": "valdearg",
        "password": "RpfiPqHiyNRX3H@?b!CQ&?KkB9enGnN!tP$nGJBL",
        "client_id": "personal-client-f4e71288-fa1b-431c-9b77-a290f8c1da0e-8aad6250",
        "client_secret": "BRvu70DMpdaj3m7SCa16ilUSeiXKutzQ"
    }

    auth_response = requests.post(
        url="https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", data=auth)

    if auth_response.status_code != 200:
        print(f"Error with MangaDex, response from API: {auth_response.status_code} exiting")
        if os.path.exists('running'):
            os.remove('running')
        quit()
        
    token = auth_response.json()["access_token"]

    with open('.mdauth_client_id', 'w') as f:
        json.dump(auth_response.json(), f, indent=4)

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

def refresh_login_client_id():
    if os.path.exists(".mdauth_client_id"):
        auth_response = json.loads(open(".mdauth_client_id", "r", encoding="utf-8").read())
    else:
        print("No existing auth, run the auth first")
        return

    auth = {
        "grant_type": "refresh_token",
        "refresh_token": auth_response['refresh_token'],
        "client_id": "personal-client-f4e71288-fa1b-431c-9b77-a290f8c1da0e-8aad6250",
        "client_secret": "BRvu70DMpdaj3m7SCa16ilUSeiXKutzQ"
    }

    auth_response = requests.post(
        url="https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", data=auth)

    if auth_response.status_code != 200:
        print(f"Error with MangaDex, response from API: {auth_response.status_code} exiting")
        if os.path.exists('running'):
            os.remove('running')
        quit()
        
    token = auth_response.json()["access_token"]

    with open('.mdauth_client_id', 'w') as f:
        json.dump(auth_response.json(), f, indent=4)

    return token

def get_manga_title(manga_id):
    data = pd.read_csv("MangaTitleDatabase.csv", sep="$", header=None)

    for manga in data.values:
        if manga_id == manga[0]:
            print(f"Found title: {manga[1]} for ID: {manga_id}")
            return manga[1]

    print("Manga ID not found, locating the new name")

    manga_data = requests.get(
        url=f"https://api.mangadex.org/manga/{manga_id}").json()['data']

    if manga_data['type'] == "manga":
        if "en" in manga_data["attributes"]["title"]:
            manga_name = manga_data["attributes"]["title"]['en']
        elif "ja" in manga_data["attributes"]["title"]:
            manga_name = manga_data["attributes"]["title"]['ja']
        elif "ja-ro" in manga_data["attributes"]["title"]:
            manga_name = manga_data["attributes"]["title"]['ja-ro']

    if manga_name:
        manga_name = clean_filename(manga_name)
        full_title = f'{manga_name}'

    print(f"{full_title} ({manga_id})")

    with open("MangaTitleDatabase.csv", mode="a+", encoding="utf-8", newline="") as file:
        file_writer = csv.writer(
            file, delimiter="$", quotechar='"', quoting=csv.QUOTE_ALL
        )

        file_writer.writerow(
            [
                manga_id,
                full_title,
            ]
        )

    return full_title
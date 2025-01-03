import json
import os
import re
import urllib
import html
import pandas as pd
import csv
import time
import io
import socket
from datetime import datetime, timedelta
import pytz
from pathlib import Path

import requests

hostname = socket.gethostname()


def func_log_to_file(log_entry):
    cur_day = time.strftime("%Y-%m-%d")
    log_file_name = f"{cur_day}-{hostname}-mangadex.log"
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{cur_time} : {log_entry}"
    with io.open(log_file_name, "a+", encoding="utf-8") as temp:
        temp.write(str("\n" + log_entry))
    print(log_entry)

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
        csv_chapter_id = manga[0]
        try:
            csv_chapter_version = int(manga[1])
        except ValueError:
            csv_chapter_version = 1

        if csv_chapter_id == chapter_id and str(csv_chapter_version) == version:
            #func_log_to_file(f"Found existing chater download: {version} for ID: {chapter_id}")
            return True

    return False

def check_last_time_processed(manga_id):
    data = pd.read_csv("FollowedManga.csv", sep="$")

    is_more_than_threshold = False
    does_manga_exist = False

    for manga in data.values:
        if manga_id == manga[0]:
            func_log_to_file(f"Found last updated for manga: {manga[1]} for ID: {manga_id}: date is: {manga[2]}")
            
            timestamp = datetime.fromisoformat(manga[2])
            now = datetime.now(pytz.timezone("UTC"))

            threshold_days_ago = now - timedelta(days=30)
            is_more_than_threshold = timestamp < threshold_days_ago
            does_manga_exist = True

    return is_more_than_threshold, does_manga_exist

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

    if os.path.exists(".auth"):
        auth_data = json.loads(open(".auth", "r", encoding="utf-8").read())

        auth = {
            "grant_type": "password",
            "username": auth_data["username"],
            "password": auth_data["password"],
        }
    else:
        print("The .auth file does not exist")
        quit()

    auth_response = requests.post(
        url="https://api.mangadex.org/auth/login", json=auth)

    if auth_response.status_code != 200:
        func_log_to_file(f"Error with MangaDex, response from API: {auth_response.status_code} exiting")
        if os.path.exists('running'):
            os.remove('running')
        quit()
        
    token = auth_response.json()["token"]["session"]

    with open('.mdauth', 'w') as f:
        json.dump(auth_response.json(), f)

    return token

def func_login_client_id():

    if os.path.exists(".auth"):
        auth_data = json.loads(open(".auth", "r", encoding="utf-8").read())

        auth = {
            "grant_type": "password",
            "username": auth_data["username"],
            "password": auth_data["password"],
            "client_id": auth_data["client_id"],
            "client_secret": auth_data["client_secret"]
        }
    else:
        print("The .auth file does not exist")
        quit()

    auth_response = requests.post(
        url="https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", data=auth)

    if auth_response.status_code != 200:
        func_log_to_file(f"Error with MangaDex, response from API: {auth_response.status_code} exiting")
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
        func_log_to_file("Logged in still")
    else:
        func_log_to_file("Expired session, logging in again")
        sess = func_login()

    return sess

def refresh_login_client_id():
    if os.path.exists(".mdauth_client_id"):
        auth_response = json.loads(open(".mdauth_client_id", "r", encoding="utf-8").read())
    else:
        func_log_to_file("No existing auth, run the auth first")
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
        func_log_to_file(f"Error with MangaDex, response from API: {auth_response.status_code} exiting")
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
            func_log_to_file(f"Found title: {manga[1]} for ID: {manga_id}")
            return manga[1]

    func_log_to_file("Manga ID not found, locating the new name")

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

    func_log_to_file(f"{full_title} ({manga_id})")

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

def func_archive_log_files():
    log_files = Path(".").glob("*-runner-mangadex.log")
    for log_file in log_files:
        func_log_to_file(f"Removing log file: {str(log_file)}")
        date_str = str(log_file).split("-", 4)
        date_str = f"{date_str[0]}-{date_str[1]}-{date_str[2]}"
        file_date = datetime.strptime(date_str, "%Y-%m-%d")

        time_difference = datetime.now() - file_date

        if time_difference > timedelta(days=7):
            new_log_name = os.path.join(log_file.parent.resolve(), "Logs", log_file.name)
            print(new_log_name)
            os.rename(os.path.join(log_file.parent.resolve(), log_file.name), new_log_name)

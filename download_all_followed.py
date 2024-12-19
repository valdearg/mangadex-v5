import datetime
import json
import os
import urllib
import re
from urllib.request import Request, urlopen
import requests
import csv
from requests.adapters import HTTPAdapter, Retry

from utils import func_login_client_id
from pagination import paged_result
from get_chapters import func_download_chapter
from utils import func_log_to_file, check_last_time_processed

s = requests.Session()

retries = Retry(total=10,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s.mount('https://', HTTPAdapter(max_retries=retries))


def func_get_all_followed_manga():
    token = func_login_client_id()

    head = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    results = s.get(
        url="https://api.mangadex.org/user/follows/manga?limit=10", headers=head)

    total = results.json()['total']

    manga_id_arr = []
    offset = -100

    while len(manga_id_arr) != total:

        offset += 100

        param = {
            "limit": "100",
            "offset": offset,
        }

        results = s.get(
            "https://api.mangadex.org/user/follows/manga", headers=head, params=param).json()

        offset = results['offset']
        total = results['total']

        for manga_data in results['data']:

            if manga_data['type'] == "manga":
                if "en" in manga_data["attributes"]["title"]:
                    manga_name = manga_data["attributes"]["title"]['en']
                elif "ja" in manga_data["attributes"]["title"]:
                    manga_name = manga_data["attributes"]["title"]['ja']
                elif "ja-ro" in manga_data["attributes"]["title"]:
                    manga_name = manga_data["attributes"]["title"]['ja-ro']
            #print(f"{manga_name} ({manga_data['id']})")

            manga_id_arr.append([manga_data['id'], manga_name])

    return manga_id_arr

def func_download_all_followed(ignore):
    manga_id_array = func_get_all_followed_manga()

    func_log_to_file(f"Located: {len(manga_id_array)} followed manga")

    total_followed_num = 0

    for manga in manga_id_array:
        total_followed_num += 1
        manga_id = manga[0]
        manga_title = manga[1]

        func_log_to_file(f"Downloading manga: {manga_title} ({total_followed_num}/{len(manga_id_array)})")

        is_more_than_threshold, does_manga_exist = check_last_time_processed(manga_id)

        if does_manga_exist:
            func_log_to_file("Already downloaded all items, skipping")
            continue

        chapters = paged_result(manga_id)

        chapter_num = 0

        for chapter in chapters:
            chapter_num += 1
            chapter_id = chapter[0]
            version = chapter[1]
            func_log_to_file(f"Downloading chapter: {chapter} ({chapter_num}/{len(chapters)})")

            func_download_chapter(chapter_id, ignore, version)

        with open("FollowedManga.csv", mode="a+", encoding="utf-8", newline="") as file:
            file_writer = csv.writer(file, delimiter="$", quotechar='"', quoting=csv.QUOTE_ALL)

            file_writer.writerow(
                [
                    manga_id,
                    manga_title,
                    datetime.datetime.now(datetime.timezone.utc).isoformat()
                ]
            )
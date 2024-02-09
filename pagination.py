import json
import os
import re
import urllib
import zipfile
import time

import requests
from dateutil import parser
from get_chapters import func_download_chapter


def paged_result(manga_id):
    head = {
        "Content-Type": "application/json"
    }

    param = {
        "manga": manga_id,
        "translatedLanguage[]": "en"
    }

    results = requests.get("https://api.mangadex.org/chapter",
                           headers=head, params=param).json()

    total = results['total']

    chapter_id_arr = []
    offset = -100

    while len(chapter_id_arr) != total:

        offset += 100

        param = {
            "manga": manga_id,
            "limit": "100",
            "offset": offset,
            "translatedLanguage[]": "en"
        }

        results = requests.get(
            "https://api.mangadex.org/chapter", headers=head, params=param).json()

        offset = results['offset']
        total = results['total']

        for result in results['data']:
            chapter_id_arr.append([result['id'], result["attributes"]['version']])

    print(f"Total chapters: {total}")

    return chapter_id_arr

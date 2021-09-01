import json
import os
import urllib
import re
import requests

from replacements import check_replacements
from blocked_groups import check_blocked_group
from utils import clean_filename
from known_groups import check_known_group, add_known_group


def func_get_chapter_name(chapter_id):
    head = {
        "Content-Type": "application/json"
    }

    chapter_data = requests.get(
        url=f"https://api.mangadex.org/chapter/{chapter_id}", headers=head).json()

    volume_num = chapter_data["data"]["attributes"]["volume"]
    chapter_num = chapter_data["data"]["attributes"]["chapter"]
    chapter_title = chapter_data["data"]["attributes"]["title"]
    published_at = chapter_data["data"]["attributes"]["publishAt"]

    for i in chapter_data["relationships"]:

        if i['type'] == "scanlation_group":

            group_id = i['id']

            is_blocked_group = check_blocked_group(group_id)

            if is_blocked_group is True:
                return None, None

            is_known_group = check_known_group(group_id)

            if is_known_group is True:
                return None, None

            if is_known_group:
                group_name = is_known_group
            else:
                try:
                    groups = requests.get(
                        url=f"https://api.mangadex.org/group/{group_id}", headers=head).json()

                    group_name = groups["data"]["attributes"]["name"]

                    add_known_group(group_id, group_name)
                except Exception as ex:
                    print("Error obtaining group ID:", group_id)
                    group_name = "UNKNOWN"

            #print("Group name:", group_name)

        if i['type'] == "manga":

            manga_id = i['id']

            manga = requests.get(
                url=f"https://api.mangadex.org/manga/{manga_id}", headers=head).json()

            manga_name = manga["data"]["attributes"]["title"]["en"]

            #print("Manga name:", manga_name)

    if manga_name:
        manga_name = check_replacements(manga_name)
        full_title = f'{manga_name}'

    if chapter_num:
        chapter_num = chapter_num.zfill(3)

        if "." in chapter_num:
            start_chapter = chapter_num.split('.')[0]
            start_chapter = start_chapter.zfill(3)
            chapter_num = start_chapter + "x" + chapter_num.split('.')[-1]

        full_title = f'{full_title} - c{chapter_num}'

    if volume_num:
        volume_num = str(volume_num).zfill(2)
        full_title = f'{full_title} (v{volume_num})'

    if chapter_title:
        full_title = f'{full_title} - {chapter_title}'

    try:
        full_title = f'{full_title} [MangaDex, {group_name}].zip'
    except:
        group_name = "No Group"
        full_title = f'{full_title} [MangaDex, {group_name}].zip'

    full_title = clean_filename(full_title)

    print(f'Full title now: {full_title} ({published_at})')

    return full_title, published_at


#zip_title, date_added = func_get_chapter_name(chapter_id, token)

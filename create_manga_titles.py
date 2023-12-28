import requests
import csv

from utils import func_login
from get_chapters import func_download_chapter
from get_title import func_get_chapter_name

from replacements import check_replacements
from blocked_groups import check_blocked_group
from utils import clean_filename

token = func_login()

head = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# this script creates a CSV file containing manga titles and IDs

# https://api.mangadex.org/user/follows/manga/feed?limit=10&offset=0&order[publishAt]=desc

list_response = requests.get(
    url="https://api.mangadex.org/manga/status", headers=head)

print(list_response.status_code)

if list_response.status_code == 200:
    list_response = list_response.json()['statuses']
else:
    quit()

for manga_id in list_response:
    print(manga_id)

    manga_data = requests.get(
        url=f"https://api.mangadex.org/manga/{manga_id}", headers=head).json()['data']

    if manga_data['type'] == "manga":
        if "en" in manga_data["attributes"]["title"]:
            manga_name = manga_data["attributes"]["title"]['en']
        elif "ja" in manga_data["attributes"]["title"]:
            manga_name = manga_data["attributes"]["title"]['ja']
        elif "ja-ro" in manga_data["attributes"]["title"]:
            manga_name = manga_data["attributes"]["title"]['ja-ro']

    if manga_name:
        manga_name = check_replacements(manga_name)
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
import argparse
import glob
import os
import sys
import time

import json
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter, Retry
from tendo import singleton

from pagination import paged_result
from get_chapters import func_download_chapter
from search import search_manga
from get_list import func_get_feed
from sync_rclone import sync_to_rclone


try:
    me = singleton.SingleInstance()
except:
    print("Already running")
    sys.exit(-1)

'''
if os.path.exists('running'):
    cur_day = time.strftime('%Y-%m-%d-%H-%M')
    command = f'mail -s "MangaDex Sync: running already" root << "MangaDex Sync: running already"'
    os.system(command)
    sys.exit("Mangadex running already")

if os.path.exists("running") is False:
    f = open("running", "w+")
    f.close()
'''

if os.path.exists(".komga"):
    sync_komga_library = True
else:
    sync_komga_library = False

s = requests.Session()

retries = Retry(total=10,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s.mount('https://', HTTPAdapter(max_retries=retries))


parser = argparse.ArgumentParser(description='Download chapters')
parser.add_argument('input')
parser.add_argument('-i', '--ignore', action='store_true')
parser.add_argument('-k', '--komga', action='store_true')

args = parser.parse_args()

print(f"Skipping existing downloads: {args.ignore}")

for f in glob.glob('*.png'):
    os.remove(f)

for f in glob.glob('*.jpg'):
    os.remove(f)

if "feed_chaps" in args.input:
    print("Downloading feed!")
    func_get_feed(False, args.ignore)

if "feed" in args.input:
    print("Downloading feed!")
    func_get_feed(True, args.ignore)

elif "chapter" in args.input:
    user_choice = input("Enter chapter ID(s): ")

    chapter_ids = user_choice.split(' ')

    for chapter_id in chapter_ids:
        if "mangadex" in chapter_id:
            chapter_id = chapter_id.split('/')[-1]

        head = {
            "Content-Type": "application/json"
        }
        
        chapter_data = s.get(
            url=f"https://api.mangadex.org/chapter/{chapter_id}", headers=head).json()
        
        volume = chapter_data["data"]["attributes"]["volume"]
            
        print("Downloading chapter:", chapter_id)
        func_download_chapter(chapter_id, args.ignore, volume)

elif "search" in args.input:
    user_choice = input("Enter search term: ")
    search_manga(user_choice)

elif "manga" in args.input:
    user_choice = input("Enter manga ID(s): ")

    manga_ids = user_choice.split(' ')

    for manga_id in manga_ids:
        chapters = paged_result(manga_id)

        num = 0

        for chapter in chapters:
            num += 1
            chapter_id = chapter[0]
            version = chapter[1]
            print(f"Downloading chapter: {chapter} ({num}/{len(chapters)})")
            func_download_chapter(chapter_id, args.ignore, version)

elif "sync" in args.input:
    print("Syncing to cloud!")

    synced_item_count = sync_to_rclone()

    if sync_komga_library and synced_item_count >= 1:
        if os.path.exists(".komga"):

            print("Scan Komga lib")

            head = {
                "Content-Type": "application/json"
            }

            komga_data = json.loads(open(".komga", "r", encoding="utf-8").read())

            for lib_id in komga_data['library_id'].split(','):
                library_response = requests.post(
                    url=f"{komga_data['base_url']}/libraries/{lib_id}/scan", auth=HTTPBasicAuth(
                        komga_data['username'],komga_data['password'] ))

else:
    print("No args entered. Try: feed/chapter/search/manga/sync")

'''
if os.path.exists('running'):
    os.remove('running')
'''
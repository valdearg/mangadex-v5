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
from send_email import func_send_email
from utils import func_log_to_file, func_archive_log_files
from download_all_followed import func_download_all_followed

'''
try:
    me = singleton.SingleInstance()
except:
    func_log_to_file("Already running")
    sys.exit(-1)
'''

parser = argparse.ArgumentParser(description='Download chapters')
parser.add_argument('-in', '--input', required=False)
parser.add_argument('-i', '--ignore', action='store_true')
parser.add_argument('-k', '--komga', action='store_true')
parser.add_argument('-f', '--feed', required=False, action='store_true')
parser.add_argument('-fc', '--feed_chaps', required=False, action='store_true')
parser.add_argument('-c', '--chapter', required=False)
parser.add_argument('-se', '--search', required=False)
parser.add_argument('-m', '--manga', required=False)
parser.add_argument('-s', '--sync', required=False, action='store_true')
parser.add_argument('-a', '--all', required=False, action='store_true')
parser.add_argument('-sk', '--skipcheck', required=False, action='store_true')

args = parser.parse_args()

func_log_to_file(f"Args: {vars(args)}")

func_log_to_file(f"Skipping checking for running: {args.skipcheck}")

if os.path.exists('running') and args.skipcheck is False:
    cur_day = time.strftime('%Y-%m-%d-%H-%M')
    func_send_email(cur_day,"MangaDex Sync: running already")
    sys.exit("Mangadex running already")
elif args.skipcheck is True:
    func_log_to_file("The skip option is set, so skipping check")
else:
    func_log_to_file(f"Unable to locate running file in: {os.getcwd()}")

if not os.path.exists("running"):
    f = open("running", "w+")
    f.close()

if os.path.exists(".komga"):
    sync_komga_library = True
else:
    sync_komga_library = False

s = requests.Session()

retries = Retry(total=10,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s.mount('https://', HTTPAdapter(max_retries=retries))

func_archive_log_files()

func_log_to_file(f"Skipping existing downloads: {args.ignore}")

if args.skipcheck is False:
    func_log_to_file("Cleaning up PNG files in DIR")
    for f in glob.glob('*.png'):
        os.remove(f)

if args.skipcheck is False:
    func_log_to_file("Cleaning up PNG files in DIR")
    for f in glob.glob('*.jpg'):
        os.remove(f)

if args.feed_chaps:
    func_log_to_file("Downloading feed!")
    func_get_feed(False, args.ignore)

if args.feed:
    func_log_to_file("Downloading feed!")
    func_get_feed(True, args.ignore)

if args.all:
    func_log_to_file("Downloading followed manga!")
    func_download_all_followed(args.ignore)

if args.chapter:
    user_choice = args.chapter

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
            
        func_log_to_file(f"Downloading chapter: {chapter_id}")
        func_download_chapter(chapter_id, args.ignore, volume)

if args.search:
    search_manga(args.search)

if args.manga:
    user_choice = args.manga

    manga_ids = user_choice.split(' ')

    for manga_id in manga_ids:
        if "http" in manga_id:
            manga_id = manga_id.split("/")[-2]
            
        chapters = paged_result(manga_id)

        num = 0

        for chapter in chapters:
            num += 1
            chapter_id = chapter[0]
            version = chapter[1]
            func_log_to_file(f"Downloading chapter: {chapter} ({num}/{len(chapters)})")
            func_download_chapter(chapter_id, args.ignore, version)

if args.sync:
    func_log_to_file("Syncing to cloud!")

    synced_item_data = sync_to_rclone()

    synced_item_count = len(synced_item_data)

    if sync_komga_library and synced_item_count >= 1:
        if os.path.exists(".komga"):

            func_log_to_file("Scan Komga lib")

            head = {
                "Content-Type": "application/json"
            }

            komga_data = json.loads(open(".komga", "r", encoding="utf-8").read())

            for lib_id in komga_data['library_id'].split(','):
                library_response = requests.post(
                    url=f"{komga_data['base_url']}/libraries/{lib_id}/scan", auth=HTTPBasicAuth(
                        komga_data['username'],komga_data['password'] ))
                
            for book in synced_item_data:
                book = book["source"]
                book_name, ext = os.path.splitext(book)

                search_term = book.split(" [")[0]

                for lib_id in komga_data['library_id'].split(','):

                    url = f"{komga_data['base_url']}/books?search={search_term}&library_id={lib_id}"

                    result = requests.get(
                        url,
                        auth=HTTPBasicAuth(komga_data["username"], komga_data["password"]),
                        headers=head,
                        timeout=30,
                    )

                    if result:
                        result_data = result.json()
                        func_log_to_file(f"Located: {result_data['totalElements']} results")

                        for search_result in result_data["content"]:
                            if search_result["name"] == book_name:
                                func_log_to_file("Book name found!")

                                url = f"{komga_data['base_url']}/books/{search_result['id']}/analyze"

                                result = requests.post(
                                    url,
                                    auth=HTTPBasicAuth(komga_data["username"], komga_data["password"]),
                                    headers=head,
                                    timeout=30000,
                                )

if os.path.exists('running'):
    os.remove('running')

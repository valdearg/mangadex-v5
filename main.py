import argparse
import glob
import os

from pagination import paged_result
from get_chapters import func_download_chapter
from search import search_manga
from get_list import func_get_feed
from sync_rclone import sync_to_rclone


parser = argparse.ArgumentParser(description='Download chapters')
parser.add_argument('input')

args = parser.parse_args()

for f in glob.glob('*.png'):
    os.remove(f)

for f in glob.glob('*.jpg'):
    os.remove(f)

if "feed_chaps" in args.input:
    print("Downloading feed!")
    func_get_feed(False)

if "feed" in args.input:
    print("Downloading feed!")
    func_get_feed(True)

elif "chapter" in args.input:
    user_choice = input("Enter chapter ID(s): ")

    chapter_ids = user_choice.split(' ')

    for chapter_id in chapter_ids:
        print("Downloading chapter:", chapter_id)
        func_download_chapter(chapter_id)

elif "search" in args.input:
    user_choice = input("Enter search term: ")
    search_manga(user_choice)

elif "manga" in args.input:
    user_choice = input("Enter manga ID(s): ")

    manga_ids = user_choice.split(' ')

    for manga_id in manga_ids:
        chapters = paged_result(manga_id)

        for chapter in chapters:
            print("Downloading chapter:", chapter)
            func_download_chapter(chapter)

elif "sync" in args.input:
    print("Syncing to cloud!")

    sync_to_rclone()

else:
    print("No args entered. Try: feed/chapter/search/manga/sync")
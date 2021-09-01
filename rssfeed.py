import argparse
import json
import os
import re
import time
import urllib
from urllib.request import Request, urlopen
import requests


#from sync_onedrive import sync_to_onedrive
from title import get_manga_title
#from runner import call_manga_runner
from mangadex import get_chapter_pages

os.chdir(os.path.dirname(os.path.realpath(__file__)))

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


def clean_filename(filename):
    filename = str(filename)
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

    return filename


def check_downloaded(chapter_id):
    chapter_id = str(chapter_id)
    chapter_id = "/" + chapter_id.split('/')[-1] + "/"
    with open('downloaded.txt') as file:
        if chapter_id in file.read():
            return True
        else:
            return False


if os.path.exists("downloaded.txt") is False:
    f = open("downloaded.txt", "w+")
    f.close()

if os.path.exists("external.txt") is False:
    f = open("external.txt", "w+")
    f.close()

cookies = {
    'mangadex_session': '8bd62291-efdc-4ca3-8cc9-b578768c4f01',
    'mangadex_rememberme_token': 'bded98da74bb7ca78e5d85c4be07063d246d302a7624b99a0e71d9b1ebe97ef4'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.47 Safari/537.36',
}


parser = argparse.ArgumentParser(description='Download chapters')
parser.add_argument('input')

args = parser.parse_args()

link_type = ""

if "default" in args.input:
    rss_url = "https://api.mangadex.org/v2/user/133996/followed-updates"
    link_type = "default"
elif args.input.isdigit():
    rss_url = "https://mangadex.org/api/manga/{}".format(
        args.input)
    link_type = "manga"
else:
    print("Unrecognised input")

print("RSS URL is:", rss_url)


if link_type == "default":
    req = requests.get(rss_url, cookies=cookies, headers=headers)

    jsonText = json.loads(req.text)
    jsonText = jsonText['data']

    entries = jsonText['chapters']

    for entry in entries:
        chapter_id = str(entry['id'])
        has_been_downloaded = check_downloaded(chapter_id)
        if has_been_downloaded is False:
            try:
                manga_title = get_manga_title(chapter_id)
            except:
                print("Error downloading:", chapter_id)
                completed = False

            if manga_title:
                completed = get_chapter_pages(chapter_id, manga_title)

            # if completed is True:
            #    downloaded = open("downloaded.txt", "a")
            #    chapter_id = entry['id']

            #    downloaded.write("/" + chapter_id + "/" + "\n")
            #    downloaded.close()


if link_type == "rss2":
    print("Manga detected")
    try:
        req = Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})

        page = urlopen(req).read()
        jsonText = json.loads(page)

        if jsonText['chapter']:
            for i in jsonText['chapter']:
                lang_code = jsonText['chapter']['{}'.format(i)]['lang_code']
                group_name = jsonText['chapter']['{}'.format(i)]['group_name']

                if lang_code == "gb":
                    #print("Chap ID: {} and lang code: {}".format(i, lang_code))
                    chap_id = str(i)

                    has_been_downloaded = check_downloaded(chap_id)
                    if has_been_downloaded is False:
                        try:
                            completed = get_manga_title(
                                group_name, chap_id, driver)
                        except Exception as ex:
                            print("Error downloading:", chap_id)
                            print("Error: {}".format(ex))
                            completed = False

                        if completed is True:
                            downloaded = open("downloaded.txt", "a")
                            downloaded.write("/" + chap_id + "/" + "\n")
                            downloaded.close()
    except Exception as ex:
        print("Error in manga loop")
        print("Error is: {}".format(ex))


if link_type == "manga":
    print("Manga detected")
    try:
        req = Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})

        page = urlopen(req).read()
        jsonText = json.loads(page)

        if jsonText['chapter']:
            for i in jsonText['chapter']:
                lang_code = jsonText['chapter']['{}'.format(i)]['lang_code']
                group_name = jsonText['chapter']['{}'.format(i)]['group_name']

                if lang_code == "gb":
                    #print("Chap ID: {} and lang code: {}".format(i, lang_code))
                    chap_id = str(i)

                    has_been_downloaded = check_downloaded(chap_id)
                    if has_been_downloaded is False:
                        try:
                            completed = get_manga_title(
                                group_name, chap_id, driver)
                        except Exception as ex:
                            print("Error downloading:", chap_id)
                            print("Error: {}".format(ex))
                            completed = False

                        if completed is True:
                            downloaded = open("downloaded.txt", "a")
                            downloaded.write("/" + chap_id + "/" + "\n")
                            downloaded.close()
    except Exception as ex:
        print("Error in manga loop")
        print("Error is: {}".format(ex))

print("Removing underscores from archive names")
filenames = os.listdir(dname)

# checking for existing files with _ in them and then renaming them
for filename in filenames:
    if ".png" in filename:
        os.remove(os.path.join(dname, filename))
    if "_" in filename:
        if "zip" in filename:
            new_filename = filename.replace('_', ' ')
            os.rename(os.path.join(dname, filename), os.path.join(
                dname, new_filename))

print("Calling OneDrive sync")
sync_to_onedrive()

driver.quit()

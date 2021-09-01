import os
import zipfile
import time
import traceback
import platform

import requests
from dateutil import parser
from tqdm import tqdm

from get_title import func_get_chapter_name
from utils import check_downloaded

os_name = platform.system()


def func_download_chapter(chapter_id):
    head = {
        "Content-Type": "application/json"
    }

    has_been_downloaded = check_downloaded(chapter_id)

    if has_been_downloaded is True:
        print("Already downloaded:", chapter_id)
        return

    dest_zip_file, date_added = func_get_chapter_name(chapter_id)

    if dest_zip_file is None:
        return

    if os.path.exists(dest_zip_file):
        downloaded = open("downloaded.txt", "a")

        downloaded.write(chapter_id + "\n")
        downloaded.close()
        print("ZIP file downloaded already, returning")
        return

    md_at_home_url = requests.get(
        url=f"https://api.mangadex.org/at-home/server/{chapter_id}", headers=head)

    md_at_home_url = md_at_home_url.json()["baseUrl"]

    chapter_data = requests.get(
        url=f"https://api.mangadex.org/chapter/{chapter_id}", headers=head).json()

    chapter_hash = chapter_data["data"]["attributes"]["hash"]

    filenames = []

    for img in chapter_data["data"]["attributes"]["data"]:
        chapter_url = f"{md_at_home_url}/data/{chapter_hash}/{img}"
        #print("Img:", chapter_url)

        resp = requests.get(chapter_url, stream=True)
        total = int(resp.headers.get('content-length', 0))

        if resp.headers.get('X-Cache') == "HIT":
            cached = True
        else:
            cached = False

        if resp.status_code > 200:
            params = {
                "url": chapter_url,
                "success": False,
                "bytes": total,
                "duration": resp.elapsed.microseconds,
                "cached": cached
            }

            print("Error downloading chapter, reporting")

            auth_response = requests.post(
                url="https://api.mangadex.network/report", json=params)

            return

        try:
            with open(img, 'wb') as file, tqdm(
                    desc=img,
                    total=total,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)
        except Exception as ex:
            print("Error downloading file: {}".format(img))
            print("Error:", ex)
            traceback.print_exc()

            print("Img:", chapter_url)

            os.remove(img)

            # exit()

        if os.path.exists(img):
            filenames.append(img)

            params = {
                "url": chapter_url,
                "success": True,
                "bytes": total,
                "duration": resp.elapsed.microseconds,
                "cached": cached
            }

            auth_response = requests.post(
                url="https://api.mangadex.network/report", json=params)

            # print(params)
        else:
            params = {
                "url": chapter_url,
                "success": False,
                "bytes": total,
                "duration": resp.elapsed.microseconds,
                "cached": cached
            }

            # print(params)

            auth_response = requests.post(
                url="https://api.mangadex.network/report", json=params)

            return

    try:
        if not all([os.path.isfile(page) for page in filenames]):
            print('Aborting archive')
            for page in filenames:
                print('Missing:', page)
    except:
        print("failed to download chapter:", filenames)

    zf = zipfile.ZipFile(dest_zip_file, mode='w')

    try:
        for file_name in filenames:
            zf.write(file_name)
    finally:
        zf.close()

    for file_name in filenames:
        os.remove(file_name)

    date_added_tuple = time.mktime(parser.parse(date_added).timetuple())

    #print("Date added:", date_added_tuple)
    #print("Date added (normal):", date_added)

    path = os.getcwd()

    try:
        if os_name == "Windows":
            from win32_setctime import setctime

            setctime(os.path.join(path, dest_zip_file), date_added_tuple)
        os.utime(os.path.join(path, dest_zip_file),
                 (date_added_tuple, date_added_tuple))
    except:
        print("Error changing time")

    if os.path.exists(dest_zip_file):
        downloaded = open("downloaded.txt", "a")

        downloaded.write(chapter_id + "\n")
        downloaded.close()

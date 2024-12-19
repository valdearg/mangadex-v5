import os
import platform
import time
import traceback
import zipfile
import csv
import datetime

import requests
from dateutil import parser
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm

from get_title import func_get_chapter_name
from utils import check_downloaded, check_downloaded_new, func_log_to_file

os_name = platform.system()
ua = UserAgent(verify_ssl=False)

s = requests.Session()

retries = Retry(total=10,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s.mount('https://', HTTPAdapter(max_retries=retries))


def func_download_chapter(chapter_id, ignore, version):
    head = {
        "Content-Type": "application/json"
    }

    if ignore is False:
        has_been_downloaded_old = check_downloaded(chapter_id)

        if has_been_downloaded_old is True:
            func_log_to_file(f"Already downloaded (Original): {chapter_id}")
            return

        has_been_downloaded_new = check_downloaded_new(chapter_id, version)

        if has_been_downloaded_new is True:
            func_log_to_file(f"Already downloaded (New!): {chapter_id}")
            return

    dest_zip_file, date_added = func_get_chapter_name(chapter_id)

    if dest_zip_file is None:
        return

    if os.path.exists(dest_zip_file):
        downloaded = open("downloaded.txt", "a")

        downloaded.write(chapter_id + "\n")
        downloaded.close()
        func_log_to_file("ZIP file downloaded already, returning")
        return

    chapter_data = s.get(
        url=f"https://api.mangadex.org/at-home/server/{chapter_id}", headers=head).json()

    if chapter_data['result'] == "ok":
        chapter_hash = chapter_data["chapter"]["hash"]
    else:
        chapter_hash = None

    if not chapter_hash:
        func_log_to_file("No chapter hash available, could be that the chapter isn't available yet!")

        chapter_data = s.get(
            url=f"https://api.mangadex.org/chapter/{chapter_id}", headers=head).json()

        func_log_to_file("PublishAt: {}".format(
            chapter_data["data"]["attributes"]["publishAt"]))
        return

    md_at_home_url = chapter_data["baseUrl"]

    filenames = []
    img_num = 0

    for img in chapter_data["chapter"]["data"]:
        img_num += 1

        chapter_url = f"{md_at_home_url}/data/{chapter_hash}/{img}"

        # getting length of first part to handle images like: "e9e3d425301eedea8b4272143227332cb2ede1e7ef4bdbdc0404b956f482daf0-e9e3d425301eedea8b4272143227332cb2ede1e7ef4bdbdc0404b956f482daf0.png",
        counting = img.split('-')

        if len(counting[0]) > 10:
            img = f"{img_num}-{counting[1]}"

        resp = s.get(chapter_url, stream=True,
                     headers={'User-Agent': ua.chrome})
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

            func_log_to_file("Error downloading chapter, reporting")

            auth_response = s.post(
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
            func_log_to_file(f"Error downloading file: {img}")
            func_log_to_file("Error:", ex)
            traceback.print_exc()

            func_log_to_file(f"Img: {chapter_url}")

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

            auth_response = s.post(
                url="https://api.mangadex.network/report", json=params)

        else:
            params = {
                "url": chapter_url,
                "success": False,
                "bytes": total,
                "duration": resp.elapsed.microseconds,
                "cached": cached
            }

            auth_response = s.post(
                url="https://api.mangadex.network/report", json=params)

            return

    try:
        if not all([os.path.isfile(page) for page in filenames]):
            func_log_to_file('Aborting archive')
            for page in filenames:
                func_log_to_file('Missing:', page)
    except:
        func_log_to_file(f"failed to download chapter: {filenames}")

    zf = zipfile.ZipFile(dest_zip_file, mode='w')

    try:
        for file_name in filenames:
            zf.write(file_name)
    finally:
        zf.close()

    for file_name in filenames:
        os.remove(file_name)

    date_added_tuple = time.mktime(parser.parse(date_added).timetuple())

    path = os.getcwd()

    try:
        if os_name == "Windows":
            from win32_setctime import setctime

            setctime(os.path.join(path, dest_zip_file), date_added_tuple)
        os.utime(os.path.join(path, dest_zip_file),
                 (date_added_tuple, date_added_tuple))
    except:
        func_log_to_file("Error changing time")

    #if os.path.exists(dest_zip_file):
    #    downloaded = open("downloaded.txt", "a")
    #    downloaded.write(chapter_id + "\n")
    #    downloaded.close()

    with open("downloaded.csv", mode="a+", encoding="utf-8", newline="") as file:
        file_writer = csv.writer(file, delimiter="$", quotechar='"', quoting=csv.QUOTE_ALL)

        file_writer.writerow(
            [
                chapter_id,
                version,
                datetime.datetime.now(datetime.timezone.utc).isoformat()
            ]
        )
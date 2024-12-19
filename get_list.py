import requests

from utils import func_login_client_id, func_log_to_file
from get_chapters import func_download_chapter
from get_title import func_get_chapter_name


def func_get_feed(download, ignore):

    token = func_login_client_id()

    head = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    param = {
        "limit": 100,
        "offset": 0,
        "translatedLanguage[]": "en",
        "order[publishAt]": "desc",
        "includeFuturePublishAt": "0",
        "includeExternalUrl": "0"
    }

    # https://api.mangadex.org/user/follows/manga/feed?limit=10&offset=0&order[publishAt]=desc

    list_response = requests.get(
        url="https://api.mangadex.org/user/follows/manga/feed", headers=head, params=param)

    func_log_to_file(list_response.status_code)

    with open("Feed.json", "w") as f:
        f.write(list_response.text)

    results = list_response.json()["data"]

    for mangas in results:
        chapter_id = mangas["id"]
        version = mangas["attributes"]['version']

        if download == True:
            func_log_to_file(f"Downloading chapter: {chapter_id}")
            func_download_chapter(chapter_id, ignore, version)
        else:
            func_log_to_file(f"Chapter: {chapter_id}")
            func_get_chapter_name(chapter_id)

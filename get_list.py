import requests

from utils import func_login
from get_chapters import func_download_chapter
from get_title import func_get_chapter_name


def func_get_feed(download):

    token = func_login()

    head = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    param = {
        "limit": 100,
        "offset": 0,
        "translatedLanguage[]": "en",
        "order[publishAt]": "desc"
    }

    # https://api.mangadex.org/user/follows/manga/feed?limit=10&offset=0&order[publishAt]=desc

    list_response = requests.get(
        url="https://api.mangadex.org/user/follows/manga/feed", headers=head, params=param)

    print(list_response.status_code)

    with open("Feed.json", "w") as f:
        f.write(list_response.text)

    results = list_response.json()["results"]

    for mangas in results:
        chapter_id = mangas["data"]["id"]

        if download == True:
            print("Downloading chapter:", chapter_id)
            func_download_chapter(chapter_id)
        else:
            print("Chapter:", chapter_id)
            func_get_chapter_name(chapter_id)

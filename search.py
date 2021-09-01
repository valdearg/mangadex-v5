import json
import os
import re
import urllib
import zipfile
import time

import requests
from dateutil import parser
from get_chapters import func_download_chapter


def search_manga(search_term):

    head = {
        "Content-Type": "application/json"
    }

    param = {
        "title": search_term,
        "limit": "100",
        "contentRating[]": "safe"
    }

    results = requests.get(
        "https://api.mangadex.org/manga", headers=head, params=param).json()

    print(f"Found: {results['total']} results for {search_term}")

    for result in results['results']:
        result_title = result['data']['attributes']['title']['en']
        result_id = result['data']['id']

        print(f"{result_title} ({result_id})")

    print("Feed the ID back")

import requests

from replacements import check_replacements
from blocked_groups import check_blocked_group
from utils import clean_filename, get_manga_title, func_log_to_file


def func_get_chapter_name(chapter_id):
    head = {
        "Content-Type": "application/json"
    }

    chapter_data = requests.get(
        url=f"https://api.mangadex.org/chapter/{chapter_id}?includes[]=scanlation_group&includes[]=manga", headers=head).json()

    volume_num = chapter_data["data"]["attributes"]["volume"]
    chapter_num = chapter_data["data"]["attributes"]["chapter"]
    chapter_title = chapter_data["data"]["attributes"]["title"]
    published_at = chapter_data["data"]["attributes"]["publishAt"]
    updated_at = chapter_data["data"]["attributes"]["updatedAt"]

    group_name = None

    for i in chapter_data["data"]["relationships"]:

        if i['type'] == "scanlation_group":

            group_id = i['id']

            is_blocked_group = check_blocked_group(group_id)

            if is_blocked_group is True:
                return None, None

            if group_name:
                group_name = group_name + " & " + i["attributes"]["name"].strip()
            else:
                group_name = i["attributes"]["name"].strip()

        if i['type'] == "manga":
            full_title = get_manga_title(i['id'])

    if chapter_num:
        chapter_num = chapter_num.zfill(3)

        if "." in chapter_num:
            start_chapter = chapter_num.split('.')[0]
            start_chapter = start_chapter.zfill(3)
            chapter_num = start_chapter + "x" + chapter_num.split('.')[-1]

        full_title = f'{full_title} - c{chapter_num}'

    if volume_num:
        volume_num = str(volume_num).zfill(2)
        full_title = f'{full_title} (v{volume_num})'

    if chapter_title:
        full_title = f'{full_title} - {chapter_title}'

    try:
        full_title = f'{full_title} [MangaDex, {group_name}].zip'
    except:
        group_name = "No Group"
        full_title = f'{full_title} [MangaDex, {group_name}].zip'

    full_title = clean_filename(full_title)

    func_log_to_file(f'Full title now: {full_title} ({updated_at})')

    return full_title, updated_at

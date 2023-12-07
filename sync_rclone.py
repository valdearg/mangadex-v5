import pandas as pd
import os
import io
import time

from send_email import func_send_email

os.chdir(os.path.dirname(os.path.realpath(__file__)))


def sync_to_rclone():
    data = pd.read_csv('manga.csv', sep='$', header=None)

    cur_day = time.strftime('%Y-%m-%d-%H-%M')
    log_file_name = os.path.join("Logs", f"{cur_day}-MangaDex.log")

    log_entry = "----------- Synced Manga -----------"

    with io.open(log_file_name, "a+", encoding='utf-8') as temp:
        temp.write(str(log_entry + "\n"))

    identified_filenames_array = []
    not_synced_filenames_array = []

    rclone_providers = ["nextcloud", "rin-komga"]

    for manga in data.values:
        mad_path = manga[0]
        od_path = manga[1]

        jap_name = mad_path.split("/")[-1]

        # checking for existing files with _ in them and then renaming them
        for filename in sorted(os.listdir(os.getcwd())):
            if ".zip" in filename:
                chapter_series = filename.split(' - c')[0]
                if jap_name.upper() in chapter_series.upper():
                    print("Syncing file:", filename)

                    with io.open(log_file_name, "a+", encoding='utf-8') as temp:
                        temp.write(f"{str(filename)} => {od_path.rstrip()}" + "\n")

                    for rclone_provider in rclone_providers:
                        if len(rclone_providers) > 1:
                            print(f"Syncing to: {rclone_provider}")
                        
                        command = f'rclone copy -v --log-file sync_manga.log "{filename.rstrip()}" "{rclone_provider}:Manga/{od_path.rstrip()}"'
                        os.system(command)

                    try:
                        os.remove(filename)
                    except:
                        print("Error removing file?")

                    identified_filenames_array.append(filename)

    log_entry = "----------- Files downloaded but not synced -----------"

    with io.open(log_file_name, "a+", encoding='utf-8') as temp:
        temp.write(str(log_entry + "\n"))

    path = os.getcwd()
    filenames = os.listdir(path)
    for filename in filenames:
        if ".zip" in filename:

            with io.open(log_file_name, "a+", encoding='utf-8') as temp:
                temp.write(str(filename + "\n"))

            print("File downloaded but not synced:", filename)
            not_synced_filenames_array.append(filename)

    if len(identified_filenames_array) >= 1:
        #command = f'mail -s "MangaDex Sync for {cur_day}" root <{log_file_name}'
        #os.system(command)
        func_send_email(cur_day, log_file_name)
    elif len(not_synced_filenames_array) >= 1:
        #command = f'mail -s "MangaDex Sync for {cur_day}" root <{log_file_name}'
        #os.system(command)
        func_send_email(cur_day, log_file_name)
    else:
        print("No files synced, not emailing")
        os.remove(log_file_name)

    return len(identified_filenames_array)
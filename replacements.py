import pandas as pd
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))


def check_replacements(manga_title):
    data = pd.read_csv('replacements.csv', sep='$', header=None)

    for manga in data.values:
        if manga_title == manga[0]:
            print("Found alternate title:", manga_title, "becomes", manga[1])
            return manga[1]

    return manga_title
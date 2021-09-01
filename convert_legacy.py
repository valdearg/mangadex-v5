
import os
import time
import urllib
import zipfile
import sqlite3
from sqlite3 import Error

import requests
from dateutil import parser

import pandas as pd


#csv_path = "chapter_map.csv"

# if os.path.exists(csv_path):
#    data = pd.read_csv(csv_path)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


user_choice = "downloaded-legacy2.txt"

if os.path.isfile(user_choice):
    print("Located file, reading")
    line_file = open(user_choice, "r", encoding="utf-8")
    lines = line_file.readlines()
    print("Completed reading, found: {} usernames".format(len(lines)))
else:
    lines = user_choice.split(' ')
    print("Presuming a username:", lines)

lines_num = 0

for line in lines:
    lines_num += 1

    line = line.rsplit()[0]
    line = line.replace('\ufeff', '')

    line = line.replace('/', '')

    sql = f''' select * from chapter_map where legacy_id = "{line}" '''
    conn = create_connection("chapter_map.db")

    try:
        results = pd.read_sql_query(sql, conn)
    except:
        results = None

    try:
        downloaded = open("downloaded-new.txt", "a")

        downloaded.write(results['new_id'][0] + "\n")
        downloaded.close()
    except:
        print("Could not find entry:", line)

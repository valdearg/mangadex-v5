import pandas as pd
import os
from csv import writer


os.chdir(os.path.dirname(os.path.realpath(__file__)))


def check_known_group(group_id):
    data = pd.read_csv('known_groups.csv', sep=',', header=None)

    for manga in data.values:
        if group_id == manga[0]:
            print(f"Known group: {manga[1]} (ID: {group_id})")
            return manga[1]

    return None


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def add_known_group(group_id, group_name):

    row_contents = [group_id, group_name]
    # Append a list as new line to an old csv file
    append_list_as_row('known_groups.csv', row_contents)

    return None

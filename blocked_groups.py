import pandas as pd
import os
from utils import func_log_to_file

os.chdir(os.path.dirname(os.path.realpath(__file__)))


def check_blocked_group(group_id):
    data = pd.read_csv('blocked_groups.csv', sep='$', header=None)

    for manga in data.values:
        if group_id == manga[0]:
            func_log_to_file(f"Blocked group: {manga[1]} (ID: {group_id})")
            return True

    return False

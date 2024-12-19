import smtplib
import time
import io
import os

from email.message import EmailMessage

port = 587  # For SSL
password = "YwS7kJfzSV9PkcXpcEjR2Q57vxCL"

HOST = "mail.gandi.net"
TO = "admin@neko.network"
FROM = "Mailer <cloud@neko.network>"


def func_send_email(date, filename):

    cur_day = time.strftime('%Y-%m-%d')
    if filename:
        log_file_name = filename
    else:
        log_file_name = f"{cur_day}-{filename}.log"

    msg = EmailMessage()

    if os.path.exists(log_file_name):
        with open(log_file_name, "r", encoding="utf-8") as fp:
            # Create a text/plain message
            
            msg.set_content(fp.read().replace('attrib +U -P "', '').replace('"', ''))

        SUBJECT = f"MangaDex Sync for {date}"
    else:
        SUBJECT = filename

    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    server = smtplib.SMTP(HOST)
    server.login(TO, password)
    server.send_message(msg)
    server.quit()

def func_send_html_email(date, filename, identified_filenames_array, not_synced_filenames_array):
    html_email = """
<HEAD>
<style>
BODY{font-family: Calibri; font-size: 12pt;}
TABLE{border: 1px solid black; border-collapse: collapse; width: 100%; }
TH{border: 1px solid black; background: #dddddd; padding: 5px;}
TD{border: 1px solid black; padding: 5px; }
</style>
</HEAD>
<BODY>
"""

    table_title = None

    cur_day = time.strftime('%Y-%m-%d')
    if filename:
        log_file_name = filename
    else:
        log_file_name = f"{cur_day}-{filename}.log"

    msg = EmailMessage()

    if identified_filenames_array:
        table_title = f"""<font face="calibri" size="5"><b>{line}</b></font><br></br>"""

        table_header = """<table>
<tr>
<th>Manga Filename</th>
<th>Destination Manga</th>
</tr>"""

        rows = []

        for item in identified_filenames_array:
            rows.append(f"<tr><td>{item['source']}</td><td>{item['dest']}</td></tr>")

        table_body = "".join(rows)

        identified_filenames_email = table_title + table_header + table_body
            

    if os.path.exists(log_file_name):
        with open(log_file_name, "r", encoding="utf-8") as fp:
            for line in fp.readlines():
                if "-----------" in line:
                    table_title = f"""<font face="calibri" size="5"><b>{line}</b></font><br></br>"""

            
            msg.set_content(fp.read().replace('attrib +U -P "', '').replace('"', ''))

        SUBJECT = f"MangaDex Sync for {date}"
    else:
        SUBJECT = filename

    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    server = smtplib.SMTP(HOST)
    server.login(TO, password)
    server.send_message(msg)
    server.quit()

#func_send_html_email("2024-07-10-19-00", "Logs/2024-07-10-19-00-MangaDex.log")
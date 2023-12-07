import smtplib
import time
import io
import os

from email.message import EmailMessage

port = 587  # For SSL
password = "YwS7kJfzSV9PkcXpcEjR2Q57vxCL"

HOST = "mail.gandi.net"
TO = "admin@neko.network"


def func_send_email(date, filename):

    cur_day = time.strftime('%Y-%m-%d')
    if filename:
        log_file_name = filename
    else:
        log_file_name = f"{cur_day}-{filename}.log"

    SUBJECT = f"MangaDex Sync for {date}"
    FROM = "Mailer <cloud@neko.network>"

    with open(log_file_name, "r", encoding="utf-8") as fp:
        # Create a text/plain message
        msg = EmailMessage()
        msg.set_content(fp.read().replace('attrib +U -P "', '').replace('"', ''))

    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    server = smtplib.SMTP(HOST)
    server.login(TO, password)
    server.send_message(msg)
    server.quit()

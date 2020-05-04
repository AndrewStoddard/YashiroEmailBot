import imaplib as imaplib
import email as email
import os as os

from dotenv import load_dotenv
#Credit to stack overflow answers as they helped greatly with figuring some of this.

load_dotenv()


def connect():
    mail = imaplib.IMAP4_SSL('imap.gmail.com','993')

    try:
        mail.login(os.getenv('EMAIL'), os.getenv('PASSWORD'))
        mail.list()
 
        mail.select(os.getenv('LABEL')) 
    except imaplib.IMAP4.error as e:
        print(e)
        return False
   

    result, data = mail.search(None, "(UNSEEN)")
    messages = []
    if result == 'OK':
        for num in data[0].split():
            result, data = mail.fetch(num, "(RFC822)") 
            email_message = email.message_from_bytes(data[0][1])
            ret, data = mail.store(num, '+FLAGS', '\Seen')
            if ret == 'OK':
                messages.append(email_message)

    bodies = []
    subjects = []

    for email_message in messages:
        body = None
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
        bodies.append(body.decode('UTF-8').rstrip())
        subjects.append(email_message['Subject'])
    emails = {'bodies': bodies, 'subjects': subjects}
    return emails
    


def check_connection():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(os.getenv('EMAIL'), os.getenv('PASSWORD'))
        mail.logout()
    except imaplib.IMAP4.error as e:
        print(e)
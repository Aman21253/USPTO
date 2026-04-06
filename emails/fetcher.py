import imaplib
import email
from django.conf import settings

class EmailFetcher:
    def __init__(self):
        self.user = settings.EMAIL_USER
        self.password = settings.EMAIL_PASSWORD

    def fetch_unseen_emails(self):
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(self.user, self.password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        emails = []

        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            emails.append(msg)
            # Mark as seen
            mail.store(num, '+FLAGS', '\\Seen')

        return emails
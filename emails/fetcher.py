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

        status, data = mail.search(
            None,
            "UNSEEN",
            "FROM",
            '"noreply@uspto.gov"',
            "SUBJECT",
            '"USPTO: Patent Electronic System - Correspondence Notification for Customer Number"',
        )

        emails = []
        if status != "OK" or not data or not data[0]:
            mail.logout()
            return emails

        for num in data[0].split():
            status, fetch_data = mail.fetch(num, "(RFC822)")
            if status != "OK" or not fetch_data or not fetch_data[0]:
                continue

            msg = email.message_from_bytes(fetch_data[0][1])
            emails.append(msg)
            mail.store(num, "+FLAGS", "\\Seen")

        mail.logout()
        return emails
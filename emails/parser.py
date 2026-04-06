from bs4 import BeautifulSoup
import re

class USPTOParser:

    def parse(self, text):
        if "<html" in text.lower():
            return self.parse_html(text)
        return self.parse_text(text)

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        results = []

        text = soup.get_text(" ", strip=True)

        cust_match = re.search(r'Customer Number[:\s]+(\d+)', text)
        customer_number = cust_match.group(1) if cust_match else None

        matches = re.findall(
            r'(\d{7,8})\s+([A-Z0-9]{2,10})\s+(\d{2}/\d{2}/\d{4})',
            text
        )

        for app_no, doc_code, mail_date in matches:
            results.append({
                "application_number": app_no,
                "document_code": doc_code,
                "mailroom_date": mail_date,
                "customer_number": customer_number
            })

        return results

    def parse_text(self, text):
        return self.parse_html(text)
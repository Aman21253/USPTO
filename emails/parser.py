from bs4 import BeautifulSoup
import re

class USPTOParser:
    SUBJECT_PATTERN = re.compile(r"Customer Number\s*:?\s*(\d+)", re.IGNORECASE)
    ROW_PATTERN = re.compile(r"(\d{7,8})\s+([A-Z0-9]{2,10})\s+(\d{2}/\d{2}/\d{4})(?:\s+(\S+))?")

    def parse(self, subject, text):
        customer_number = self.parse_subject(subject)
        if "<html" in text.lower():
            results = self.parse_html(text)
        else:
            results = self.parse_text(text)

        for item in results:
            if not item.get("customer_number"):
                item["customer_number"] = customer_number

        return results

    def parse_subject(self, subject):
        if not subject:
            return None

        match = self.SUBJECT_PATTERN.search(subject)
        return match.group(1) if match else None

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for table in soup.find_all("table"):
            headers = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
            if not headers or not any("application" in h for h in headers):
                continue

            for row in table.find_all("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
                if len(cells) < 3:
                    continue

                application_number = cells[0]
                document_code = cells[1]
                mailroom_date = cells[2]
                attorney_docket_no = cells[3] if len(cells) > 3 else None

                if not re.fullmatch(r"\d{7,8}", application_number):
                    continue

                results.append({
                    "application_number": application_number,
                    "document_code": document_code,
                    "mailroom_date": mailroom_date,
                    "attorney_docket_no": attorney_docket_no,
                })

            if results:
                return results

        return self.parse_text(soup.get_text(" ", strip=True))

    def parse_text(self, text):
        results = []
        for application_number, document_code, mailroom_date, attorney_docket_no in self.ROW_PATTERN.findall(text):
            results.append({
                "application_number": application_number,
                "document_code": document_code,
                "mailroom_date": mailroom_date,
                "attorney_docket_no": attorney_docket_no,
            })
        return results

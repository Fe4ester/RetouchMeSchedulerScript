import email
from bs4 import BeautifulSoup

with open("page.mhtml", "r", encoding="utf-8") as f:
    msg = email.message_from_file(f)

for part in msg.walk():
    if part.get_content_type() == "text/html":
        charset = part.get_content_charset() or "utf-8"
        html_bytes = part.get_payload(decode=True)
        html = html_bytes.decode(charset, errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        with open("extracted.html", "w", encoding="utf-8") as out:
            out.write(str(soup))

        print("saved")
        break

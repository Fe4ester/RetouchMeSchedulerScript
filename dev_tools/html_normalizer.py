from bs4 import BeautifulSoup

with open("extracted.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
pretty_html = soup.prettify()

with open("normalized.html", "w", encoding="utf-8") as f:
    f.write(pretty_html)

print("saved")

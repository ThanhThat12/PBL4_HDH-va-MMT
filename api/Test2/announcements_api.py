from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/announcements', methods=['GET'])
def get_announcements():
    url = 'http://sv.dut.udn.vn/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    announcements = []
    tab_ids = ["tabs_PubTB-divT0", "tabs_PubTB-divT1"]
    
    for tab_id in tab_ids:
        tab_content = soup.find(id=tab_id)
        if tab_content:
            announcement_divs = tab_content.find_all("div", class_="tbBox")
            for announcement in announcement_divs:
                caption = announcement.find("div", class_="tbBoxCaption")
                content = announcement.find("div", class_="tbBoxContent")

                if caption and content:
                    spans = caption.find_all("span")
                    if len(spans) >= 2:
                        date = spans[0].text.strip()
                        title = spans[1].text.strip()
                    else:
                        date = "No date"
                        title = "No title"

                    content_text = content.get_text(strip=True)
                    announcements.append({'date': date, 'title': title, 'content': content_text})

    return jsonify(announcements)

if __name__ == '__main__':
    app.run(debug=True)

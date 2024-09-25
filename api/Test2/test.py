from flask import Flask, jsonify

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Hàm khởi tạo Selenium WebDriver
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ headless
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Hàm để phân tích các thông báo từ một tab
def extract_announcements(soup, tab_id):
    tab_content = soup.find(id=tab_id)
    announcements_list = []
    if tab_content:
        announcements = tab_content.select("div.tbBox")
        if not announcements:
            print(f"Không tìm thấy thông báo nào trong tab với id: {tab_id}")
        for announcement in announcements:
            caption = announcement.select_one("div.tbBoxCaption")
            content = announcement.select_one("div.tbBoxContent")

            if caption and content:
                spans = caption.find_all("span")
                if len(spans) >= 2:
                    date = spans[0].text.strip()
                    title = spans[1].text.strip()
                else:
                    date = "No date"
                    title = "No title"

                # Xử lý các thẻ <a> trong phần nội dung
                for a_tag in content.find_all("a"):
                    href = a_tag.get("href", "")
                    a_tag.string = f"{a_tag.text.strip()} ({href})"

                announcement_content = content.text.strip()

                announcements_list.append({
                    'date': date,
                    'title': title,
                    'content': announcement_content
                })
    else:
        print(f"Không tìm thấy tab với id: {tab_id}")
    return announcements_list

# API để lấy thông báo từ tab0
@app.route('/tab0', methods=['GET'])
def get_announcements_tab0():
    driver = create_driver()
    try:
        url = 'http://sv.dut.udn.vn/'
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        tab_id = "tabs_PubTB-divT0"

        # Tìm tab và nhấp vào nó
        tab_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[aria-controls="{tab_id}"] a')))
        tab_link.click()

        # Chờ nội dung tab được hiển thị
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{tab_id} div.tbBox')))

        # Phân tích cú pháp HTML bằng BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Gọi hàm để xử lý các thông báo từ tab
        announcements = extract_announcements(soup, tab_id)

        return jsonify(announcements)

    finally:
        driver.quit()

# API để lấy thông báo từ tab1
@app.route('/tab1', methods=['GET'])
def get_announcements_tab1():
    driver = create_driver()
    try:
        url = 'http://sv.dut.udn.vn/'
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        tab_id = "tabs_PubTB-divT1"

        # Tìm tab và nhấp vào nó
        tab_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[aria-controls="{tab_id}"] a')))
        tab_link.click()

        # Chờ nội dung tab được hiển thị
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{tab_id} div.tbBox')))

        # Phân tích cú pháp HTML bằng BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Gọi hàm để xử lý các thông báo từ tab
        announcements = extract_announcements(soup, tab_id)

        return jsonify(announcements)

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)

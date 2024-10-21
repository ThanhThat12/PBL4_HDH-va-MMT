from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time

app = Flask(__name__)

# Tạo driver global để sử dụng lại
driver = None

# Hàm khởi tạo Selenium WebDriver và tái sử dụng
def create_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ headless
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Hàm để phân tích các thông báo từ một tab
def extract_announcements(soup, tab_id):
    tab_content = soup.find(id=tab_id)
    announcements_list = []
    if tab_content:
        announcements = tab_content.select("div.tbBox")
        for announcement in announcements:
            caption = announcement.select_one("div.tbBoxCaption")
            content = announcement.select_one("div.tbBoxContent")

            if caption and content:
                spans = caption.find_all("span")
                date = spans[0].text.strip() if len(spans) >= 1 else "No date"
                title = spans[1].text.strip() if len(spans) >= 2 else "No title"

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

# Hàm để lấy thông báo từ một tab
def get_tab_announcements(tab_id):
    driver = create_driver()
    url = 'http://sv.dut.udn.vn/'
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    try:
        # Tìm tab và nhấp vào nó
        tab_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[aria-controls="{tab_id}"] a')))
        tab_link.click()

        # Chờ nội dung tab được hiển thị
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{tab_id} div.tbBox')))

        # Phân tích cú pháp HTML bằng BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Gọi hàm để xử lý các thông báo từ tab
        return extract_announcements(soup, tab_id)
    except Exception as e:
        print(f"Lỗi khi lấy thông báo từ tab {tab_id}: {e}")
        return []

# Hàm định kỳ cập nhật nội dung từ các tab
def update_announcements_cache():
    while True:
        print("Cập nhật dữ liệu thông báo...")
        app.config['announcements_tab0'] = get_tab_announcements("tabs_PubTB-divT0")
        app.config['announcements_tab1'] = get_tab_announcements("tabs_PubTB-divT1")
        time.sleep(300)  # Cập nhật lại sau mỗi 5 phút

# API để lấy thông báo từ tab0
@app.route('/tab0', methods=['GET'])
def get_announcements_tab0():
    return jsonify(app.config.get('announcements_tab0', []))

# API để lấy thông báo từ tab1
@app.route('/tab1', methods=['GET'])
def get_announcements_tab1():
    return jsonify(app.config.get('announcements_tab1', []))

# Khởi động luồng cập nhật dữ liệu khi chạy server
if __name__ == '__main__':
    # Khởi động WebDriver
    create_driver()
    # Chạy luồng cập nhật dữ liệu
    threading.Thread(target=update_announcements_cache, daemon=True).start()
    # Chạy Flask server
    app.run(debug=True)

from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time
import traceback

app = Flask(__name__)

# Global driver variable for re-use
driver = None

# Function to create a Selenium WebDriver
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--headless")  # Uncomment for headless mode if needed
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Function to log in to the website and return the driver after successful login
def login_to_website(username, password):
    global driver
    if driver is not None:
        try:
            driver.quit()  # Quit existing driver if it's still running
        except Exception as e:
            print(f"Error when quitting the driver: {str(e)}")

    driver = create_driver()  # Create a new driver instance

    try:
        driver.get('http://sv.dut.udn.vn/PageDangNhap.aspx')

        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "DN_txtAcc")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "DN_txtPass")))

        username_field.clear()  # Clear any pre-filled data
        password_field.clear()  # Clear any pre-filled data

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = wait.until(EC.element_to_be_clickable((By.ID, "QLTH_btnLogin")))
        login_button.click()

        # Wait for the page to load and verify if the login was successful
        wait.until(EC.url_changes('http://sv.dut.udn.vn/PageDangNhap.aspx'))

        if driver.current_url == 'http://sv.dut.udn.vn/PageCaNhan.aspx':  # URL after successful login
            print("Login successful!")
            return driver
        else:
            raise Exception("Login unsuccessful! URL mismatch.")

    except Exception as e:
        print(f"Login error: {str(e)}")
        raise Exception(f"Error during login: {str(e)}")

# Example usage
try:
    driver = login_to_website("your_username", "your_password")
except Exception as e:
    print(f"Failed to log in: {e}")
finally:
    if driver is not None:
        driver.quit()  # Ensure the driver is closed after usage
# Function to extract announcements from a tab
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

                # Process <a> tags in content
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
        print(f"Tab with id: {tab_id} not found")
    return announcements_list

# Function to get announcements from a specific tab
def get_tab_announcements(tab_id):
    driver = create_driver()
    url = 'http://sv.dut.udn.vn/'
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    try:
        tab_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[aria-controls="{tab_id}"] a')))
        tab_link.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{tab_id} div.tbBox')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return extract_announcements(soup, tab_id)
    except Exception as e:
        print(f"Error getting announcements from tab {tab_id}: {e}")
        return []

# Function to periodically update announcements cache
def update_announcements_cache():
    while True:
        print("Updating announcements...")
        app.config['announcements_tab0'] = get_tab_announcements("tabs_PubTB-divT0")
        app.config['announcements_tab1'] = get_tab_announcements("tabs_PubTB-divT1")
        time.sleep(300)  # Update every 5 minutes

# Function to get schedule
def get_schedule(driver):
    wait = WebDriverWait(driver, 10)
    menu_personal = wait.until(EC.visibility_of_element_located((By.ID, "lPaCANHAN")))
    actions = ActionChains(driver)
    actions.move_to_element(menu_personal).perform()

    schedule_link = wait.until(EC.element_to_be_clickable((By.ID, "lCoCANHAN03")))
    schedule_link.click()

    wait.until(EC.presence_of_element_located((By.ID, "LHTN_divList")))

    html_content = driver.find_element(By.ID, 'LHTN_divList').get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.find('table')
    schedule_data = []
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            schedule_data.append(row_data)
    else:
        raise Exception("Schedule table not found in HTML.")
    return schedule_data

# Function to get survey schedule
def get_survey_schedule(driver):
    wait = WebDriverWait(driver, 10)
    survey_menu = wait.until(EC.visibility_of_element_located((By.ID, "lPaCANHAN")))
    actions = ActionChains(driver)
    actions.move_to_element(survey_menu).perform()

    survey_link = wait.until(EC.element_to_be_clickable((By.ID, "lCoCANHAN04")))
    survey_link.click()

    wait.until(EC.presence_of_element_located((By.ID, "TTKB_GridInfo")))

    html_content = driver.find_element(By.ID, 'TTKB_GridInfo').get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.find('table')
    survey_data = []
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            survey_data.append(row_data)
    else:
        raise Exception("Survey schedule table not found in HTML.")
    return survey_data

# API to fetch schedule and survey schedule
@app.route('/get_all_data', methods=['POST'])
def get_all_data():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    driver = None  # Khởi tạo driver là None

    try:
        # Đăng nhập vào trang và trả về trình duyệt đã đăng nhập
        driver = login_to_website(username, password)

        # Lấy dữ liệu lịch học
        schedule_data = get_schedule(driver)

        # Lấy dữ liệu lịch khảo sát ý kiến
        survey_data = get_survey_schedule(driver)

        # Trả về thông tin lịch học và lịch khảo sát ý kiến
        return jsonify({
            "success": True,
            "username": username,
            "schedule": schedule_data,
            "survey_schedule": survey_data
        }), 200

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({"success": False, "error": str(e)}), 400

    finally:
        # Kiểm tra xem driver có được khởi tạo hay không trước khi gọi driver.quit()
        if driver is not None:
            driver.quit()

# API to get announcements from tab 0
@app.route('/tab0', methods=['GET'])
def get_announcements_tab0():
    return jsonify(app.config.get('announcements_tab0', []))

# API to get announcements from tab 1
@app.route('/tab1', methods=['GET'])
def get_announcements_tab1():
    return jsonify(app.config.get('announcements_tab1', []))

# Start a thread to update announcements cache
if __name__ == '__main__':
    create_driver()
    threading.Thread(target=update_announcements_cache, daemon=True).start()
    app.run(debug=True)

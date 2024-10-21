from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Khởi tạo Flask app
app = Flask(__name__)

# Hàm đăng nhập và trả về trình duyệt đã đăng nhập thành công
def login_to_website(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")  # Thêm chế độ headless để không hiển thị trình duyệt
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get('http://sv.dut.udn.vn/PageDangNhap.aspx')

        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "DN_txtAcc")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "DN_txtPass")))

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = wait.until(EC.element_to_be_clickable((By.ID, "QLTH_btnLogin")))
        login_button.click()

        # Đợi cho trang tải xong và kiểm tra URL
        wait.until(EC.url_changes('http://sv.dut.udn.vn/PageDangNhap.aspx'))

        # Kiểm tra nếu URL đã thay đổi thành URL trang chính
        if driver.current_url == 'http://sv.dut.udn.vn/PageCaNhan.aspx':  # Thay đổi thành URL trang chính
            return driver
        else:
            raise Exception("Đăng nhập không thành công!")
    except Exception as e:
        driver.quit()
        raise Exception(f"Lỗi khi đăng nhập: {str(e)}")

# Hàm lấy lịch học
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
        raise Exception("Không tìm thấy bảng lịch học trong HTML.")

    return schedule_data

# Hàm lấy lịch khảo sát ý kiến
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
        raise Exception("Không tìm thấy bảng khảo sát ý kiến trong HTML.")

    return survey_data

# API tích hợp đăng nhập và lấy dữ liệu
@app.route('/get_all_data', methods=['POST'])
def get_all_data():
    data = request.json
    username = data.get('username')
    password = data.get('password')

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
        return jsonify({"success": False, "error": str(e)}), 400

    finally:
        driver.quit()

# Chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(debug=True) 
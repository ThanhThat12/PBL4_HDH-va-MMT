from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Thông tin đăng nhập
username = "102220253"  # Thay bằng tài khoản thực của bạn
password = "that120704"  # Thay bằng mật khẩu thực của bạn

# Cấu hình trình điều khiển Chrome
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Chạy trình duyệt không hiển thị (headless)
chrome_options.add_argument("--disable-gpu")
service = Service(ChromeDriverManager().install())

# Khởi tạo trình duyệt Chrome với dịch vụ ChromeDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Bước 1: Truy cập trang web cần đăng nhập
    driver.get('http://sv.dut.udn.vn/PageDangNhap.aspx')

    # Bước 2: Điền thông tin đăng nhập
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.ID, "DN_txtAcc")))
    password_field = wait.until(EC.presence_of_element_located((By.ID, "DN_txtPass")))

    username_field.send_keys(username)
    password_field.send_keys(password)

    # Bước 3: Nhấn vào nút "Đăng nhập"
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "QLTH_btnLogin")))
    login_button.click()

    # Bước 4: Chờ trang chính tải xong và kiểm tra đăng nhập thành công
    wait.until(EC.presence_of_element_located((By.ID, "SVMainMenu")))

    # Bước 5: Di chuột vào menu "Cá nhân"
    menu_personal = wait.until(EC.visibility_of_element_located((By.ID, "lPaCANHAN")))
    actions = ActionChains(driver)
    actions.move_to_element(menu_personal).perform()

    # Bước 6: Nhấn vào "Lịch học trong ngày"
    schedule_link = wait.until(EC.element_to_be_clickable((By.ID, "lCoCANHAN03")))
    schedule_link.click()

    # Bước 7: Chờ trang "Lịch học trong ngày" tải xong
    wait.until(EC.presence_of_element_located((By.ID, "LHTN_divList")))

    # Bước 8: Lấy HTML của phần tử chứa bảng lịch học trong ngày
    html_content = driver.find_element(By.ID, 'LHTN_divList').get_attribute('outerHTML')

    # Sử dụng BeautifulSoup để phân tích cú pháp HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Tìm bảng (table) trong HTML
    table = soup.find('table')

    if table:
        # Tìm tất cả các hàng (tr) trong bảng
        rows = table.find_all('tr')

        for row in rows:
            # Tìm tất cả các ô (td) trong hàng
            cells = row.find_all('td')

            # In nội dung của từng ô
            for cell in cells:
                print(cell.get_text(strip=True))  # Lấy văn bản trong ô và xóa khoảng trắng
    else:
        print("Không tìm thấy bảng trong HTML.")

except Exception as e:
    print(f"Lỗi: {e}")

finally:
    driver.quit()  # Đóng trình duyệt sau khi hoàn thành

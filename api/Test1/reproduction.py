from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Cấu hình trình điều khiển Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ headless (không hiển thị cửa sổ trình duyệt)
service = Service(ChromeDriverManager().install())

# Khởi tạo trình duyệt Chrome với dịch vụ ChromeDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Hàm để phân tích các thông báo từ một tab
def extract_announcements(soup, tab_id):
    tab_content = soup.find(id=tab_id)
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

                #print(f"{tab_id}")
                print(f"Ngày: {date}")
                print(f"Tiêu đề: {title}")
                print(f"Nội dung: {announcement_content}")
                print("-" * 40)
    else:
        print(f"Không tìm thấy tab với id: {tab_id}")


try:
    # Tải trang web
    url = 'http://sv.dut.udn.vn/'
    driver.get(url)

    # Tạo đối tượng WebDriverWait
    wait = WebDriverWait(driver, 10)  # Chờ tối đa 10 giây

    # Duyệt qua từng tab và nhấp vào chúng
    tab_ids = ["tabs_PubTB-divT0", "tabs_PubTB-divT1"]
    
    for tab_id in tab_ids:
        # Tìm tab và nhấp vào nó
        tab_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'li[aria-controls="{tab_id}"] a')))
        tab_link.click()
        print("-" * 50)
        print(f"Nhấp vào tab với id: {tab_id}")
        print("-" * 50)

        # Chờ nội dung tab được hiển thị đầy đủ
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{tab_id} div.tbBox')))

        # Phân tích cú pháp HTML bằng BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Gọi hàm để xử lý các thông báo từ tab hiện tại
        extract_announcements(soup, tab_id)

finally:
    # Đóng trình duyệt
    driver.quit()

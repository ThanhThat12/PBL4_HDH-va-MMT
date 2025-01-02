from flask import Flask, request, jsonify
from flasgger import Swagger
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime

app = Flask(__name__)
# Cấu hình Swagger UI cho ứng dụng Flask
swagger = Swagger(app)
def get_current_semester():
    """
    Lấy mã học kỳ hiện tại theo định dạng:
    - 24: Hai số cuối của năm hiện tại.
    - 10: Kỳ 1 (tháng 8-12).
    - 20: Kỳ 2 (tháng 1-5).
    - 21: Kỳ hè (tháng 6-7).
    """
    now = datetime.now()
    year_suffix = now.year % 100
    month = now.month

    if 8 <= month <= 12:
        semester_code = 10
    elif 1 <= month <= 5:
        semester_code = 20
    else:
        semester_code = 21

    return f"{year_suffix}{semester_code}"

# Hàm kết nối đến cơ sở dữ liệu
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='PBL4'
    )
# Hàm kiểm tra và lưu thông báo vào cơ sở dữ liệu
def save_announcement(table_name, announcement):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kiểm tra xem thông báo đã tồn tại chưa
    cursor.execute(f"SELECT * FROM {table_name} WHERE title = %s AND date = %s", 
                   (announcement['title'], announcement['date']))
    existing_announcement = cursor.fetchone()
    
    if existing_announcement is None:  # Nếu chưa tồn tại, thêm thông báo mới
        cursor.execute(f"INSERT INTO {table_name} (date, title, content) VALUES (%s, %s, %s)", 
                       (announcement['date'], announcement['title'], announcement['content']))
        conn.commit()
    
    conn.close()

def extract_announcements(html):
    soup = BeautifulSoup(html, "html.parser")
    announcements = []
    seen_announcements = set()  # Sử dụng tập hợp để lưu trữ các thông báo đã thấy

    for announcement_div in soup.find_all(class_="tbBox"):
        date_element = announcement_div.select_one("div.tbBoxCaption b > span")
        date = date_element.get_text(strip=True).replace(":", "") if date_element else None

        # Lấy trường title
        span_elements = announcement_div.select("div.tbBoxCaption span")
        title = span_elements[1].get_text(strip=True) if len(span_elements) > 1 else None

        # Lấy nội dung thông báo và thay thế "tại đây" bằng liên kết
        content_element = announcement_div.select_one("div.tbBoxContent")
        if content_element:
            # Lấy nội dung gốc
            content_text = content_element.get_text(" ", strip=True)

            # Thay thế các liên kết chứa "tại đây" bằng chính URL
            for link in content_element.find_all("a", href=True):
                href = link["href"]
                link_text = link.get_text(strip=True)
                if link_text == "tại đây":
                    content_text = content_text.replace(link_text, f"({href})")
                else:
                    content_text = content_text.replace(link_text, f"{link_text} ({href})")

            content = content_text
        else:
            content = None

        # Kiểm tra và thêm thông báo mới nếu chưa có trong danh sách
        if (date, title) not in seen_announcements:
            announcements.append({
                "date": date,
                "title": title,
                "content": content
            })
            seen_announcements.add((date, title))  # Thêm cặp date-title vào tập đã thấy

    return announcements



@app.route('/search', methods=['GET'])
def search_announcements():
    """
    Search notifications by criteria: title, content, or date
    ---
    parameters:
      - name: query
        in: query
        type: string
        required: false
        description: Từ khóa tìm kiếm
      - name: criteria
        in: query
        type: string
        required: false
        description: Tiêu chí tìm kiếm (title, content, date)
      - name: tab
        in: query
        type: string
        required: true
        description: Tab của thông báo (tab0 hoặc tab1)
    responses:
      200:
        description: Danh sách thông báo phù hợp
        examples:
          application/json: [{"date": "10/12/2024", "title": "Thông báo quan trọng", "content": "Chi tiết ở đây"}]
      400:
        description: Lỗi nếu không có tiêu chí tìm kiếm hoặc tab không hợp lệ
        examples:
          application/json: {"status": "failed", "error": "Tab không hợp lệ"}
    """
     # Lấy các tham số tìm kiếm
    query = request.args.get('query', '')
    criteria = request.args.get('criteria', '')
    tab = request.args.get('tab', '')

    # Kiểm tra nếu thiếu tham số tab hoặc nếu tab không hợp lệ
    if not tab:
        return jsonify({"status": "error", "message": "Tab là bắt buộc"}), 400
    if tab not in ["tab0", "tab1"]:
        return jsonify({"status": "error", "message": "Tab không hợp lệ"}), 400

    # Kiểm tra nếu thiếu tham số tiêu chí tìm kiếm
    if not criteria or criteria not in ["title", "content", "date"]:
        return jsonify({"status": "error", "message": "Tiêu chí tìm kiếm không hợp lệ"}), 400

    # Xác định bảng dữ liệu dựa vào tab
    table = "tab0_announcements" if tab == "tab0" else "tab1_announcements"
    
    # Tạo kết nối cơ sở dữ liệu
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Nếu tìm kiếm theo ngày, kiểm tra và chuẩn bị chuỗi truy vấn
        if criteria == 'date':
            if not query:
                return jsonify({"status": "error", "message": "Giá trị tìm kiếm ngày không được để trống"}), 400
            
            # Kiểm tra định dạng ngày nhập vào
            if not validate_date_format(query, '%d/%m/%Y'):
                return jsonify({"status": "error", "message": "Định dạng ngày không hợp lệ, phải là dd/mm/yyyy"}), 400

            # Tạo truy vấn chính xác (tìm kiếm chính xác ngày)
            query_str = f"SELECT * FROM {table} WHERE {criteria} = %s"
            cursor.execute(query_str, (query,))
        else:
            # Tìm kiếm theo tiêu chí khác (tiêu đề, nội dung)
            query_str = f"SELECT * FROM {table} WHERE {criteria} LIKE %s"
            cursor.execute(query_str, (f"%{query}%",))

        # Lấy kết quả
        results = cursor.fetchall()

        if not results:
            return jsonify({"status": "error", "message": "Không tìm thấy thông báo phù hợp"}), 404

        conn.close()
        return jsonify(results), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500

    finally:
        if conn.is_connected():
            conn.close()

def validate_date_format(date_str, format):
    """
    Kiểm tra chuỗi ngày có đúng định dạng không.
    Trả về True nếu đúng định dạng, ngược lại False.
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

# API: /tab0 - Lấy thông báo không cần đăng nhập
@app.route('/tab0', methods=['GET'])
def announcement_general_tab0():
    """
    Get general announcements from Tab 0
    ---
    responses:
      200:
        description: A list of general announcements
        examples:
          application/json: [{ "date":"Ngày Thông báo", "title": "Thông báo 1", "content": "Nội dung thông báo 1"}]
      401:
        description: Error when fetching data
        examples:
          application/json: {"status": "failed", "error": "Unexpected status code"}
    """
    session = requests.Session()
    payload = {
        'E': 'CTRTBSV',
        'PAGETB': '1',
        'COL': 'TieuDe',
        'NAME': '',
        'TAB': 0
    }
    response = session.post(
        "http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=CTRTBSV&PAGETB=1&COL=TieuDe&NAME=&TAB=0",
        data=payload,
        allow_redirects=True
    )
    
    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Unexpected status code"}), 401

    announcements = extract_announcements(response.text)
    
    # Lưu thông báo vào bảng tab0_announcements
    for announcement in announcements:
        save_announcement("tab0_announcements", announcement)
    
    return jsonify(announcements), 200

# API: /tab1 - Lấy thông báo từ tab1
@app.route('/tab1', methods=['GET'])
def announcement_general_tab1():
    """
    Get module-specific announcements from Tab 1
    ---
    responses:
      200:
        description: A list of module-specific announcements
        examples:
          application/json: [{"date":"Ngày Thông báo", "title": "Thông báo 1", "content": "Nội dung thông báo 1"}]
      401:
        description: Error when fetching data
        examples:
          application/json: {"status": "failed", "error": "Unexpected status code"}
    """
    session = requests.Session()
    payload = {
        'E': 'CTRTBGV',
        'PAGETB': '1',
        'COL': 'TieuDe',
        'NAME': '',
        'TAB': 1
    }
    response = session.post(
        "http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=CTRTBGV&PAGETB=1&COL=TieuDe&NAME=&TAB=1",
        data=payload,
        allow_redirects=True
    )
    
    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Unexpected status code"}), 401

    announcements = extract_announcements(response.text)
    
    # Lưu thông báo vào bảng tab1_announcements
    for announcement in announcements:
        save_announcement("tab1_announcements", announcement)
    
    return jsonify(announcements), 200

@app.route('/login', methods=['POST'])
def login():
    """
    Login to the website and get the session
    ---
    parameters:
      - name: username,password
        in: body
        type: string
        required: true
        description: The username password for login
    responses:
      200:
        description: Login successful
        examples:
          application/json: {"status": "success"}
      401:
        description: Login failed
        examples:
          application/json: {"status": "failed"}
    """
    global session 
    
    username = request.json.get("username")
    password = request.json.get("password")

    # Tạo một session để duy trì cookies
    session = requests.Session()
    
    # Gửi yêu cầu GET để lấy VIEWSTATE và các trường cần thiết khác
    login_page = session.get("http://sv.dut.udn.vn/PageDangNhap.aspx")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    
    # Lấy VIEWSTATE, VIEWSTATEGENERATOR và EVENTVALIDATION nếu có
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    
    # Tạo payload đăng nhập
    payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstate_generator,
        '_ctl0:MainContent:DN_txtAcc': username,
        '_ctl0:MainContent:DN_txtPass': password,
        '_ctl0:MainContent:QLTH_btnLogin': 'Đăng nhập'
    }
    
    # Gửi yêu cầu POST để đăng nhập
    login_response = session.post("http://sv.dut.udn.vn/PageDangNhap.aspx", data=payload, allow_redirects=True)

    # Kiểm tra mã trạng thái
    if login_response.status_code != 200:
        return jsonify({"status": "failed", "error": "Unexpected status code"}), 401

    # Kiểm tra URL redirect
    if login_response.url.endswith('/PageCaNhan.aspx'):
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failed"}), 401
    
@app.route('/personal_info', methods=['GET'])
def personal_info():
    """
    Get Personal infor
    ---
    responses:
      200:
        description: Personal info retrieved successfully
        examples:
          application/json: {"status": "success", "data": {"HoTen": "Nguyen Thanh That", "NgaySinh": "01/01/1995", "GioiTinh": "Nam", "Email": "that1234@gmail.com"}}
      401:
        description: User is not logged in
        examples:
          application/json: {"status": "failed", "error": "User is not logged in"}
      404:
        description: Personal info not found
        examples:
          application/json: {"status": "failed", "error": "Personal info not found"}
    """
    global session
    
    # Kiểm tra đăng nhập
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    # Gửi yêu cầu GET tới trang thông tin cá nhân
    personal_info_page = session.get("http://sv.dut.udn.vn/PageCaNhan.aspx")

    # Kiểm tra mã trạng thái
    if personal_info_page.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể truy cập trang thông tin cá nhân"}), 500

    # Phân tích HTML thông tin cá nhân
    soup = BeautifulSoup(personal_info_page.text, 'html.parser')
    personal_info = {}

    # Lấy thông tin cá nhân từ các thẻ input có id cụ thể
    personal_info['HoTen'] = soup.find(id='CN_txtHoTen').get('value').strip() if soup.find(id='CN_txtHoTen') else None
    personal_info['NgaySinh'] = soup.find(id='CN_txtNgaySinh').get('value').strip() if soup.find(id='CN_txtNgaySinh') else None
    personal_info['GioiTinh'] = soup.find(id='CN_txtGioiTinh').get('value').strip() if soup.find(id='CN_txtGioiTinh') else None
    personal_info['NganhHoc'] = soup.find(id='MainContent_CN_txtNganh').get('value').strip() if soup.find(id='MainContent_CN_txtNganh') else None
    personal_info['Email'] = soup.find(id='CN_txtMail2').get('value').strip() if soup.find(id='CN_txtMail2') else None
    personal_info['CTDT'] = soup.find(id='MainContent_CN_txtCTDT').get('value').strip() if soup.find(id='MainContent_CN_txtCTDT') else None

    # Kiểm tra nếu thông tin cá nhân đã được trích xuất đầy đủ
    if all(personal_info.values()):
        return jsonify({"status": "success", "data": personal_info}), 200
    else:
        return jsonify({"status": "failed", "error": "Không tìm thấy thông tin cá nhân"}), 404



@app.route('/page_lh_ngay', methods=['GET'])
def page_lh_ngay():
    """
    Get day scheduled
    ---
    responses:
      200:
        description: Lịch học ngày hôm nay
        schema:
          type: array
          items:
            type: object
            properties:
              STT:
                type: string
              Ma:
                type: string
              TenLopHocPhan:
                type: string
              GiangVien:
                type: string
              ThoiKhoaBieu:
                type: string
              NgayHoc:
                type: string
              HocOnline:
                type: string
              GhiChu:
                type: string
      401:
        description: Người dùng chưa đăng nhập
        examples:
          application/json: {"status": "failed", "error": "Người dùng chưa đăng nhập"}
      500:
        description: Lỗi không thể lấy lịch học
        examples:
          application/json: {"status": "failed", "error": "Không thể lấy lịch học"}
    """
    global session  # Declare session as global
    
    # Check if the user is logged in
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    # Tạo URL AJAX
    today = datetime.today().strftime('%d/%m/%Y')
    ajax_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=LHTNLOAD&NF={today}"
    
    # Gửi yêu cầu AJAX
    get_schedule = session.get(ajax_url)
    
    # Kiểm tra phản hồi của yêu cầu AJAX
    if get_schedule.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể lấy lịch học"}), 500

    # Phân tích HTML content từ phản hồi AJAX
    soup = BeautifulSoup(get_schedule.text, 'html.parser')
    
    # Tìm bảng với ID LHTN_Grid
    table = soup.find('table', {'id': 'LHTN_Grid'})
    lich_hoc = []

    # Lặp qua các hàng trong bảng, bỏ qua tiêu đề
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 0:  # Kiểm tra nếu có dữ liệu trong hàng
            lich_hoc.append({
                'STT': cols[0].text.strip(),
                'Ma': cols[1].text.strip(),
                'TenLopHocPhan': cols[2].text.strip(),
                'GiangVien': cols[3].text.strip(),
                'ThoiKhoaBieu': cols[4].text.strip(),
                'NgayHoc': cols[5].text.strip(),
                'HocOnline': cols[6].text.strip(),
                'GhiChu': cols[7].text.strip() if len(cols) > 7 else None
            })
     # Kiểm tra nếu không có dữ liệu lịch học
    if not lich_hoc:
        return jsonify({"status": "failed", "error": "Không có lịch học nào cho ngày hôm nay"}), 404
    return jsonify(lich_hoc), 200
@app.route('/exam_schedule/class_schedule', methods=['GET'])
def class_schedule():
    """
    Get semester Scheduled
    ---
    responses:
      200:
        description: Lịch học theo mã học kỳ
        schema:
          type: object
          properties:
            Lịch Học:
              type: array
              items:
                type: object
                properties:
                  TT:
                    type: string
                  MaLHP:
                    type: string
                  TenLHP:
                    type: string
                  SoTC:
                    type: string
                  GiangVien:
                    type: string
                  TKB:
                    type: string
                  TuanHoc:
                    type: string
      401:
        description: Người dùng chưa đăng nhập
        examples:
          application/json: {"status": "failed", "error": "Người dùng chưa đăng nhập"}
      500:
        description: Lỗi không thể lấy lịch học
        examples:
          application/json: {"status": "failed", "error": "Không thể lấy lịch học"}
    """
    global session
    
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401
    
    # Lấy mã học kỳ hiện tại
    semester = get_current_semester()

    ajax_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=TTKBLoad&Code={semester}"
    response = session.get(ajax_url)

    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể lấy lịch học"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    table1 = soup.find('table', {'id': 'TTKB_GridInfo'})
    if table1:
        for row in table1.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 9:
                results.append({
                    'TT': cells[0].get_text(strip=True),
                    'MaLHP': cells[1].get_text(strip=True),
                    'TenLHP': cells[2].get_text(strip=True),
                    'SoTC': cells[3].get_text(strip=True),
                    'GiangVien': cells[6].get_text(strip=True),
                    'TKB': cells[7].get_text(strip=True),
                    'TuanHoc': cells[8].get_text(strip=True)
                })

    return jsonify({"Lịch Học": results}), 200



@app.route('/exam_schedule/exam_schedule', methods=['GET'])
def exam_schedule_details():
    """
    Get exam scheduled
    ---
    responses:
      200:
        description: Lịch thi theo mã học kỳ
        schema:
          type: object
          properties:
            Lịch Thi:
              type: array
              items:
                type: object
                properties:
                  TT:
                    type: string
                  MaLHP:
                    type: string
                  TenLHP:
                    type: string
                  NhomThi:
                    type: string
                  ThiChung:
                    type: string
                  LichThi:
                    type: string
      401:
        description: Người dùng chưa đăng nhập
        examples:
          application/json: {"status": "failed", "error": "Người dùng chưa đăng nhập"}
      500:
        description: Lỗi không thể lấy lịch thi
        examples:
          application/json: {"status": "failed", "error": "Không thể lấy lịch thi"}
    """
    global session
    
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    # Lấy mã học kỳ hiện tại
    semester = get_current_semester()
    ajax_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=TTKBLoad&Code={semester}"
    response = session.get(ajax_url)

    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể lấy lịch thi"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    table2 = soup.find('table', {'id': 'TTKB_GridLT'})
    if table2:
        for row in table2.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 6:
                results.append({
                    'TT': cells[0].get_text(strip=True),
                    'MaLHP': cells[1].get_text(strip=True),
                    'TenLHP': cells[2].get_text(strip=True),
                    'NhomThi': cells[3].get_text(strip=True),
                    'ThiChung': cells[4].get_text(strip=True),
                    'LichThi': cells[5].get_text(strip=True)
                })

    return jsonify({"Lịch Thi": results}), 200



@app.route('/tuition', methods=['GET'])
def tuition():
    """
    Get Tutition
    ---
    responses:
      200:
        description: Danh sách học phí và tổng tín chỉ của học kỳ hiện tại
        schema:
          type: object
          properties:
            STT:
              type: string
            MaHP:
              type: string
            TenHP:
              type: string
            SoTC:
              type: string
            CLC:
              type: string
            HOCPHI:
              type: string
            TONGCONG:
              type: object
              properties:
                TONGTC:
                  type: integer
                TONGHOCPHI:
                  type: string
      401:
        description: Người dùng chưa đăng nhập
        examples:
          application/json: {"status": "failed", "error": "Người dùng chưa đăng nhập"}
      500:
        description: Lỗi không thể lấy thông tin học phí
        examples:
          application/json: {"status": "failed", "error": "Không thể lấy học phí"}
    """
    # Kiểm tra nếu người dùng đã đăng nhập
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    # Lấy mã học kỳ hiện tại
    semester = get_current_semester()
    # URL học phí
    tuition_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=THPhiLoad&Code={semester}"

    # Gửi yêu cầu HTTP để lấy dữ liệu
    response = session.get(tuition_url)
    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể lấy học phí"}), 500

    # Phân tích nội dung HTML bằng BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm bảng học phí theo id 'THocPhi_GridInfo'
    table = soup.find('table', {'id': 'THocPhi_GridInfo'})
    if not table:
        return jsonify({"status": "failed", "error": "Không tìm thấy bảng học phí"}), 500

    tuition_info = []
    total_credits = 0  # Biến lưu tổng số tín chỉ
    total_fee = 0.0    # Biến lưu tổng học phí

    # Lặp qua các dòng trong bảng
    rows = table.find_all('tr')[1:]  # Bỏ qua dòng tiêu đề
    for row in rows:
        if 'kctHeader' not in row.get('class', []):  # Loại trừ dòng tổng cộng
            cols = row.find_all('td')
            if len(cols) >= 6:  # Đảm bảo đủ số cột
                # Lấy dữ liệu chi tiết
                stt = cols[0].text.strip()
                ma_hp = cols[1].text.strip()
                ten_hp = cols[2].text.strip()
                so_tc = cols[3].text.strip()
                clc = cols[4].text.strip()
                hoc_phi = cols[5].text.strip()

                # Tính tổng tín chỉ
                if so_tc.isdigit():
                    total_credits += int(so_tc)

                # Cộng học phí vào tổng học phí
                try:
                    hoc_phi_cleaned = hoc_phi.replace(',', '').strip()
                    if hoc_phi_cleaned.replace('.', '', 1).isdigit():
                        total_fee += float(hoc_phi_cleaned)
                except ValueError:
                    print(f"Lỗi khi chuyển đổi học phí: {hoc_phi}")

                # Thêm vào danh sách kết quả
                tuition_info.append({
                    'STT': stt,
                    'MaHP': ma_hp,
                    'TenHP': ten_hp,
                    'SoTC': so_tc,
                    'CLC': clc,
                    'HOCPHI': hoc_phi
                })
        else:
            # Dòng tổng cộng (có class 'kctHeader')
            total_cols = row.find_all('td')
            if len(total_cols) >= 6:
                total_fee_text = total_cols[5].text.strip()

    # Định dạng tổng học phí với dấu phẩy phân cách hàng nghìn
    formatted_total_fee = "{:,.0f}".format(total_fee)

    # Thêm tổng tín chỉ và học phí vào danh sách
    tuition_info.append({
        'TONGCONG': {
            'TONGTC': total_credits,  # Tổng số tín chỉ
            'TONGHOCPHI': formatted_total_fee   # Tổng học phí đã định dạng
        }
    })

    # Trả về dữ liệu học phí dưới dạng JSON
    return jsonify(tuition_info), 200
if __name__== '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime

app = Flask(__name__)
def get_current_semester():
    now = datetime.now()
    month = now.month

    if month >= 8:  # Từ tháng 8 trở đi, năm học bắt đầu từ năm hiện tại
        year = now.year % 100
    else:  # Trước tháng 8, năm học bắt đầu từ năm trước
        year = (now.year - 1) % 100

    # Xác định mã học kỳ
    if 8 <= month <= 12:
        semester_code = 10  # Học kỳ 1
    elif 1 <= month <= 5:
        semester_code = 20  # Học kỳ 2
    else:
        semester_code = 21  # Học kỳ hè

    return f"{year}{semester_code}"


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='PBL4'
    )

def save_announcement(table_name, announcement):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name} WHERE title = %s AND date = %s", 
                   (announcement['title'], announcement['date']))
    existing_announcement = cursor.fetchone()
    
    if existing_announcement is None: 
        cursor.execute(f"INSERT INTO {table_name} (date, title, content) VALUES (%s, %s, %s)", 
                       (announcement['date'], announcement['title'], announcement['content']))
        conn.commit()
    
    conn.close()

def extract_announcements(html):
    soup = BeautifulSoup(html, "html.parser")
    announcements = []
    seen_announcements = set()  

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

        if (date, title) not in seen_announcements:
            announcements.append({
                "date": date,
                "title": title,
                "content": content
            })
            seen_announcements.add((date, title))  

    return announcements



@app.route('/search', methods=['GET'])
def search_announcements():
     # Lấy các tham số tìm kiếm
    query = request.args.get('query', '')
    criteria = request.args.get('criteria', '')
    tab = request.args.get('tab', '')

    if not tab:
        return jsonify({"status": "error", "message": "Tab là bắt buộc"}), 400
    if tab not in ["tab0", "tab1"]:
        return jsonify({"status": "error", "message": "Tab không hợp lệ"}), 400

    if not criteria or criteria not in ["title", "content", "date"]:
        return jsonify({"status": "error", "message": "Tiêu chí tìm kiếm không hợp lệ"}), 400

    table = "tab0_announcements" if tab == "tab0" else "tab1_announcements"
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if criteria == 'date':
            if not query:
                return jsonify({"status": "error", "message": "Giá trị tìm kiếm ngày không được để trống"}), 400
            
            if not validate_date_format(query, '%d/%m/%Y'):
                return jsonify({"status": "error", "message": "Định dạng ngày không hợp lệ, phải là dd/mm/yyyy"}), 400

            query_str = f"SELECT * FROM {table} WHERE {criteria} = %s"
            cursor.execute(query_str, (query,))
        else:
            query_str = f"SELECT * FROM {table} WHERE {criteria} LIKE %s"
            cursor.execute(query_str, (f"%{query}%",))

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
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

@app.route('/tab0', methods=['GET'])
def announcement_general_tab0():
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
    
    for announcement in announcements:
        save_announcement("tab0_announcements", announcement)
    
    return jsonify(announcements), 200

@app.route('/tab1', methods=['GET'])
def announcement_general_tab1():
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
    
    for announcement in announcements:
        save_announcement("tab1_announcements", announcement)
    
    return jsonify(announcements), 200

@app.route('/login', methods=['POST'])
def login():
    global session 
    
    username = request.json.get("username")
    password = request.json.get("password")

    session = requests.Session() 
 
    login_page = session.get("http://sv.dut.udn.vn/PageDangNhap.aspx")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    
    payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstate_generator,
        '_ctl0:MainContent:DN_txtAcc': username,
        '_ctl0:MainContent:DN_txtPass': password,
        '_ctl0:MainContent:QLTH_btnLogin': 'Đăng nhập'
    }
    
    login_response = session.post("http://sv.dut.udn.vn/PageDangNhap.aspx", 
    data=payload, 
    allow_redirects=True)

    if login_response.status_code != 200:
        return jsonify({"status": "failed", "error": "Unexpected status code"}), 401

    if login_response.url.endswith('/PageCaNhan.aspx'):
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failed"}), 401
    
@app.route('/personal_info', methods=['GET'])
def personal_info():
    global session
    
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    personal_info_page = session.get("http://sv.dut.udn.vn/PageCaNhan.aspx")

    if personal_info_page.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể truy cập trang thông tin cá nhân"}), 500

    soup = BeautifulSoup(personal_info_page.text, 'html.parser')
    personal_info = {}

    # Lấy thông tin cá nhân từ các thẻ input có id cụ thể
    personal_info['HoTen'] = soup.find(id='CN_txtHoTen').get('value').strip() if soup.find(id='CN_txtHoTen') else None
    personal_info['NgaySinh'] = soup.find(id='CN_txtNgaySinh').get('value').strip() if soup.find(id='CN_txtNgaySinh') else None
    personal_info['GioiTinh'] = soup.find(id='CN_txtGioiTinh').get('value').strip() if soup.find(id='CN_txtGioiTinh') else None
    personal_info['NganhHoc'] = soup.find(id='MainContent_CN_txtNganh').get('value').strip() if soup.find(id='MainContent_CN_txtNganh') else None
    personal_info['Email'] = soup.find(id='CN_txtMail2').get('value').strip() if soup.find(id='CN_txtMail2') else None
    personal_info['CTDT'] = soup.find(id='MainContent_CN_txtCTDT').get('value').strip() if soup.find(id='MainContent_CN_txtCTDT') else None

    if all(personal_info.values()):
        return jsonify({"status": "success", "data": personal_info}), 200
    else:
        return jsonify({"status": "failed", "error": "Không tìm thấy thông tin cá nhân"}), 404



@app.route('/page_lh_ngay', methods=['GET'])
def page_lh_ngay():
    global session  

    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    ngay = request.args.get('ngay')  
    if not ngay:
        ngay = datetime.today().strftime('%d/%m/%Y')
    else:
        try:
            datetime.strptime(ngay, '%d/%m/%Y')
        except ValueError:
            return jsonify({"status": "failed", "error": "Định dạng ngày không hợp lệ, cần dạng dd/mm/yyyy"}), 400

    ajax_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=LHTNLOAD&NF={ngay}"

    get_schedule = session.get(ajax_url)

    if get_schedule.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể lấy lịch học"}), 500

    soup = BeautifulSoup(get_schedule.text, 'html.parser')

    table = soup.find('table', {'id': 'LHTN_Grid'})
    lich_hoc = []

    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) > 0:  
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
    if not lich_hoc:
        return jsonify({"status": "failed", "error": f"Không có lịch học nào cho ngày {ngay}"}), 404

    return jsonify(lich_hoc), 200

@app.route('/exam_schedule/class_schedule', methods=['GET'])
def class_schedule():
   
    global session
    
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401
    
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
    global session
    
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

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
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    semester = get_current_semester()
    tuition_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=THPhiLoad&Code={semester}"

    response = session.get(tuition_url)
    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Không thể lấy học phí"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'id': 'THocPhi_GridInfo'})
    if not table:
        return jsonify({"status": "failed", "error": "Không tìm thấy bảng học phí"}), 500

    tuition_info = []
    total_credits = 0  
    total_fee = 0.0    

    # Lặp qua các dòng trong bảng
    rows = table.find_all('tr')[1:]  # Bỏ qua dòng tiêu đề
    for row in rows:
        if 'kctHeader' not in row.get('class', []):  # Loại trừ dòng tổng cộng
            cols = row.find_all('td')
            if len(cols) >= 6:  
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
            total_cols = row.find_all('td')
            if len(total_cols) >= 6:
                total_fee_text = total_cols[5].text.strip()

    formatted_total_fee = "{:,.0f}".format(total_fee)

    tuition_info.append({
        'TONGCONG': {
            'TONGTC': total_credits, 
            'TONGHOCPHI': formatted_total_fee   
        }
    })

    return jsonify(tuition_info), 200
if __name__== '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
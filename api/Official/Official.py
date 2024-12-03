from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

app = Flask(__name__)

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

        # Lấy trường content
        content_element = announcement_div.select_one("div.tbBoxContent")
        content = str(content_element) if content_element else None

        # Kiểm tra và thêm thông báo mới nếu chưa có trong danh sách
        if (date, title) not in seen_announcements:
            announcements.append({
                "date": date,
                "title": title,
                "content": content
            })
            seen_announcements.add((date, title))  # Thêm cặp date-title vào tập đã thấy

    return announcements

@app.route('/tab0', methods=['GET'])
def announcement_general():
    session = requests.Session()
    payload = {
        'E': 'CTRTBSV',
        'PAGETB': '1',
        'COL': 'TieuDe',
        'NAME': '', 
        'TAB': 0
    }

    #time.sleep(3)
    response = session.post(
        "http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=CTRTBSV&PAGETB=1&COL=TieuDe&NAME=&TAB=0",
        data=payload,
        allow_redirects=True
    )
    
    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Unexpected status code"}), 401

    # Giả sử bạn xử lý và trả về dữ liệu như sau
    announcements_general = extract_announcements(response.text)  # Lưu vào biến toàn cục
    return jsonify(announcements_general), 200  # Đảm bảo trả về từ điển


@app.route('/tab1', methods=['GET'])
def announcement_module():
    session = requests.Session()
    payload = {
        'E': 'CTRTBGV',
        'PAGETB': '1',
        'COL': 'TieuDe',
        'NAME': '', 
        'TAB': 1
    }

    #time.sleep(3)
    response = session.post(
        "http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=CTRTBGV&PAGETB=1&COL=TieuDe&NAME=&TAB=1",
        data=payload,
        allow_redirects=True
    )

    if response.status_code != 200:
        return jsonify({"status": "failed", "error": "Unexpected status code"}), 401
    
    # Parse announcements and format the output
    announcements = extract_announcements(response.text)
    return jsonify(announcements), 200

session = None
        
@app.route('/login', methods=['POST'])
def login():
    global session 
    
    username= request.json.get("username")
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
    # personal_info['Lop'] = soup.find(id='CN_txtLop').get('value').strip() if soup.find(id='CN_txtLop') else None
    personal_info['Email'] = soup.find(id='CN_txtMail2').get('value').strip() if soup.find(id='CN_txtMail2') else None
    personal_info['CTDT'] = soup.find(id='MainContent_CN_txtCTDT').get('value').strip() if soup.find(id='MainContent_CN_txtCTDT') else None
    # if personal_info['Lop'] is None:
    #  print("Không tìm thấy thông tin về lớp.")
    # Kiểm tra nếu thông tin cá nhân đã được trích xuất đầy đủ
    if all(personal_info.values()):  # Kiểm tra nếu tất cả các trường đều có giá trị
        return jsonify({"status": "success", "data": personal_info}), 200
    else:
        return jsonify({"status": "failed", "error": "Không tìm thấy thông tin cá nhân"}), 404


    
@app.route('/page_lh_ngay', methods=['GET'])
def page_lh_ngay():
    global session  # Declare session as global
    
    # Check if the user is logged in
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    # Lấy ngày từ tham số query
    # date = request.args.get("date")
    # if not date:
    #     return jsonify({"status": "failed", "error": "Ngày không hợp lệ"}), 400

    # Tạo URL AJAX
    today = datetime.today().strftime('%d/%m/%Y')
    ajax_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=LHTNLOAD&NF={today}"
    
    # Gửi yêu cầu AJAX
    get_schedule = session.get(ajax_url)
    print(today) 
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
                'GhiChu': cols[7].text.strip()
            })

    return jsonify(lich_hoc), 200
@app.route('/exam_schedule/class_schedule', methods=['GET'])

def class_schedule():
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
    # Kiểm tra nếu người dùng đã đăng nhập
    if session is None:
        return jsonify({"status": "failed", "error": "Người dùng chưa đăng nhập"}), 401

    # Lấy mã học kỳ hiện tại
    semester = get_current_semester()
    # URL học phí
    tuition_url = f"http://sv.dut.udn.vn/WebAjax/evLopHP_Load.aspx?E=THPhiLoad&Code={semester}"

    # Gửi yêu cầu HTTP để lấy dữ liệu
    response = session.get(tuition_url)
    # print("Mã trạng thái HTTP:", response.status_code)  # Kiểm tra mã trạng thái
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
    total_fee = 0.0    # Biến lưu tổng học phí (Sử dụng số thực để tính toán tiền)

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
                #clc = cols[4].text.strip()
                hoc_phi = cols[5].text.strip()

                # # Tính tổng tín chỉ
                # if so_tc.isdigit():
                #     total_credits += int(so_tc)

                # # Cộng học phí vào tổng học phí (Chuyển đổi thành số thực)
                # try:
                #     # Loại bỏ dấu phẩy và khoảng trắng trước khi chuyển đổi
                #     hoc_phi_cleaned = hoc_phi.replace(',', '').strip()
                #     if hoc_phi_cleaned.replace('.', '', 1).isdigit():
                #         total_fee += float(hoc_phi_cleaned)
                # except ValueError:
                #     print(f"Lỗi khi chuyển đổi học phí: {hoc_phi}")

                # Thêm vào danh sách kết quả
                tuition_info.append({
                    'STT': stt,
                    'MaHP': ma_hp,
                    'TenHP': ten_hp,
                    'SoTC': so_tc,
                    #'CLC': clc,
                    'HOCPHI': hoc_phi
                })
        else:
            # Dòng tổng cộng (có class 'kctHeader')
            total_cols = row.find_all('td')
            if len(total_cols) >= 6:
                total_fee_text = total_cols[5].text.strip()

    # # Định dạng tổng học phí với dấu phẩy phân cách hàng nghìn
    # formatted_total_fee = "{:,.0f}".format(total_fee)

    # # Thêm tổng tín chỉ và học phí vào danh sách
    # tuition_info.append({
    #     'TONGCONG': {
    #         'TONGTC': total_credits,  # Tổng số tín chỉ
    #         'TONGHOCPHI': formatted_total_fee   # Tổng học phí đã định dạng
    #     }
    # })

    # Trả về dữ liệu học phí dưới dạng JSON
    return jsonify(tuition_info), 200



if __name__== '__main__':
    app.run(port=5000,debug=True)
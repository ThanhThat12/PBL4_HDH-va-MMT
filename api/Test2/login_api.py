from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

LOGIN_URL = 'http://sv.dut.udn.vn/PageDangNhap.aspx'
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('102220253')
    password = data.get('that120704')
    login_data = {'DN_txtAcc': username, 'DN_txtPass': password}
    session = requests.Session()
    response = session.post(LOGIN_URL, data=login_data, headers=HEADERS)

    if response.ok:
        response = session.get('http://sv.dut.udn.vn/PageLichHoc.aspx')
        soup = BeautifulSoup(response.text, 'html.parser')
        schedule_html = soup.find(id='LHTN_divList').prettify()

        return jsonify({'message': 'Đăng nhập thành công', 'schedule': schedule_html})
    else:
        return jsonify({'error': 'Đăng nhập không thành công'}), 401

if __name__ == '__main__':
    app.run(debug=True)

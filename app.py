from flask import Flask, jsonify, abort
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# Hàm kết nối cơ sở dữ liệu
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'thongbao')
        )
        if connection.is_connected():
            print("Đã kết nối đến MySQL trên XAMPP")
        return connection
    except Error as e:
        print(f"Lỗi khi kết nối MySQL: {e}")
        return None

# Hàm lấy dữ liệu từ bảng
def get_announcements_from_db(table):
    connection = create_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)  # Sử dụng dictionary=True để trả về kết quả dạng dict
        select_query = f"SELECT ngay, tieude, noidung FROM {table}"
        cursor.execute(select_query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"Lỗi khi lấy dữ liệu từ {table}: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API lấy dữ liệu từ bảng thongbaochung1
@app.route('/api/thongbaochung', methods=['GET'])
def get_thongbaochung():
    try:
        announcements = get_announcements_from_db("thongbaochung1")
        if not announcements:
            abort(404, description="Không tìm thấy dữ liệu trong bảng thongbaochung1")
        return jsonify(announcements)
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu: {e}")
        abort(500, description="Lỗi khi lấy dữ liệu.")
# API lấy dữ liệu từ bảng thongbaoLHP
@app.route('/api/thongbaolhp', methods=['GET'])
def get_thongbaolhp():
    announcements = get_announcements_from_db("thongbaolhp")
    if not announcements:
        abort(404, description="Không tìm thấy dữ liệu trong bảng thongbaolhp")
    return jsonify(announcements)

if __name__ == '__main__':
    app.run(debug=True, port = 5000)

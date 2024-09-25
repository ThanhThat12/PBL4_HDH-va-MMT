import mysql.connector  # type: ignore
from mysql.connector import Error  # type: ignore

# Hàm kết nối cơ sở dữ liệu
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Để trống nếu không có mật khẩu
            database="thongbao"
        )
        if connection.is_connected():
            print("Đã kết nối đến MySQL trên XAMPP")
        return connection
    except Error as e:
        print(f"Lỗi khi kết nối MySQL: {e}")
        return None

# Hàm lưu thông báo vào MySQL, với tham số table để chọn bảng lưu dữ liệu
def save_announcement_to_db(connection, table, date, title, content):
    try:
        cursor = connection.cursor()

        # In ra thông tin để kiểm tra trước khi lưu
        print(f"Saving to DB ({table}) - Date: {date}, Title: {title}, Content: {content}")
        
        # Chuẩn bị câu lệnh SQL với bảng động
        insert_query = f"INSERT INTO {table} (ngay, tieude, noidung) VALUES (%s, %s, %s)"
        data_tuple = (date, title, content)  # date bây giờ là chuỗi (VARCHAR)
        
        # Thực hiện câu lệnh SQL
        cursor.execute(insert_query, data_tuple)
        connection.commit()
        print(f"Thông báo '{title}' đã được lưu vào bảng {table}.")
    except Error as e:
        print(f"Lỗi khi lưu thông báo vào {table}: {e}")


import reflex as rx
from dotenv import load_dotenv
import bcrypt
import pyodbc
import os

load_dotenv()
# Lấy chuỗi kết nối từ biến môi trường đã được tải
CONNECTION_STRING = os.getenv("DATABASE_URL")


class State(rx.State):
    username: str = ""
    password: str = ""
    old_password: str = ""
    new_password: str = ""
    confirm_new_password: str = ""

    error_message: str = ""
    current_user: dict = {}

    def handle_login(self):
        """Xử lý logic đăng nhập."""
        self.error_message = ""  # Reset thông báo lỗi
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Tìm user dựa trên username
                cursor.execute(
                    "SELECT ID, Username, PasswordHash, Role, FullName FROM Users WHERE Username = ?",
                    self.username,
                )
                user_row = cursor.fetchone()
                if user_row and bcrypt.checkpw(
                    self.password.encode(), user_row.PasswordHash.encode()
                ):
                    self.current_user = {
                        "id": user_row.ID,
                        "username": user_row.Username,
                        "role": user_row.Role,
                        "fullname": user_row.FullName,
                    }

                    self.username = ""
                    self.password = ""

                    if self.current_user["role"] == "user":
                        return rx.redirect("/main_page")
                    else:
                        return rx.redirect("/product_types")

                    # ĐĂNG NHẬP THÀNH CÔNG!
                    # Thay vì alert, chúng ta chuyển hướng đến trang dashboard
                else:
                    # ĐĂNG NHẬP THẤT BẠI
                    self.error_message = "Tên đăng nhập hoặc mật khẩu không đúng."

        except Exception as e:
            self.error_message = "Lỗi kết nối database."
            print(f"Lỗi đăng nhập: {e}")

    def handle_logout(self):
        self.current_user = {}
        self.username = ""
        self.password = ""
        self.old_password = ""
        self.new_password = ""
        self.confirm_new_password = ""
        return rx.redirect("/login_page")

    def login_on_enter(self, key: str):
        if key == "Enter":
            return self.handle_login()

    def set_username(self, value: str):
        self.username = value
        self.error_message = ""

    def set_password(self, value: str):
        self.password = value
        self.error_message = ""

    def set_old_password(self, value: str):
        self.old_password = value

    def set_new_password(self, value: str):
        self.new_password = value

    def set_confirm_new_password(self, value: str):
        self.confirm_new_password = value

    def change_password(self):
        # Kiểm tra người dùng đã đăng nhập chưa
        if "username" not in self.current_user:
            return rx.window_alert("Lỗi: Bạn chưa đăng nhập.")  # Thay thế

        current_username = self.current_user["username"]

        # Kiểm tra đầu vào
        if (
            not self.old_password
            or not self.new_password
            or not self.confirm_new_password
        ):
            return rx.window_alert("Vui lòng điền đầy đủ thông tin.")  # Thay thế

        if self.new_password != self.confirm_new_password:
            return rx.window_alert(
                "Mật khẩu mới và xác nhận mật khẩu không khớp."
            )  # Thay thế

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT PasswordHash FROM Users WHERE Username = ?",
                    current_username,
                )
                user_row = cursor.fetchone()

                if user_row and bcrypt.checkpw(
                    self.old_password.encode(), user_row.PasswordHash.encode()
                ):
                    new_password_hash = bcrypt.hashpw(
                        self.new_password.encode(), bcrypt.gensalt()
                    ).decode()

                    cursor.execute(
                        "UPDATE Users SET PasswordHash = ? WHERE Username = ?",
                        new_password_hash,
                        current_username,
                    )
                    conn.commit()

                    # Xóa các trường input
                    self.old_password = ""
                    self.new_password = ""
                    self.confirm_new_password = ""

                    # Trả về alert thành công
                    return rx.window_alert("Đổi mật khẩu thành công!")  # Thay thế
                else:
                    return rx.window_alert("Mật khẩu hiện tại không đúng.")  # Thay thế

        except Exception as e:
            print(f"Lỗi khi đổi mật khẩu: {e}")
            return rx.window_alert("Lỗi hệ thống khi đổi mật khẩu.")  # Thay thế

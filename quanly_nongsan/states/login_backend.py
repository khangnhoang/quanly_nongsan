import reflex as rx
from dotenv import load_dotenv
import bcrypt
import pyodbc
import os
import json

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class State(rx.State):
    username: str = ""
    password: str = ""
    old_password: str = ""
    new_password: str = ""
    confirm_new_password: str = ""

    remember_me: bool = False

    error_message: str = ""
    current_user: dict = {}

    # Checkbox "Ghi nhớ tôi"
    def set_remember_me(self, value: bool):
        self.remember_me = bool(value)

    # Đọc cookie 'auth_user' bằng JS và set current_user nếu hợp lệ
    # login_backend.py (thêm trong class State)

    def hydrate_from_cookie(self, cookie_val):
        """Callback cho call_script: parse cookie và set current_user."""
        try:
            import json

            text = "null" if cookie_val in (None, "null", "") else str(cookie_val)
            data = json.loads(text)
            if isinstance(data, dict) and data.get("id") and data.get("username"):
                self.current_user = data
        except Exception:
            pass
        return []  # phải trả về list rỗng để hợp lệ

    def try_auto_login(self):
        js = r"""
        (() => {
        const name = 'auth_user=';
        const decoded = decodeURIComponent(document.cookie || '');
        const parts = decoded.split(';');
        for (let p of parts) {
            p = p.trim();
            if (p.startsWith(name)) return p.substring(name.length);
        }
        return null;
        })()
        """
        # dùng tham chiếu class, không dùng hàm lồng/nested
        return rx.call_script(js, callback=type(self).hydrate_from_cookie)

    def handle_login(self):
        """Xử lý đăng nhập + đặt cookie nếu tick 'Ghi nhớ tôi'."""
        self.error_message = ""
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT ID, Username, PasswordHash, Role, FullName FROM Users WHERE Username = ?",
                    (self.username,),  # dùng tuple tham số
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

                    # Reset form trước khi điều hướng
                    self.username = ""
                    self.password = ""

                    events = []

                    # Nếu tick "Ghi nhớ tôi": ghi cookie 30 ngày (Path=/, SameSite=Lax)
                    if self.remember_me:
                        # 1. Tạo dictionary chứa thông tin cần lưu
                        user_data_payload = {
                            "id": self.current_user["id"],
                            "username": self.current_user["username"],
                            "role": self.current_user.get("role"),
                            "fullname": self.current_user.get("fullname"),
                        }

                        # 2. Chuyển dictionary thành một chuỗi JSON DUY NHẤT
                        cookie_value_string = json.dumps(user_data_payload)

                        # 3. Tạo script để set cookie.
                        #    Dùng json.dumps lần nữa chỉ để đảm bảo chuỗi an toàn khi đưa vào script.
                        js_safe_string = json.dumps(cookie_value_string)

                        events.append(
                            rx.call_script(
                                f"document.cookie = 'auth_user=' + encodeURIComponent({js_safe_string}) + '; Max-Age=2592000; Path=/; SameSite=Lax'"
                            )
                        )
                    else:
                        # Không tick → xoá cookie nếu có
                        events.append(
                            rx.call_script(
                                'document.cookie = "auth_user=; Max-Age=0; Path=/";'
                            )
                        )

                    # Điều hướng theo role
                    if self.current_user["role"] == "user":
                        events.append(rx.redirect("/main_page"))
                    else:
                        events.append(rx.redirect("/product_types"))
                    return events

                else:
                    self.error_message = "Tên đăng nhập hoặc mật khẩu không đúng."

        except Exception as e:
            self.error_message = "Lỗi kết nối database."
            print(f"Lỗi đăng nhập: {e}")

    def handle_logout(self):
        """Đăng xuất + xoá cookie nhớ đăng nhập."""
        self.current_user = {}
        self.username = ""
        self.password = ""
        self.old_password = ""
        self.new_password = ""
        self.confirm_new_password = ""
        self.remember_me = False

        return [
            rx.call_script('document.cookie = "auth_user=; Max-Age=0; Path=/";'),
            rx.redirect("/login_page"),
        ]

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
        # Kiểm tra đăng nhập
        if "username" not in self.current_user:
            return rx.window_alert("Lỗi: Bạn chưa đăng nhập.")

        current_username = self.current_user["username"]

        # Kiểm tra đầu vào
        if (
            not self.old_password
            or not self.new_password
            or not self.confirm_new_password
        ):
            return rx.window_alert("Vui lòng điền đầy đủ thông tin.")

        if self.new_password != self.confirm_new_password:
            return rx.window_alert("Mật khẩu mới và xác nhận mật khẩu không khớp.")

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT PasswordHash FROM Users WHERE Username = ?",
                    (current_username,),
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
                        (new_password_hash, current_username),
                    )
                    conn.commit()

                    # Xoá input
                    self.old_password = ""
                    self.new_password = ""
                    self.confirm_new_password = ""

                    return rx.window_alert("Đổi mật khẩu thành công!")
                else:
                    return rx.window_alert("Mật khẩu hiện tại không đúng.")

        except Exception as e:
            print(f"Lỗi khi đổi mật khẩu: {e}")
            return rx.window_alert("Lỗi hệ thống khi đổi mật khẩu.")

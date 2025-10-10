import reflex as rx
import pyodbc
import bcrypt
import os
from dotenv import load_dotenv
from unidecode import unidecode

# Tải các biến môi trường từ file .env
load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class UserState(rx.State):
    users: list[dict] = []

    search_query: str = ""
    """
    State quản lý các hoạt động liên quan đến người dùng như thêm, sửa, xóa.
    """
    # Lưu thông tin của user đang được chọn
    selected_user: dict | None = None
    # Lưu thông tin mới trên form chỉnh sửa
    edited_phone_number: str = ""
    edited_address: str = ""

    # --- Biến cho form "Thêm Người Dùng" ---
    new_user_full_name: str = ""
    new_user_phone_number: str = ""
    new_user_address: str = ""

    def handle_user_selection(self, checked: bool, user: dict):
    
        if checked:
        # Nếu checkbox được check, chọn user này
            self.selected_user = user
        # Đồng thời điền thông tin vào form sửa
            self.edited_phone_number = user.get("phone_number", "")
            self.edited_address = user.get("address", "")
        else:
        # Nếu checkbox được uncheck, và user đang được bỏ check chính là user đang được chọn
            if self.selected_user and self.selected_user["id"] == user["id"]:
                self.unselect_user()
    
    def unselect_user(self):
        """Reset trạng thái lựa chọn và form sửa."""
        self.selected_user = None
        self.edited_phone_number = ""
        self.edited_address = ""

    def update_user(self):
        """Cập nhật thông tin SĐT và Địa chỉ cho user đã chọn."""
        if self.selected_user is None:
            return rx.window_alert("Vui lòng chọn một người dùng để cập nhật.")

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                sql = "UPDATE Users SET PhoneNumber = ?, Address = ? WHERE ID = ?"
                cursor.execute(
                    sql,
                    (
                        self.edited_phone_number.strip(),
                        self.edited_address.strip(),
                        self.selected_user["id"],
                    ),
                )
                conn.commit()
            
            # Reset form và tải lại danh sách
            self.unselect_user()
            self.load_users()
            return rx.window_alert("Cập nhật thông tin thành công!")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi cập nhật: {e}")
        
    def delete_user(self):
        """Xóa người dùng đã chọn."""
        if self.selected_user is None:
            return rx.window_alert("Vui lòng chọn một người dùng để xóa.")

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Có thể cần xóa token của user này trước nếu có
                # cursor.execute("DELETE FROM AuthTokens WHERE UserID = ?", self.selected_user["id"])
                
                # Xóa user
                sql = "DELETE FROM Users WHERE ID = ?"
                cursor.execute(sql, self.selected_user["id"])
                conn.commit()

            # Reset form và tải lại danh sách
            self.unselect_user()
            self.load_users()
            return rx.window_alert("Xóa người dùng thành công!")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi xóa: {e}")
        
    def set_edited_phone_number(self, phone: str):
        self.edited_phone_number = phone

    def set_edited_address(self, address: str):
        self.edited_address = address

    
    #Tìm kiếm
    def set_search_query(self, query: str):
        self.search_query = query

        if not query.strip():
            return self.load_users()

    #     if not self.search_query.strip():
    #         return self.load_users()
        
    def execute_search(self):
        if not self.search_query.strip():
            return self.load_users()

        query_pattern = f"%{self.search_query.strip()}%"

        sql = """
            SELECT ID, Username, FullName, Role, PhoneNumber, Address 
            FROM Users 
            WHERE FullName LIKE ? OR PhoneNumber LIKE ? OR Username LIKE ?
            ORDER BY ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Truyền tham số tìm kiếm 3 lần (cho 3 cột)
                cursor.execute(sql, (query_pattern, query_pattern, query_pattern))
                rows = cursor.fetchall()

                # Cập nhật state users với kết quả tìm kiếm
                self.users = []
                for row in rows:
                    self.users.append(
                        {
                            "id": row.ID,
                            "username": row.Username or "",
                            "full_name": row.FullName or "",
                            "role": row.Role or "",
                            "phone_number": row.PhoneNumber or "",
                            "address": row.Address or "",
                        }
                    )

        except Exception as e:
            print(f"Lỗi khi tìm kiếm người dùng: {e}")
            return rx.window_alert(f"Lỗi cơ sở dữ liệu khi tìm kiếm: {e}")

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.execute_search()
        
    # --- Hàm xử lý chính cho việc thêm người dùng ---
    def add_user(self):
        """
        Thêm một người dùng mới vào bảng Users.
        """
        # 1. Kiểm tra dữ liệu đầu vào
        if (
            not self.new_user_full_name.strip()
            or not self.new_user_phone_number.strip()
            or not self.new_user_address.strip()
        ):
            return rx.window_alert(
                "Vui lòng nhập đầy đủ Họ tên, Số điện thoại và Địa chỉ."
            )

        # 2. Tạo username tự động
        full_name_stripped = self.new_user_full_name.strip()
        # Dùng unidecode để chuyển "Nguyễn Hoàng Khang" -> "Nguyen Hoang Khang"
        no_accent_full_name = unidecode(full_name_stripped)
        # Chuyển thành "nguyenhoangkhang" và xử lý chữ "đ"
        username = no_accent_full_name.lower().replace(" ", "").replace("đ", "d")

        # 3. Hash mật khẩu mặc định "123456"
        default_password = "123456"
        password_bytes = default_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        password_hash_str = hashed_password.decode("utf-8")

        # 4. Gán vai trò mặc định
        role = "user"

        # 5. Câu lệnh SQL để chèn dữ liệu
        sql = """
            INSERT INTO Users (Username, PasswordHash, FullName, Role, PhoneNumber, Address)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            username,
            password_hash_str,
            self.new_user_full_name.strip(),
            role,
            self.new_user_phone_number.strip(),
            self.new_user_address.strip(),
        )

        # 6. Thực thi và lưu vào cơ sở dữ liệu
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Kiểm tra xem username đã tồn tại chưa
                cursor.execute("SELECT ID FROM Users WHERE Username = ?", (username,))
                if cursor.fetchone():
                    return rx.window_alert(
                        f"Lỗi: Username '{username}' đã tồn tại. Vui lòng chọn Họ Tên khác."
                    )

                # Nếu chưa tồn tại, thêm người dùng mới
                cursor.execute(sql, values)
                conn.commit()

                # 7. Reset form sau khi thêm thành công
                self.new_user_full_name = ""
                self.new_user_phone_number = ""
                self.new_user_address = ""

                self.load_users()

        except pyodbc.Error as e:
            print(f"Lỗi khi thêm người dùng: {e}")
            return rx.window_alert(f"Lỗi cơ sở dữ liệu: {e}")
        except Exception as ex:
            print(f"Đã có lỗi xảy ra: {ex}")
            return rx.window_alert(f"Đã có lỗi hệ thống xảy ra: {ex}")

    # --- Event Handlers (Setters) cho form "Thêm Người Dùng" ---
    def set_new_user_full_name(self, name: str):
        self.new_user_full_name = name

    def set_new_user_phone_number(self, phone: str):
        self.new_user_phone_number = phone

    def set_new_user_address(self, address: str):
        self.new_user_address = address

    def load_users(self):
        """
        Tải toàn bộ danh sách người dùng từ cơ sở dữ liệu và lưu vào biến state 'users'.
        """
        self.users = []  # Xóa danh sách cũ trước khi tải
        # Lưu ý: Tuyệt đối không lấy cột PasswordHash về phía client
        sql = """
            SELECT ID, Username, FullName, Role, PhoneNumber, Address 
            FROM Users 
            ORDER BY ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    self.users.append(
                        {
                            "id": row.ID,
                            "username": row.Username or "",
                            "full_name": row.FullName or "",
                            "role": row.Role or "",
                            "phone_number": row.PhoneNumber or "",
                            "address": row.Address or "",
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải danh sách người dùng: {e}")

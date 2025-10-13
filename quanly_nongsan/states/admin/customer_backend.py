# customer_backend.py

import reflex as rx
import pyodbc
import bcrypt
import os
from dotenv import load_dotenv
from unidecode import unidecode

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class UserState(rx.State):
    users: list[dict] = []
    search_query: str = ""

    # --- BIẾN STATE CHO CHỌN NHIỀU MỤC ---
    selected_user_ids: list[int] = []
    all_selected: bool = False
    
    # --- Biến cho form "Sửa" ---
    edited_phone_number: str = ""
    edited_address: str = ""

    # --- Biến cho form "Thêm" ---
    new_user_full_name: str = ""
    new_user_phone_number: str = ""
    new_user_address: str = ""

    # --- COMPUTED PROPERTIES (TÍNH TOÁN DỰA TRÊN STATE) ---
    @rx.var
    def is_only_one_selected(self) -> bool:
        """Kiểm tra xem chỉ có đúng một khách hàng được chọn hay không."""
        return len(self.selected_user_ids) == 1

    @rx.var
    def user_to_edit(self) -> dict | None:
        """Lấy thông tin khách hàng duy nhất được chọn để hiển thị trong khung chỉnh sửa."""
        if self.is_only_one_selected:
            user_id = self.selected_user_ids[0]
            for user in self.users:
                if user["id"] == user_id:
                    return user
        return None

    # --- TẢI DỮ LIỆU ---
    def load_users(self):
        self.selected_user_ids = []
        self.all_selected = False
        self.users = []
        sql = "SELECT ID, Username, FullName, Role, PhoneNumber, Address FROM Users ORDER BY ID DESC"
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    self.users.append({
                        "id": row.ID, "username": row.Username or "",
                        "full_name": row.FullName or "", "role": row.Role or "",
                        "phone_number": row.PhoneNumber or "", "address": row.Address or "",
                    })
        except Exception as e:
            print(f"Lỗi khi tải danh sách người dùng: {e}")

    # --- HÀM XỬ LÝ CHỌN (CHECKBOX) ---
    def select_user(self, user: dict, checked: bool):
        user_id = user["id"]
        if checked:
            if user_id not in self.selected_user_ids:
                self.selected_user_ids.append(user_id)
        else:
            if user_id in self.selected_user_ids:
                self.selected_user_ids.remove(user_id)
        
        self.all_selected = (len(self.users) > 0 and len(self.selected_user_ids) == len(self.users))
        self._update_edit_fields()

    def select_all_users(self, checked: bool):
        self.all_selected = checked
        if checked:
            self.selected_user_ids = [u['id'] for u in self.users]
        else:
            self.selected_user_ids = []
        self._update_edit_fields()

    def select_single_user_for_edit(self, user: dict):
        """Chọn một khách hàng duy nhất từ nút Sửa icon."""
        self.selected_user_ids = [user["id"]]
        self.all_selected = False
        self._update_edit_fields()

    def _update_edit_fields(self):
        """Hàm nội bộ để cập nhật các trường chỉnh sửa dựa trên lựa chọn."""
        if self.is_only_one_selected:
            user = self.user_to_edit
            self.edited_phone_number = user.get("phone_number", "")
            self.edited_address = user.get("address", "")
        else:
            self.edited_phone_number = ""
            self.edited_address = ""

    # --- HÀM THÊM / SỬA / XÓA ---
    def update_user(self):
        if not self.is_only_one_selected:
            return
        
        user_id = self.user_to_edit["id"]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                sql = "UPDATE Users SET PhoneNumber = ?, Address = ? WHERE ID = ?"
                cursor.execute(sql, (self.edited_phone_number.strip(), self.edited_address.strip(), user_id))
                conn.commit()
            
            self.selected_user_ids = []
            self._update_edit_fields()
            self.load_users()
            return rx.window_alert("Cập nhật thông tin thành công!")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi cập nhật: {e}")
        
    def delete_selected_users(self):
        if not self.selected_user_ids:
            return
        
        id_list = tuple(self.selected_user_ids)
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(id_list))
                sql = f"DELETE FROM Users WHERE ID IN ({placeholders})"
                cursor.execute(sql, id_list)
                conn.commit()
            
            self.selected_user_ids = []
            self._update_edit_fields()
            self.load_users()
            return rx.window_alert(f"Đã xóa thành công {len(id_list)} khách hàng.")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi xóa: {e}")

    def delete_user_by_id(self, user_id: int):
        """Xóa một khách hàng từ nút Xóa icon."""
        self.selected_user_ids = [user_id]
        return self.delete_selected_users()

    def add_user(self):
        if not self.new_user_full_name.strip() or not self.new_user_phone_number.strip() or not self.new_user_address.strip():
            return rx.window_alert("Vui lòng nhập đầy đủ Họ tên, Số điện thoại và Địa chỉ.")

        full_name_stripped = self.new_user_full_name.strip()
        no_accent_full_name = unidecode(full_name_stripped)
        username = no_accent_full_name.lower().replace(" ", "").replace("đ", "d")

        default_password = "123456"
        password_bytes = default_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

        sql = "INSERT INTO Users (Username, PasswordHash, FullName, Role, PhoneNumber, Address) VALUES (?, ?, ?, ?, ?, ?)"
        values = (username, hashed_password, self.new_user_full_name.strip(), "user", self.new_user_phone_number.strip(), self.new_user_address.strip())

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID FROM Users WHERE Username = ?", (username,))
                if cursor.fetchone():
                    return rx.window_alert(f"Lỗi: Username '{username}' đã tồn tại. Vui lòng chọn Họ Tên khác.")
                
                cursor.execute(sql, values)
                conn.commit()

                self.new_user_full_name = ""
                self.new_user_phone_number = ""
                self.new_user_address = ""
                self.load_users()
                return rx.window_alert("Thêm khách hàng thành công!")
        except Exception as e:
            print(f"Lỗi khi thêm người dùng: {e}")
            return rx.window_alert(f"Lỗi cơ sở dữ liệu: {e}")

    # --- TÌM KIẾM ---
    def set_search_query(self, query: str):
        self.search_query = query

    def execute_search(self):
        if not self.search_query.strip():
            self.load_users()
            return

        query_pattern = f"%{self.search_query.strip()}%"
        sql = "SELECT ID, Username, FullName, Role, PhoneNumber, Address FROM Users WHERE FullName LIKE ? OR PhoneNumber LIKE ? OR Username LIKE ? ORDER BY ID DESC"
        
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query_pattern, query_pattern, query_pattern))
                rows = cursor.fetchall()

                self.users = []
                for row in rows:
                    self.users.append({
                        "id": row.ID, "username": row.Username or "", "full_name": row.FullName or "",
                        "role": row.Role or "", "phone_number": row.PhoneNumber or "", "address": row.Address or "",
                    })
                self.selected_user_ids = []
                self.all_selected = False
        except Exception as e:
            print(f"Lỗi khi tìm kiếm người dùng: {e}")

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.execute_search()

    # --- SETTERS ---
    def set_edited_phone_number(self, phone: str): self.edited_phone_number = phone
    def set_edited_address(self, address: str): self.edited_address = address
    def set_new_user_full_name(self, name: str): self.new_user_full_name = name
    def set_new_user_phone_number(self, phone: str): self.new_user_phone_number = phone
    def set_new_user_address(self, address: str): self.new_user_address = address
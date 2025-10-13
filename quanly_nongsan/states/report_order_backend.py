import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")

# Định nghĩa các cột cần lấy từ DB
CUSTOMER_COLUMNS = "ID, FullName, PhoneNumber, Address"


class ReportOrderState(rx.State):
    
    customers: list[dict] = []
    search_query: str = ""

    def load_customers(self):
        """
        Tải toàn bộ danh sách khách hàng (User) từ cơ sở dữ liệu.
        Chỉ lấy các cột: ID, FullName, PhoneNumber, Address.
        """
        self.customers = []  # Xóa danh sách cũ trước khi tải
        sql = f"""
            SELECT {CUSTOMER_COLUMNS}
            FROM Users 
            ORDER BY ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    self.customers.append(
                        {
                            "id": row.ID,
                            "full_name": row.FullName or "",
                            "phone_number": row.PhoneNumber or "",
                            "address": row.Address or "",
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải danh sách khách hàng: {e}")

    def set_search_query(self, query: str):
        """Đặt giá trị tìm kiếm và tải lại nếu chuỗi rỗng."""
        self.search_query = query
        if not query.strip():
            return self.load_customers()

    def execute_search(self):
        """
        Thực thi tìm kiếm khách hàng theo FullName hoặc PhoneNumber.
        Nếu chuỗi rỗng, tải lại toàn bộ.
        """
        if not self.search_query.strip():
            return self.load_customers()

        query_pattern = f"%{self.search_query.strip()}%"

        # Chỉ tìm kiếm theo FullName và PhoneNumber
        sql = f"""
            SELECT {CUSTOMER_COLUMNS}
            FROM Users 
            WHERE FullName LIKE ? OR PhoneNumber LIKE ?
            ORDER BY ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Truyền tham số tìm kiếm 2 lần (cho 2 cột)
                cursor.execute(sql, (query_pattern, query_pattern))
                rows = cursor.fetchall()

                # Cập nhật state customers với kết quả tìm kiếm
                self.customers = []
                for row in rows:
                    self.customers.append(
                        {
                            "id": row.ID,
                            "full_name": row.FullName or "",
                            "phone_number": row.PhoneNumber or "",
                            "address": row.Address or "",
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tìm kiếm khách hàng: {e}")
            return rx.window_alert(f"Lỗi cơ sở dữ liệu khi tìm kiếm: {e}")

    def search_on_enter(self, key: str):
        """Thực thi tìm kiếm khi nhấn phím Enter."""
        if key == "Enter":
            return self.execute_search()
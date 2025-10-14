import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class ReportOrderState(rx.State):
    
    customers: list[dict] = []
    search_query: str = ""

    def load_customers(self):
        """
        Tải danh sách khách hàng đã từng đặt hàng, cùng với tổng số đơn hàng của họ.
        """
        self.customers = []
        # Câu lệnh SQL đã được sửa lại với đúng tên cột
        sql = """
            SELECT
                u.ID,
                u.FullName,
                u.PhoneNumber,
                u.Address,
                COUNT(o.ID) as TotalOrders
            FROM
                Users u
            INNER JOIN
                Orders o ON u.ID = o.UserID -- SỬA Ở ĐÂY
            GROUP BY
                u.ID, u.FullName, u.PhoneNumber, u.Address
            ORDER BY
                u.ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for row in cursor.fetchall():
                    self.customers.append(
                        {
                            "id": row.ID,
                            "full_name": row.FullName or "",
                            "phone_number": row.PhoneNumber or "",
                            "address": row.Address or "",
                            "total_orders": row.TotalOrders,
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
        Thực thi tìm kiếm khách hàng đã đặt hàng theo Tên hoặc SĐT.
        """
        if not self.search_query.strip():
            return self.load_customers()

        query_pattern = f"%{self.search_query.strip()}%"
        # Câu lệnh tìm kiếm cũng được cập nhật tương tự
        sql = """
            SELECT
                u.ID,
                u.FullName,
                u.PhoneNumber,
                u.Address,
                COUNT(o.ID) as TotalOrders
            FROM
                Users u
            INNER JOIN
                Orders o ON u.ID = o.UserID -- SỬA Ở ĐÂY
            WHERE
                u.FullName LIKE ? OR u.PhoneNumber LIKE ?
            GROUP BY
                u.ID, u.FullName, u.PhoneNumber, u.Address
            ORDER BY
                u.ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query_pattern, query_pattern))
                
                self.customers = [] 
                for row in cursor.fetchall():
                    self.customers.append(
                        {
                            "id": row.ID,
                            "full_name": row.FullName or "",
                            "phone_number": row.PhoneNumber or "",
                            "address": row.Address or "",
                            "total_orders": row.TotalOrders,
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tìm kiếm khách hàng: {e}")
            return rx.window_alert(f"Lỗi cơ sở dữ liệu khi tìm kiếm: {e}")

    def search_on_enter(self, key: str):
        """Thực thi tìm kiếm khi nhấn phím Enter."""
        if key == "Enter":
            return self.execute_search()
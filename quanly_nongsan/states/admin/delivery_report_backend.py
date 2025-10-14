# states/admin/delivery_report_backend.py

import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")

# Dựa trên bảng dbo.Orders:
# ID (int), UserID (int), OrderDate (datetime2(7)), DeliveryDate (date), 
# Status (nvarchar(50)), Notes (nvarchar(500)), RecipientName (nvarchar(100)), 
# RecipientPhone (varchar(20)), ShippingAddress (nvarchar(MAX))

class DeliveryState(rx.State):
    orders: list[dict] = []
    search_query: str = ""

    # --- BIẾN STATE CHO CHỌN NHIỀU MỤC ---
    selected_order_ids: list[int] = []
    all_selected: bool = False
    
    # --- Biến cho form "Sửa" (Chỉ sửa Status/Notes/DeliveryDate) ---
    order_to_edit: dict | None = None
    edited_status: str = ""
    edited_notes: str = ""
    edited_delivery_date: str = "" # Dùng cho input type="date"

    # --- COMPUTED PROPERTIES (TÍNH TOÁN DỰA TRÊN STATE) ---
    @rx.var
    def is_only_one_selected(self) -> bool:
        """Kiểm tra xem chỉ có đúng một đơn hàng được chọn hay không."""
        return len(self.selected_order_ids) == 1

    @rx.var
    def order_to_edit_computed(self) -> dict | None:
        """Lấy thông tin đơn hàng duy nhất được chọn để hiển thị trong khung chỉnh sửa."""
        if self.is_only_one_selected:
            order_id = self.selected_order_ids[0]
            for order in self.orders:
                if order["id"] == order_id:
                    return order
        return None

    # --- TẢI DỮ LIỆU ---
    def load_orders(self):
        self.selected_order_ids = []
        self.all_selected = False
        self.orders = []
        
        # Lấy thêm UserName và FullName từ bảng Users để hiển thị thông tin người đặt hàng
        sql = """
            SELECT 
                o.ID, o.UserID, o.OrderDate, o.DeliveryDate, o.Status, o.Notes, 
                o.RecipientName, o.RecipientPhone, o.ShippingAddress, u.Username, u.FullName 
            FROM Orders o
            LEFT JOIN Users u ON o.UserID = u.ID
            ORDER BY o.OrderDate DESC, o.ID DESC -- ĐÃ CẬP NHẬT: Sắp xếp theo Ngày Đặt (mới nhất -> cũ nhất)
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    # Định dạng OrderDate và DeliveryDate thành chuỗi ngày và giờ
                    order_date_str = row.OrderDate.strftime("%Y-%m-%d %H:%M:%S") if row.OrderDate else ""
                    delivery_date_str = row.DeliveryDate.strftime("%Y-%m-%d %H:%M:%S") if row.DeliveryDate else ""
                    
                    self.orders.append({
                        "id": row.ID, "user_id": row.UserID, "username": row.Username or "",
                        "customer_name": row.FullName or "", 
                        "order_date": order_date_str, 
                        "delivery_date": delivery_date_str,
                        "status": row.Status or "", "notes": row.Notes or "",
                        "recipient_name": row.RecipientName or "", 
                        "recipient_phone": row.RecipientPhone or "", 
                        "shipping_address": row.ShippingAddress or "",
                    })
        except Exception as e:
            print(f"Lỗi khi tải danh sách đơn hàng: {e}")

    # --- HÀM XỬ LÝ CHỌN (CHECKBOX) ---
    def select_order(self, order: dict, checked: bool):
        order_id = order["id"]
        if checked:
            if order_id not in self.selected_order_ids:
                self.selected_order_ids.append(order_id)
        else:
            if order_id in self.selected_order_ids:
                self.selected_order_ids.remove(order_id)
        
        self.all_selected = (len(self.orders) > 0 and len(self.selected_order_ids) == len(self.orders))
        self._update_edit_fields()

    def select_all_orders(self, checked: bool):
        self.all_selected = checked
        if checked:
            self.selected_order_ids = [o['id'] for o in self.orders]
        else:
            self.selected_order_ids = []
        self._update_edit_fields()

    def select_single_order_for_edit(self, order: dict):
        """Chọn một đơn hàng duy nhất từ nút Sửa icon."""
        self.selected_order_ids = [order["id"]]
        self.all_selected = False
        self._update_edit_fields()

    def _update_edit_fields(self):
        """Hàm nội bộ để cập nhật các trường chỉnh sửa dựa trên lựa chọn."""
        if self.is_only_one_selected:
            order = self.order_to_edit_computed
            self.order_to_edit = order # Cập nhật biến State cho giao diện hiển thị
            self.edited_status = order.get("status", "")
            self.edited_notes = order.get("notes", "")
            
            # Lấy phần ngày (YYYY-MM-DD) từ chuỗi ngày giờ để điền vào input type="date"
            full_date_time = order.get("delivery_date", "")
            self.edited_delivery_date = full_date_time.split(" ")[0] if full_date_time else ""
        else:
            self.order_to_edit = None
            self.edited_status = ""
            self.edited_notes = ""
            self.edited_delivery_date = ""

    # --- HÀM SỬA / XÓA ---
    def update_order(self):
        if not self.is_only_one_selected:
            return
        
        order_id = self.selected_order_ids[0]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                sql = "UPDATE Orders SET Status = ?, Notes = ?, DeliveryDate = ? WHERE ID = ?"
                # Đảm bảo DeliveryDate là NULL nếu chuỗi rỗng
                delivery_date = self.edited_delivery_date.strip() if self.edited_delivery_date.strip() else None
                
                cursor.execute(sql, (self.edited_status.strip(), self.edited_notes.strip(), delivery_date, order_id))
                conn.commit()
            
            self.selected_order_ids = []
            self._update_edit_fields()
            self.load_orders()
            return rx.window_alert("Cập nhật thông tin đơn hàng thành công!")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi cập nhật: {e}")
        
    def delete_selected_orders(self):
        if not self.selected_order_ids:
            return
        
        id_list = tuple(self.selected_order_ids)
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(id_list))
                sql = f"DELETE FROM Orders WHERE ID IN ({placeholders})"
                cursor.execute(sql, id_list)
                conn.commit()
            
            self.selected_order_ids = []
            self._update_edit_fields()
            self.load_orders()
            return rx.window_alert(f"Đã xóa thành công {len(id_list)} đơn hàng.")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi xóa: {e}")

    def delete_order_by_id(self, order_id: int):
        """Xóa một đơn hàng từ nút Xóa icon."""
        self.selected_order_ids = [order_id]
        return self.delete_selected_orders()

    # --- TÌM KIẾM ---
    def set_search_query(self, query: str):
        self.search_query = query

    def execute_search(self):
        if not self.search_query.strip():
            self.load_orders()
            return

        query_pattern = f"%{self.search_query.strip()}%"
        
        # Tìm kiếm theo ID, Tên người nhận, SĐT người nhận, Địa chỉ, Trạng thái
        sql = """
            SELECT 
                o.ID, o.UserID, o.OrderDate, o.DeliveryDate, o.Status, o.Notes, 
                o.RecipientName, o.RecipientPhone, o.ShippingAddress, u.Username, u.FullName 
            FROM Orders o
            LEFT JOIN Users u ON o.UserID = u.ID
            WHERE CAST(o.ID AS nvarchar) LIKE ? OR o.RecipientName LIKE ? OR o.RecipientPhone LIKE ? OR o.ShippingAddress LIKE ? OR o.Status LIKE ?
            ORDER BY o.OrderDate DESC, o.ID DESC -- ĐÃ CẬP NHẬT: Sắp xếp theo Ngày Đặt (mới nhất -> cũ nhất)
        """
        
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query_pattern, query_pattern, query_pattern, query_pattern, query_pattern))
                rows = cursor.fetchall()

                self.orders = []
                for row in rows:
                    # Định dạng OrderDate và DeliveryDate thành chuỗi ngày và giờ
                    order_date_str = row.OrderDate.strftime("%Y-%m-%d %H:%M:%S") if row.OrderDate else ""
                    delivery_date_str = row.DeliveryDate.strftime("%Y-%m-%d %H:%M:%S") if row.DeliveryDate else ""
                    
                    self.orders.append({
                        "id": row.ID, "user_id": row.UserID, "username": row.Username or "",
                        "customer_name": row.FullName or "", 
                        "order_date": order_date_str, "delivery_date": delivery_date_str,
                        "status": row.Status or "", "notes": row.Notes or "",
                        "recipient_name": row.RecipientName or "", 
                        "recipient_phone": row.RecipientPhone or "", 
                        "shipping_address": row.ShippingAddress or "",
                    })
                self.selected_order_ids = []
                self.all_selected = False
        except Exception as e:
            print(f"Lỗi khi tìm kiếm đơn hàng: {e}")

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.execute_search()

    # --- SETTERS ---
    def set_edited_status(self, status: str): self.edited_status = status
    def set_edited_notes(self, notes: str): self.edited_notes = notes
    def set_edited_delivery_date(self, date: str): self.edited_delivery_date = date
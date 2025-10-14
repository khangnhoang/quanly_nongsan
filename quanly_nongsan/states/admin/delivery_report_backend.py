import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

from ..admin.login_backend import State as LoginState

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")

STATUS_MAP = {
    "pending": {"text": "Chờ xác nhận", "color": "orange"},
    "processing": {"text": "Đang xử lý", "color": "blue"},
    "delivered": {"text": "Giao thành công", "color": "green"},
    "cancelled": {"text": "Đã hủy", "color": "red"},
}
DEFAULT_STATUS = {"text": "Không xác định", "color": "gray"}


class DeliveryState(rx.State):
    orders: list[dict] = []
    search_query: str = ""
    selected_order_ids: list[int] = []
    all_selected: bool = False
    order_to_edit: dict | None = None
    edited_status: str = ""
    edited_notes: str = ""
    edited_delivery_date: str = ""
    total_orders: int = 0
    delivered_today_count: int = 0
    overdue_count: int = 0

    @rx.var
    def is_only_one_selected(self) -> bool:
        return len(self.selected_order_ids) == 1

    @rx.var
    def status_options(self) -> list[list[str]]:
        return [[status["text"], key] for key, status in STATUS_MAP.items()]

    @rx.var
    def is_editing_disabled(self) -> bool:
        if not self.order_to_edit or not self.order_to_edit.get("delivery_date"):
            return False
        try:
            delivery_date = datetime.fromisoformat(self.order_to_edit["delivery_date"])
            return delivery_date < datetime.now()
        except (ValueError, TypeError):
            return False

    def on_load(self):
        self.load_orders()
        self.load_dashboard_stats()

    def load_dashboard_stats(self):
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Orders")
                self.total_orders = cursor.fetchone()[0] or 0
                cursor.execute(
                    "SELECT COUNT(*) FROM Orders WHERE Status = 'delivered' AND CAST(DeliveryDate AS DATE) = CAST(GETDATE() AS DATE)"
                )
                self.delivered_today_count = cursor.fetchone()[0] or 0
                cursor.execute(
                    "SELECT COUNT(*) FROM Orders WHERE Status IN ('pending', 'processing') AND DeliveryDate < GETDATE()"
                )
                self.overdue_count = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"Lỗi khi tải thống kê: {e}")

    def load_orders(self):
        self.orders = []
        sql = "SELECT o.ID, o.OrderDate, o.DeliveryDate, o.Status, o.Notes, o.RecipientName, o.RecipientPhone, o.ShippingAddress FROM Orders o ORDER BY o.DeliveryDate ASC"
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for row in cursor.fetchall():
                    status_info = STATUS_MAP.get(row.Status, DEFAULT_STATUS)
                    self.orders.append(
                        {
                            "id": row.ID,
                            "order_date": (
                                row.OrderDate.strftime("%d/%m/%Y %H:%M")
                                if row.OrderDate
                                else ""
                            ),
                            "delivery_date": (
                                row.DeliveryDate.isoformat() if row.DeliveryDate else ""
                            ),
                            "delivery_date_formatted": (
                                row.DeliveryDate.strftime("%d/%m/%Y %H:%M")
                                if row.DeliveryDate
                                else "Chưa có"
                            ),
                            "status_key": row.Status or "",
                            "status_text": status_info["text"],
                            "status_color": status_info["color"],
                            "notes": row.Notes or "",
                            "recipient_name": row.RecipientName or "",
                            "recipient_phone": row.RecipientPhone or "",
                            "shipping_address": row.ShippingAddress or "",
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải danh sách đơn hàng: {e}")

    def _update_edit_fields(self):
        if self.is_only_one_selected:
            order_id = self.selected_order_ids[0]
            order = next((o for o in self.orders if o["id"] == order_id), None)
            if order:
                self.order_to_edit = order
                self.edited_status = order.get("status_key", "")
                self.edited_notes = order.get("notes", "")
                iso_date = order.get("delivery_date", "")
                self.edited_delivery_date = iso_date.split("T")[0] if iso_date else ""
            else:
                self.order_to_edit = None
                self.edited_status = ""
                self.edited_notes = ""
                self.edited_delivery_date = ""
        else:
            self.order_to_edit = None
            self.edited_status = ""
            self.edited_notes = ""
            self.edited_delivery_date = ""

    def select_order(self, order: dict, checked: bool):
        order_id = order["id"]
        if checked:
            if order_id not in self.selected_order_ids:
                self.selected_order_ids.append(order_id)
        else:
            if order_id in self.selected_order_ids:
                self.selected_order_ids.remove(order_id)
        self.all_selected = len(self.orders) > 0 and len(
            self.selected_order_ids
        ) == len(self.orders)
        self._update_edit_fields()

    def select_all_orders(self, checked: bool):
        """Chọn hoặc bỏ chọn tất cả các đơn hàng."""
        self.all_selected = checked
        if checked:
            # Nếu chọn tất cả, thêm ID của tất cả các đơn hàng vào danh sách
            self.selected_order_ids = [order["id"] for order in self.orders]
        else:
            # Nếu bỏ chọn tất cả, xóa sạch danh sách
            self.selected_order_ids = []
        
        # Cập nhật các trường chỉnh sửa sau khi thay đổi lựa chọn
        self._update_edit_fields()

    def select_single_order_for_edit(self, order: dict):
        self.selected_order_ids = [order["id"]]
        self.all_selected = False
        self._update_edit_fields()

    def update_order(self):
        if self.is_editing_disabled:
            return rx.window_alert("Đơn hàng đã quá hạn giao, không thể cập nhật!")
        if not self.is_only_one_selected:
            return
        order_id = self.selected_order_ids[0]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                sql = "UPDATE Orders SET Status = ?, Notes = ?, DeliveryDate = ? WHERE ID = ?"
                cursor.execute(
                    sql,
                    (
                        self.edited_status,
                        self.edited_notes,
                        self.edited_delivery_date or None,
                        order_id,
                    ),
                )
                conn.commit()
            self.selected_order_ids = []
            self._update_edit_fields()
            self.on_load()
            return rx.window_alert("Cập nhật thành công!")
        except Exception as e:
            return rx.window_alert(f"Lỗi khi cập nhật: {e}")

    # Các hàm còn lại giữ nguyên
    def set_search_query(self, query: str):
        self.search_query = query

    def execute_search(self):
        pass  # Implement search logic here

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.execute_search()

    def set_edited_status(self, status: str):
        self.edited_status = status

    def set_edited_notes(self, notes: str):
        self.edited_notes = notes

    def set_edited_delivery_date(self, date: str):
        self.edited_delivery_date = date

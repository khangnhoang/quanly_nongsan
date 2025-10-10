# C:\quanly_nongsan\quanly_nongsan\states\order_history_backend.py
import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from .login_backend import State as LoginState

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")

STATUS_MAP = {
    "1": {"text": "Chờ xác nhận", "color": "orange"},
    "Mới": {"text": "Mới", "color": "blue"},
    "Giao thành công": {"text": "Giao thành công", "color": "green"},
    "Đã hủy": {"text": "Đã hủy", "color": "red"},
}
DEFAULT_STATUS = {"text": "Không xác định", "color": "gray"}


class Order(rx.Base):
    id: str
    status_text: str
    status_color: str
    product_images: list[str]
    total_price_formatted: str


class OrderHistoryState(rx.State):
    orders: list[Order] = []
    is_loading: bool = False

    @rx.var
    def has_orders(self) -> bool:
        return len(self.orders) > 0

    async def bootstrap_after_login(self):
        """Đợi LoginState.current_user có id rồi mới load_orders."""
        login = await self.get_state(LoginState)
        user_id = login.current_user.get("id") if isinstance(login.current_user, dict) else None
        if not user_id:
            # Poll nhẹ 50ms cho đến khi hydrate xong
            return rx.call_script("setTimeout(()=>true, 50)", callback=type(self).bootstrap_after_login)
        return self.load_orders

    async def load_orders(self):
        self.is_loading = True
        login_state = await self.get_state(LoginState)
        user_id = login_state.current_user.get("id")

        if not user_id:
            self.orders = []
            self.is_loading = False
            return rx.redirect("/login_page")

        temp_orders: list[Order] = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT ID, OrderDate, Status FROM Orders WHERE UserID = ? ORDER BY OrderDate DESC",
                    (user_id,),
                )
                user_orders = cursor.fetchall()

                for order_row in user_orders:
                    order_id = order_row.ID
                    cursor.execute(
                        """
                        SELECT oi.Quantity, p.Price, i.ImageURL
                        FROM OrderItems oi
                        JOIN Products p ON oi.ProductID = p.ID
                        LEFT JOIN Images i ON p.PrimaryImageID = i.STT
                        WHERE oi.OrderID = ?
                        """,
                        (order_id,),
                    )
                    order_items = cursor.fetchall()

                    total_price = 0
                    product_images: list[str] = []
                    for item in order_items:
                        total_price += int(item.Quantity) * int(item.Price)
                        if len(product_images) < 4:
                            product_images.append(item.ImageURL or "/no-image.png")

                    status_info = STATUS_MAP.get(str(order_row.Status), DEFAULT_STATUS)

                    temp_orders.append(
                        Order(
                            id=f"{order_id:08X}",
                            status_text=status_info["text"],
                            status_color=status_info["color"],
                            product_images=product_images,
                            total_price_formatted=f"{int(total_price):,} đ".replace(",", "."),
                        )
                    )
            self.orders = temp_orders
        except Exception as e:
            print(f"Lỗi khi tải lịch sử đơn hàng: {e}")
        self.is_loading = False

    # Tuỳ chọn: nút "Mua lại"
    def reorder(self, order_id: str):
        return rx.window_alert(f"Chức năng 'Mua lại' cho đơn #{order_id} sẽ sớm được hỗ trợ.")

import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
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


class Order(rx.Base):
    id: str
    status_text: str
    status_color: str
    product_images: list[str]
    total_price_formatted: str
    # THÊM TRƯỜNG MỚI ĐỂ HIỂN THỊ
    delivery_date_formatted: str


class OrderHistoryState(rx.State):
    orders: list[Order] = []
    is_loading: bool = False

    @rx.var
    def has_orders(self) -> bool:
        return len(self.orders) > 0

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
                # CẬP NHẬT CÂU LỆNH SQL: Lấy thêm cột DeliveryDate
                cursor.execute(
                    "SELECT ID, OrderDate, Status, DeliveryDate FROM Orders WHERE UserID = ? ORDER BY OrderDate DESC",
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

                    # CẬP NHẬT LOGIC: Định dạng ngày giờ giao hàng
                    delivery_datetime = order_row.DeliveryDate
                    delivery_date_formatted = ""
                    if delivery_datetime:
                        hour = delivery_datetime.hour
                        day = delivery_datetime.strftime("%d/%m/%Y")
                        delivery_date_formatted = f"Giao trước {hour}:00 - {day}"

                    status_info = STATUS_MAP.get(str(order_row.Status), DEFAULT_STATUS)

                    temp_orders.append(
                        Order(
                            id=f"{order_id:08X}",
                            status_text=status_info["text"],
                            status_color=status_info["color"],
                            product_images=product_images,
                            total_price_formatted=f"{int(total_price):,} đ".replace(",", "."),
                            # Gán giá trị đã định dạng vào đối tượng Order
                            delivery_date_formatted=delivery_date_formatted,
                        )
                    )
            self.orders = temp_orders
        except Exception as e:
            print(f"Lỗi khi tải lịch sử đơn hàng: {e}")
        self.is_loading = False

    def reorder(self, order_id: str):
        return rx.redirect(f"/product_detail?order_id={order_id}")
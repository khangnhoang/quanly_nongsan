# C:\quanly_nongsan\quanly_nongsan\states\product_detail_backend.py
import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from .cart_backend import CartState # <-- THÊM IMPORT NÀY

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class OrderItem(rx.Base):
    """Định nghĩa cấu trúc cho một sản phẩm trong đơn hàng chi tiết."""
    product_id: int # <-- THÊM TRƯỜNG NÀY (ĐÃ CÓ TRONG FILE GỐC)
    product_name: str
    image_url: str
    quantity: int
    unit_price_formatted: str


class ProductDetailState(rx.State):
    """State quản lý logic cho trang chi tiết đơn hàng."""
    order_id: str = ""
    order_items: list[OrderItem] = []
    grand_total: str = ""
    is_loading: bool = False

    async def load_order_details(self):
        """Tải chi tiết các sản phẩm của một đơn hàng dựa vào order_id từ URL."""
        self.is_loading = True
        self.order_id = self.router.page.params.get("order_id", "")
        if not self.order_id:
            print("Không tìm thấy order_id trong URL.")
            self.is_loading = False
            return

        try:
            order_id_int = int(self.order_id, 16)
        except ValueError:
            print(f"order_id không hợp lệ: {self.order_id}")
            self.is_loading = False
            return

        temp_items = []
        total_price = 0
        
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        p.ID,  -- <-- THÊM p.ID VÀO ĐÂY (ĐÃ CÓ TRONG FILE GỐC)
                        p.Name, 
                        i.ImageURL, 
                        oi.Quantity, 
                        p.Price
                    FROM OrderItems oi
                    JOIN Products p ON oi.ProductID = p.ID
                    LEFT JOIN Images i ON p.PrimaryImageID = i.STT
                    WHERE oi.OrderID = ?
                    """,
                    (order_id_int,),
                )
                items_in_order = cursor.fetchall()

                for item in items_in_order:
                    total_price += item.Quantity * item.Price
                    temp_items.append(
                        OrderItem(
                            product_id=item.ID, # <-- LƯU PRODUCT ID VÀO MODEL (ĐÃ CÓ TRONG FILE GỐC)
                            product_name=item.Name,
                            image_url=item.ImageURL or "/no-image.png",
                            quantity=item.Quantity,
                            unit_price_formatted=f"{int(item.Price):,} đ".replace(",", "."),
                        )
                    )

            self.order_items = temp_items
            self.grand_total = f"{int(total_price):,} đ".replace(",", ".")

        except Exception as e:
            print(f"Lỗi khi tải chi tiết đơn hàng: {e}")

        self.is_loading = False

    def reorder_from_detail(self):
        """Chức năng 'Mua lại' trên trang chi tiết: thêm tất cả sản phẩm vào giỏ hàng."""
        
        # Tạo danh sách các cặp (product_id, quantity)
        items_to_reorder = [
            (item.product_id, item.quantity) for item in self.order_items
        ]
        
        return [
            # Gọi hàm mới trong CartState (giả định đã được triển khai)
            CartState.add_multiple_items_to_cart(items_to_reorder),
            rx.window_alert(f"Đang thêm {len(items_to_reorder)} sản phẩm vào giỏ hàng..."),
            rx.redirect("/cart")
        ]
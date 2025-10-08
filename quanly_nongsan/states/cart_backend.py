# cart_backend.py
import reflex as rx
import pyodbc
import os

from .login_backend import State as LoginState  # điều chỉnh import cho đúng đường dẫn
CONNECTION_STRING = os.getenv("DATABASE_URL")

class CartState(rx.State):
    items: list[dict] = []
    total: int = 0

    @rx.var
    def has_items(self) -> bool:
        return len(self.items) > 0

    async def load_cart(self):
        """Lấy giỏ hàng của user hiện tại."""
        login_state = await self.get_state(LoginState)
        user_id = login_state.current_user.get("id")
        if not user_id:
            # chưa đăng nhập → báo & điều hướng
            return [
                rx.window_alert("Bạn phải đăng nhập để xem giỏ hàng!"),
                rx.redirect("/login_page"),
            ]

        tmp = []
        total = 0
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Lấy các item trong giỏ: tên SP, giá, số lượng, ảnh
                cursor.execute(
                    """
                    SELECT ci.CartItemID,
                           p.ID       AS ProductID,
                           p.Name,
                           p.Price,
                           ci.Quantity,
                           i.ImageURL
                    FROM Carts c
                    JOIN CartItems ci ON c.CartID = ci.CartID
                    JOIN Products p   ON p.ID = ci.ProductID
                    LEFT JOIN Images i ON p.PrimaryImageID = i.STT
                    WHERE c.UserID = ?
                    ORDER BY ci.CartItemID DESC
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
                for r in rows:
                    line_total = int(r.Price) * int(r.Quantity)
                    total += line_total
                    tmp.append(
                        {
                            "cart_item_id": r.CartItemID,
                            "product_id": r.ProductID,
                            "name": r.Name,
                            "price": int(r.Price),
                            "quantity": int(r.Quantity),
                            "image_url": r.ImageURL or "/no-image.png",
                            "line_total": line_total,
                        }
                    )
        except Exception as e:
            print(f"Lỗi load_cart: {e}")

        self.items = tmp
        self.total = total

    def increment_item(self, cart_item_id: int):
        """Tăng số lượng 1 item (demo – bạn có thể gắn SQL UPDATE)."""
        for it in self.items:
            if it["cart_item_id"] == cart_item_id:
                it["quantity"] += 1
                it["line_total"] = it["quantity"] * it["price"]
                break
        self.total = sum(it["line_total"] for it in self.items)

    def decrement_item(self, cart_item_id: int):
        for it in self.items:
            if it["cart_item_id"] == cart_item_id and it["quantity"] > 1:
                it["quantity"] -= 1
                it["line_total"] = it["quantity"] * it["price"]
                break
        self.total = sum(it["line_total"] for it in self.items)

    def clear_cart(self):
        """Xóa hết trong giỏ (demo – gắn SQL DELETE nếu muốn)."""
        self.items = []
        self.total = 0

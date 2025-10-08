# cart_backend.py
import reflex as rx
import pyodbc
import os

from .login_backend import State as LoginState

CONNECTION_STRING = os.getenv("DATABASE_URL")


class CartState(rx.State):
    items: list[dict] = []
    total: int = 0

    @rx.var
    def has_items(self) -> bool:
        return len(self.items) > 0

    async def _get_user_id(self) -> int | None:
        login_state = await self.get_state(LoginState)
        return login_state.current_user.get("id")

    async def _get_cart_id(self, conn, user_id: int) -> int | None:
        cur = conn.cursor()
        cur.execute("SELECT CartID FROM Carts WHERE UserID = ?", (user_id,))
        row = cur.fetchone()
        return row.CartID if row else None

    async def load_cart(self):
        user_id = await self._get_user_id()
        if not user_id:
            return [
                rx.window_alert("Bạn phải đăng nhập để xem giỏ hàng!"),
                rx.redirect("/login_page"),
            ]

        tmp = []
        total = 0
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cur = conn.cursor()
                cur.execute(
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
                for r in cur.fetchall():
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

    # +1 số lượng
    async def increment_item(self, cart_item_id: int):
        user_id = await self._get_user_id()
        if not user_id:
            return [rx.window_alert("Bạn cần đăng nhập!"), rx.redirect("/login_page")]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cur = conn.cursor()
                # Chỉ update item thuộc cart của user
                cur.execute(
                    """
                    UPDATE ci SET Quantity = Quantity + 1
                    FROM CartItems ci
                    JOIN Carts c ON c.CartID = ci.CartID
                    WHERE ci.CartItemID = ? AND c.UserID = ?
                    """,
                    (cart_item_id, user_id),
                )
                conn.commit()
        except Exception as e:
            print(f"increment_item error: {e}")
        # reload lại state
        return type(self).load_cart()

    # -1 số lượng; nếu =1 thì xóa khỏi giỏ
    async def decrement_item(self, cart_item_id: int):
        user_id = await self._get_user_id()
        if not user_id:
            return [rx.window_alert("Bạn cần đăng nhập!"), rx.redirect("/login_page")]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cur = conn.cursor()
                # Lấy qty hiện tại (và thuộc user)
                cur.execute(
                    """
                    SELECT ci.Quantity
                    FROM CartItems ci
                    JOIN Carts c ON c.CartID = ci.CartID
                    WHERE ci.CartItemID = ? AND c.UserID = ?
                    """,
                    (cart_item_id, user_id),
                )
                row = cur.fetchone()
                if not row:
                    return
                qty = int(row.Quantity)
                if qty <= 1:
                    # Xóa luôn item
                    cur.execute(
                        """
                        DELETE ci
                        FROM CartItems ci
                        JOIN Carts c ON c.CartID = ci.CartID
                        WHERE ci.CartItemID = ? AND c.UserID = ?
                        """,
                        (cart_item_id, user_id),
                    )
                else:
                    # Giảm số lượng
                    cur.execute(
                        """
                        UPDATE ci SET Quantity = Quantity - 1
                        FROM CartItems ci
                        JOIN Carts c ON c.CartID = ci.CartID
                        WHERE ci.CartItemID = ? AND c.UserID = ?
                        """,
                        (cart_item_id, user_id),
                    )
                conn.commit()
        except Exception as e:
            print(f"decrement_item error: {e}")
        return type(self).load_cart()

    # Xóa 1 dòng theo CartItemID
    async def delete_item(self, cart_item_id: int):
        user_id = await self._get_user_id()
        if not user_id:
            return [rx.window_alert("Bạn cần đăng nhập!"), rx.redirect("/login_page")]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    DELETE ci
                    FROM CartItems ci
                    JOIN Carts c ON c.CartID = ci.CartID
                    WHERE ci.CartItemID = ? AND c.UserID = ?
                    """,
                    (cart_item_id, user_id),
                )
                conn.commit()
        except Exception as e:
            print(f"delete_item error: {e}")
        return type(self).load_cart()

    # Xóa hết giỏ của user
    async def clear_cart(self):
        user_id = await self._get_user_id()
        if not user_id:
            return [rx.window_alert("Bạn cần đăng nhập!"), rx.redirect("/login_page")]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    DELETE ci
                    FROM CartItems ci
                    JOIN Carts c ON c.CartID = ci.CartID
                    WHERE c.UserID = ?
                    """,
                    (user_id,),
                )
                conn.commit()
        except Exception as e:
            print(f"clear_cart error: {e}")
        return type(self).load_cart()

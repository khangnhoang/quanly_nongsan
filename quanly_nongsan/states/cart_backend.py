import reflex as rx
import pyodbc
import os

from .login_backend import State as LoginState

CONNECTION_STRING = os.getenv("DATABASE_URL")


class CartState(rx.State):
    items: list[dict] = []
    total: int = 0
    
    # THÔNG TIN KHÁCH HÀNG (Lấy từ DB Users)
    user_full_name: str = ""
    user_phone: str = ""
    user_address: str = ""
    
    is_loading: bool = False
    
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
                
                # 1. LẤY THÔNG TIN USER TỪ DB (FullName, PhoneNumber, Address)
                cur.execute(
                    """
                    SELECT FullName, PhoneNumber, Address
                    FROM Users
                    WHERE ID = ?
                    """,
                    (user_id,)
                )
                user_row = cur.fetchone()
                if user_row:
                    self.user_full_name = user_row.FullName or ""
                    self.user_phone = user_row.PhoneNumber or ""
                    self.user_address = user_row.Address or ""
                
                # 2. LẤY DANH SÁCH SẢN PHẨM TRONG GIỎ
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

    async def place_order(self):
            self.is_loading = True
            
            user_id = await self._get_user_id()
            if not user_id:
                self.is_loading = False
                return [rx.window_alert("Bạn cần đăng nhập!"), rx.redirect("/login_page")]
            if not self.items:
                self.is_loading = False
                return rx.window_alert("Giỏ hàng của bạn đang trống!")
            
            # KIỂM TRA THÔNG TIN USER TỪ DB
            if not self.user_full_name or not self.user_phone or not self.user_address:
                self.is_loading = False
                return rx.window_alert("Vui lòng cập nhật đầy đủ Họ tên, SĐT và Địa chỉ trong hồ sơ trước khi đặt hàng!")

            try:
                with pyodbc.connect(CONNECTION_STRING) as conn:
                    cur = conn.cursor() 

                    try:
                        # 3. TẠO ĐƠN HÀNG MỚI (Orders)
                        cur.execute(
                            """
                            INSERT INTO Orders 
                            (UserID, OrderDate, Status, RecipientName, RecipientPhone, ShippingAddress)
                            OUTPUT INSERTED.ID
                            VALUES (?, GETDATE(), ?, ?, ?, ?)
                            """,
                            (
                                user_id,
                                1, # 1 là trạng thái: Chờ xác nhận
                                self.user_full_name,
                                self.user_phone,
                                self.user_address,
                            ),
                        )
                        order_id = cur.fetchone()[0]

                        # 4. THÊM CÁC MẶT HÀNG VÀO CHI TIẾT ĐƠN HÀNG (OrderItems)
                        for item in self.items:
                            cur.execute(
                                """
                                INSERT INTO OrderItems (OrderID, ProductID, Quantity)
                                VALUES (?, ?, ?)
                                """,
                                (
                                    order_id,
                                    item["product_id"],
                                    item["quantity"],
                                ),
                            )

                        # 5. XÓA TẤT CẢ SẢN PHẨM TRONG GIỎ HÀNG CỦA USER (CartItems)
                        cur.execute(
                            "SELECT CartID FROM Carts WHERE UserID = ?", (user_id,)
                        )
                        cart_id = cur.fetchone()[0]
                        
                        cur.execute(
                            "DELETE FROM CartItems WHERE CartID = ?", (cart_id,)
                        )
                        
                        conn.commit()
                        
                        # Reset state: CHỈ CẦN RESET items VÀ total.
                        self.items = []
                        self.total = 0
                        
                        self.is_loading = False

                        return [
                            rx.window_alert("Đặt hàng thành công!"),
                            rx.redirect("/") 
                        ]

                    except Exception as e:
                        print(f"Lỗi trong transaction, đang rollback: {e}")
                        conn.rollback()
                        self.is_loading = False
                        return rx.window_alert(f"Đã xảy ra lỗi khi đặt hàng: {e}")

            except Exception as e:
                print(f"Lỗi kết nối CSDL khi đặt hàng: {e}")
                self.is_loading = False
                return rx.window_alert("Lỗi hệ thống, vui lòng thử lại sau.")
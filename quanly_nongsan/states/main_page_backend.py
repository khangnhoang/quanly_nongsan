import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from .login_backend import State as LoginState

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class MainPageState(rx.State):

    product_types_with_images: list[dict] = []
    recently_purchased_products: list[dict] = []
    products: list[dict] = []
    LoginState = LoginState

    async def check_login_and_add_to_cart(self, product: dict):
        login_state = await self.get_state(LoginState)

        if "id" not in login_state.current_user:
            yield rx.window_alert("Bạn phải đăng nhập để mua hàng!")
            yield rx.redirect("/login_page")
            return

        try:
            user_id = int(login_state.current_user["id"])
            product_id = int(product.get("id"))
            product_name = product.get("name", "Sản phẩm")

            with pyodbc.connect(CONNECTION_STRING) as conn:
                conn.autocommit = False
                cursor = conn.cursor()

                # B1: Tìm (hoặc tạo) giỏ
                cursor.execute("SELECT CartID FROM Carts WHERE UserID = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    cart_id = row.CartID
                else:
                    cursor.execute(
                        "INSERT INTO Carts (UserID) OUTPUT INSERTED.CartID VALUES (?)",
                        (user_id,),
                    )
                    cart_id = cursor.fetchone()[0]
                    conn.commit()  # hoặc để commit chung phía dưới cũng được

                # B2: Thêm/cộng dồn
                cursor.execute(
                    "SELECT CartItemID, Quantity FROM CartItems WHERE CartID = ? AND ProductID = ?",
                    (cart_id, product_id),
                )
                item_row = cursor.fetchone()
                if item_row:
                    cursor.execute(
                        "UPDATE CartItems SET Quantity = ? WHERE CartItemID = ?",
                        (item_row.Quantity + 1, item_row.CartItemID),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO CartItems (CartID, ProductID, Quantity) VALUES (?, ?, 1)",
                        (cart_id, product_id),
                    )

                conn.commit()
                yield rx.window_alert(f"Đã thêm '{product_name}' vào giỏ hàng!")
                return

        except Exception as e:
            print(f"Lỗi khi thêm vào giỏ hàng: {e}")
            try:
                conn.rollback()
            except:
                pass
            yield rx.window_alert("Đã xảy ra lỗi khi thêm sản phẩm vào giỏ hàng.")


    def load_products(self):
        """
        Lấy danh sách sản phẩm (Tên, Giá, Ảnh đại diện) từ database.
        """
        temp_products = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()

                # Câu query để lấy thông tin sản phẩm và ảnh đại diện
                # Chúng ta dùng LEFT JOIN để vẫn lấy được sản phẩm dù nó không có ảnh
                query = """
                    SELECT TOP 12
                        p.ID,
                        p.Name,
                        p.Price,
                        i.ImageURL
                    FROM 
                        Products p
                    LEFT JOIN 
                        Images i ON p.PrimaryImageID = i.STT
                    ORDER BY
                        p.ID DESC; 
                """
                # ORDER BY p.ID DESC để lấy các sản phẩm mới nhất

                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    # Định dạng lại giá tiền cho đẹp hơn (ví dụ: 60000 -> 60.000 đ)
                    formatted_price = f"{int(row.Price):,} đ".replace(",", ".")

                    temp_products.append(
                        {
                            "id": row.ID,
                            "name": row.Name,
                            "price": formatted_price,
                            "image_url": (
                                row.ImageURL if row.ImageURL else "/no-image.png"
                            ),  # Dùng ảnh mặc định nếu không có
                        }
                    )

            # Cập nhật state với danh sách sản phẩm
            self.products = temp_products

        except Exception as e:
            print(f"Lỗi khi tải danh sách sản phẩm: {e}")

    # --- KẾT THÚC PHẦN MỚI ---

    def load_product_types(self):
        """
        Lấy tất cả các loại sản phẩm và tìm một ảnh đại diện cho mỗi loại.
        Ảnh đại diện được tìm dựa trên quy tắc tên file chứa 'loai_'.
        """
        temp_list = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()

                # B1: Lấy tất cả các loại sản phẩm (tên và mã)
                cursor.execute("SELECT Code, Name FROM ProductTypes")
                product_types = cursor.fetchall()

                for pt in product_types:
                    # B2: Với mỗi loại, tìm MỘT ảnh đại diện trong bảng Images
                    # Dùng TOP 1 để chỉ lấy ảnh đầu tiên tìm thấy
                    # Dựa theo quy tắc của bạn: imageurl like '%loai%' và thêm mã code để chính xác hơn
                    image_query = "SELECT TOP 1 ImageURL FROM Images WHERE ImageURL LIKE ? ORDER BY STT"

                    # Pattern tìm kiếm, ví dụ: %/loai_RAUCU%
                    # Điều này giả định bạn đặt tên file ảnh là /loai_CODE.jpg
                    search_pattern = f"%/loai_{pt.Code}%"

                    cursor.execute(image_query, search_pattern)
                    image_row = cursor.fetchone()

                    image_url = "/no-image.png"  # Ảnh mặc định nếu không tìm thấy
                    if image_row:
                        image_url = image_row.ImageURL

                    # Thêm vào danh sách tạm thời
                    temp_list.append({"name": pt.Name, "image_url": image_url})

            # B3: Cập nhật state với dữ liệu đã lấy được
            self.product_types_with_images = temp_list

        except Exception as e:
            print(f"Lỗi khi tải loại sản phẩm: {e}")

    async def load_recently_purchased_products(self):
        # Lấy User ID từ Login State
        user_id_obj = await self.get_state(self.LoginState)
        user_id = user_id_obj.current_user.get("id")

        # Không log, không clear list, chỉ bỏ qua nếu chưa có user
        if not user_id:
            return

        temp_list = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT DISTINCT 
                        p.ID, 
                        p.Name, 
                        p.Price, 
                        i.ImageURL
                    FROM Orders o
                    JOIN OrderItems oi ON o.ID = oi.OrderID
                    JOIN Products p ON oi.ProductID = p.ID
                    LEFT JOIN Images i ON p.PrimaryImageID = i.STT
                    WHERE o.UserID = ?
                    ORDER BY p.ID DESC
                    """,
                    (user_id,)
                )
                for row in cursor.fetchall():
                    temp_list.append({
                        "id": row.ID,
                        "name": row.Name,
                        "price": f"{int(row.Price):,} đ".replace(",", "."),
                        "image_url": row.ImageURL or "/no-image.png",
                        "product_id": row.ID
                    })

            self.recently_purchased_products = temp_list
        except Exception as e:
            print(f"Lỗi khi tải sản phẩm đã mua: {e}")
            # Không clear list trong trường hợp lỗi, để tránh mất dữ liệu đang hiển thị
            # self.recently_purchased_products = []

import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from ..admin.login_backend import State as LoginState

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class MainPageState(rx.State):

    product_types_with_images: list[dict] = []
    recently_purchased_products: list[dict] = []
    products: list[dict] = []
    LoginState = LoginState
    
    # --- BỔ SUNG STATE CHO MODAL & SỐ LƯỢNG MỚI ---
    selected_product_for_cart: dict = {}
    show_add_to_cart_modal: bool = False
    quantity_to_add: int = 1  # <--- BỔ SUNG: State lưu số lượng
    # -----------------------------------------------

    def set_show_add_to_cart_modal(self, value: bool):
        self.show_add_to_cart_modal = value

    def close_add_to_cart_modal(self):
        self.show_add_to_cart_modal = False
        self.selected_product_for_cart = {} 
        self.quantity_to_add = 1 # Reset số lượng khi đóng modal

    # --- HÀM MỚI: TĂNG GIẢM SỐ LƯỢNG TRONG MODAL ---
    def increase_quantity(self):
        self.quantity_to_add += 1

    def decrease_quantity(self):
        if self.quantity_to_add > 1:
            self.quantity_to_add -= 1

    def set_quantity_to_add(self, value: str):
        """Cập nhật số lượng từ input, chỉ chấp nhận số nguyên dương."""
        try:
            int_value = int(value)
            if int_value >= 1:
                self.quantity_to_add = int_value
        except ValueError:
            # Tùy chọn: Bạn có thể giữ nguyên giá trị cũ hoặc đặt lại là 1 nếu lỗi
            pass
    # -----------------------------------------------------

    # --- HÀM 1: GỌI TỪ NÚT BẤM UI (ĐÃ CẬP NHẬT) ---
    async def check_login_and_add_to_cart(self, product: dict):
        """Kiểm tra đăng nhập, sau đó lưu sản phẩm, khởi tạo số lượng và mở modal."""
        login_state = await self.get_state(LoginState)
        
        # B1: Kiểm tra đăng nhập
        if "id" not in login_state.current_user:
            yield rx.window_alert("Bạn phải đăng nhập để mua hàng!")
            yield rx.redirect("/login_page")
            return
        
        # B2: Nếu đã đăng nhập, lưu sản phẩm, đặt số lượng mặc định và mở modal
        self.selected_product_for_cart = product
        self.quantity_to_add = 1 # Khởi tạo số lượng
        self.show_add_to_cart_modal = True

    # --- HÀM 2: GỌI TỪ NÚT XÁC NHẬN TRONG MODAL (CHẠY LOGIC DB) ---
    async def add_selected_product_to_cart(self):
        """Được gọi khi người dùng nhấn nút 'HOÀN TẤT' trong modal."""
        # Gọi hàm logic thêm vào giỏ hàng
        # Truyền cả sản phẩm và số lượng
        yield MainPageState.add_to_cart_logic(
            self.selected_product_for_cart, 
            self.quantity_to_add
        )
        
        # Đóng modal sau khi thêm
        self.close_add_to_cart_modal()


    # --- HÀM 3: LOGIC THÊM VÀO DB (ĐÃ CẬP NHẬT ĐỂ SỬ DỤNG SỐ LƯỢNG) ---
    # *THAY ĐỔI: Thêm đối số quantity và sử dụng nó trong truy vấn SQL*
    async def add_to_cart_logic(self, product: dict, quantity: int):
        """Logic xử lý DB: Thêm hoặc cập nhật số lượng sản phẩm trong CSDL."""
        login_state = await self.get_state(LoginState)

        # Đảm bảo số lượng hợp lệ
        if quantity < 1:
            yield rx.window_alert("Số lượng phải lớn hơn hoặc bằng 1.")
            return

        user_id = int(login_state.current_user["id"])
        product_id = int(product.get("id"))
        product_name = product.get("name", "Sản phẩm")
        quantity_to_add = quantity # Sử dụng số lượng truyền vào

        try:
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

                # B2: Thêm/cộng dồn
                cursor.execute(
                    "SELECT CartItemID, Quantity FROM CartItems WHERE CartID = ? AND ProductID = ?",
                    (cart_id, product_id),
                )
                item_row = cursor.fetchone()
                if item_row:
                    # Cộng dồn số lượng MỚI
                    new_quantity = item_row.Quantity + quantity_to_add
                    cursor.execute(
                        "UPDATE CartItems SET Quantity = ? WHERE CartItemID = ?",
                        (new_quantity, item_row.CartItemID),
                    )
                else:
                    # Thêm với số lượng MỚI
                    cursor.execute(
                        "INSERT INTO CartItems (CartID, ProductID, Quantity) VALUES (?, ?, ?)",
                        (cart_id, product_id, quantity_to_add),
                    )

                conn.commit()
                yield rx.window_alert(f"Đã thêm {quantity_to_add} sản phẩm '{product_name}' vào giỏ hàng!")
                return

        except Exception as e:
            print(f"Lỗi khi thêm vào giỏ hàng: {e}")
            try:
                conn.rollback()
            except:
                pass
            yield rx.window_alert("Đã xảy ra lỗi khi thêm sản phẩm vào giỏ hàng.")

    # --- CÁC HÀM TẢI DỮ LIỆU GIỮ NGUYÊN ---
    def load_products(self):
        temp_products = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
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
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    formatted_price = f"{int(row.Price):,} đ".replace(",", ".")
                    temp_products.append(
                        {
                            "id": row.ID,
                            "name": row.Name,
                            "price": formatted_price,
                            "image_url": (
                                row.ImageURL if row.ImageURL else "/no-image.png"
                            ), 
                        }
                    )
            self.products = temp_products
        except Exception as e:
            print(f"Lỗi khi tải danh sách sản phẩm: {e}")

    def load_product_types(self):
        temp_list = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Code, Name FROM ProductTypes")
                product_types = cursor.fetchall()
                for pt in product_types:
                    image_query = "SELECT TOP 1 ImageURL FROM Images WHERE ImageURL LIKE ? ORDER BY STT"
                    search_pattern = f"%/loai_{pt.Code}%"
                    cursor.execute(image_query, search_pattern)
                    image_row = cursor.fetchone()
                    image_url = "/no-image.png" 
                    if image_row:
                        image_url = image_row.ImageURL
                    temp_list.append({"name": pt.Name, "image_url": image_url})
            self.product_types_with_images = temp_list
        except Exception as e:
            print(f"Lỗi khi tải loại sản phẩm: {e}")

    async def load_recently_purchased_products(self):
        user_id_obj = await self.get_state(self.LoginState)
        user_id = user_id_obj.current_user.get("id")

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
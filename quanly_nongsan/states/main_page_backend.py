import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from .login_backend import State as LoginState

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class MainPageState(rx.State):
    """State quản lý dữ liệu cho trang chính."""

    # Biến để lưu danh sách các loại sản phẩm cùng với ảnh
    # Cấu trúc: [{"name": "Tên Loại", "image_url": "/url/anh.jpg"}, ...]
    product_types_with_images: list[dict] = []

    # --- BẮT ĐẦU PHẦN MỚI ---
    # Biến state để lưu danh sách sản phẩm
    # Cấu trúc: [{"name": "Tên SP", "price": "Giá", "image_url": "/url/anh.jpg"}, ...]
    products: list[dict] = []
    LoginState = LoginState

    async def check_login_and_add_to_cart(self, product: dict):
        """
        Kiểm tra nếu người dùng đã đăng nhập trước khi thêm vào giỏ hàng.
        """

        login_state = await self.get_state(LoginState)

        # Nếu dict current_user rỗng -> chưa đăng nhập
        if "username" not in login_state.current_user:
            # Trả về 2 hành động: hiện thông báo VÀ chuyển trang

            return [
                rx.window_alert("Bạn phải đăng nhập để mua hàng!"),
                rx.redirect("/login_page"),
            ]

        # Nếu đã đăng nhập, xử lý logic thêm vào giỏ hàng ở đây
        # Ví dụ:
        print(
            f"Người dùng {self.LoginState.current_user['username']} đã thêm sản phẩm {product['name']} vào giỏ."
        )
        return rx.window_alert(f"Đã thêm '{product['name']}' vào giỏ hàng!")

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

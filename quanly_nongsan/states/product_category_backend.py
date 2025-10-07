import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
import datetime
import asyncio
from decimal import Decimal, InvalidOperation 

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class State(rx.State):
    products: list[dict] = []
    product_types_options: list[str] = []

    # --- Biến cho form "Thêm" ---
    selected_type_code: str = ""
    new_product_code: str = ""
    new_product_name: str = ""
    new_expiry_date: str = ""
    new_notes: str = ""
    new_image_url: str = ""
    uploaded_image_preview: str = ""
    new_price: Decimal = Decimal("0.0") 

    # --- Biến cho form "Sửa" ---
    selected_product: dict | None = None
    edited_code: str = ""
    edited_name: str = ""
    edited_type_code: str = ""
    edited_expiry_date: str = ""
    edited_notes: str = ""
    edited_image_url: str = ""
    edited_price: Decimal = Decimal("0.0")

    search_query: str = ""

    # Biến này sẽ chứa danh sách tất cả các ảnh để đưa vào dropdown
    all_images_options: list[str] = []
    edited_primary_image_url: str = ""

    # Biến cho dialog xác nhận xóa
    show_delete_confirm_dialog: bool = False

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Xử lý việc tải file lên.

        Args:
            files: Danh sách các file được tải lên.
        """
        if not files:
            return

        # Chỉ xử lý file đầu tiên được chọn
        file = files[0]
        upload_data = await file.read()
        outfile = f".web/public/{file.filename}"

        # Lưu file vào thư mục public của web
        with open(outfile, "wb") as file_object:
            file_object.write(upload_data)

        # Cập nhật state với đường dẫn của file và ảnh preview
        self.new_image_url = f"/{file.filename}"
        self.uploaded_image_preview = self.new_image_url
        yield

    def on_page_load(self):
        self.load_products()
        self.load_product_types_code()
        self.load_all_images()

    def load_products(self):
        self.products = []
        sql = """
            SELECT p.ID, p.ProductCode, p.Name, p.ProductType, p.ExpiryDate, p.Notes,
                   p.PrimaryImageID, p.Price, i.ImageURL AS PrimaryImageURL
            FROM Products AS p
            LEFT JOIN Images AS i ON p.PrimaryImageID = i.STT
            ORDER BY p.ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    expiry_date_str = (
                        row.ExpiryDate.strftime("%Y-%m-%d")
                        if isinstance(row.ExpiryDate, datetime.date)
                        else ""
                    )
                    self.products.append(
                        {
                            "id": row.ID,
                            "code": row.ProductCode or "",
                            "name": row.Name or "",
                            "producttype": row.ProductType or "",
                            "expirydate": expiry_date_str,
                            "primary_image_url": row.PrimaryImageURL or "",
                            "primary_image_id": row.PrimaryImageID,
                            "notes": row.Notes or "",
                            "price": row.Price or ""
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải sản phẩm {e}")

    def load_product_types_code(self):
        self.product_types_options = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Code FROM ProductTypes ORDER BY Code")
                rows = cursor.fetchall()
                for row in rows:
                    self.product_types_options.append(row.Code)
        except Exception as e:
            print(f"Lỗi khi tải mã loại hàng {e}")

    def load_all_images(self):
        self.all_images_options = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ImageURL FROM Images ORDER BY STT DESC")
                rows = cursor.fetchall()
                for row in rows:
                    self.all_images_options.append(row.ImageURL)
        except Exception as e:
            print(f"Lỗi khi tải danh sách ảnh: {e}")

    def handle_selection(self, checked: bool, product: dict):
        if checked:
            self.selected_product = product
            self.edited_code = product.get("code", "")
            self.edited_name = product.get("name", "")
            self.edited_type_code = product.get("producttype", "")
            self.edited_expiry_date = product.get("expirydate", "")
            self.edited_notes = product.get("notes", "")
            self.edited_primary_image_url = product.get("primary_image_url")
            self.edited_price = product.get("price", "")            
        else:
            # Nếu bỏ check, và sản phẩm đang được bỏ check chính là sản phẩm đang được chọn
            if self.selected_product and self.selected_product["id"] == product["id"]:
                self.unselect_product()

    def unselect_product(self):
        self.selected_product = None
        # Reset các trường của form sửa khi bỏ chọn
        self.edited_code = ""
        self.edited_name = ""
        self.edited_type_code = ""
        self.edited_expiry_date = ""
        self.edited_notes = ""
        self.edited_primary_image_url = ""
        self.edited_price = ""

    def change_delete_dialog_state(self, show: bool):
        self.show_delete_confirm_dialog = show

    def delete_product(self):
        if self.selected_product is not None:
            try:
                with pyodbc.connect(CONNECTION_STRING) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM Products WHERE ID = ?",
                        (self.selected_product["id"],),
                    )
                    conn.commit()
                self.unselect_product() # Sử dụng hàm đã có để reset
                self.load_products()
            except Exception as e:
                print(f"Lỗi khi xóa: {e}")

    def search_products(self):
        query = f"%{self.search_query.strip()}%"
        self.products = []
        sql = """
            SELECT p.ID, p.ProductCode, p.Name, p.ProductType, p.ExpiryDate, p.Notes,
                   p.PrimaryImageID, p.Price, i.ImageURL AS PrimaryImageURL
            FROM Products AS p
            LEFT JOIN Images AS i ON p.PrimaryImageID = i.STT
            WHERE p.ProductCode LIKE ? OR p.Name LIKE ?
            ORDER BY p.ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query, query))
                rows = cursor.fetchall()
                for row in rows:
                    expiry_date_str = (
                        row.ExpiryDate.strftime("%Y-%m-%d")
                        if isinstance(row.ExpiryDate, datetime.date)
                        else ""
                    )
                    self.products.append(
                        {
                            "id": row.ID,
                            "code": row.ProductCode or "",
                            "name": row.Name or "",
                            "producttype": row.ProductType or "",
                            "expirydate": expiry_date_str,
                            "primary_image_url": row.PrimaryImageURL or "",
                            "primary_image_id": row.PrimaryImageID,
                            "notes": row.Notes or "",
                            "price": row.Price or ""
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tìm kiếm {e}")

    def update_product(self):
        if self.selected_product is None:
            return
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                image_stt = None
                if self.edited_primary_image_url:
                    cursor.execute(
                        "SELECT STT FROM Images WHERE ImageURL = ?",
                        self.edited_primary_image_url,
                    )
                    image_row = cursor.fetchone()
                    if image_row:
                        image_stt = image_row.STT

                cursor.execute(
                    """UPDATE Products SET Name = ?, ProductCode = ?, ProductType = ?, Notes = ?, ExpiryDate = ?, PrimaryImageID = ?
                    WHERE ID = ?""",
                    (
                        self.edited_name,
                        self.edited_code,
                        self.edited_type_code,
                        self.edited_notes,
                        self.edited_expiry_date or None,
                        image_stt,
                        self.selected_product["id"],
                    ),
                )
                conn.commit()
            self.unselect_product() # Sử dụng hàm đã có để reset
            self.load_products()
        except Exception as e:
            print(f"Lỗi khi cập nhật: {e}")

    def add_products(self):
        if not self.new_product_name.strip() or not self.selected_type_code:
            return rx.window_alert("Vui lòng chọn loại hàng và nhập tên hàng hóa.")

        product_type_id = None
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                new_image_id = None
                if self.new_image_url:
                    cursor.execute(
                        "INSERT INTO Images (ImageURL) OUTPUT INSERTED.STT VALUES (?)",
                        (self.new_image_url,),
                    )
                    new_image_id = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT ID FROM ProductTypes WHERE Code = ?",
                    self.selected_type_code,
                )
                row = cursor.fetchone()
                if not row:
                    return rx.window_alert("Loại hàng không hợp lệ")
                product_type_id = row.ID

                cursor.execute(
                    """
                INSERT INTO Products (ProductCode, Name, ProductType, ExpiryDate, Notes, ProductTypeID, PrimaryImageID, Price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    self.new_product_code.strip() or None,
                    self.new_product_name.strip(),
                    self.selected_type_code,
                    self.new_expiry_date or None,
                    self.new_notes.strip() or None,
                    product_type_id,
                    new_image_id,
                    self.new_price.strip() or None
                )
                conn.commit()

                # Reset form
                self.new_product_name = ""
                self.new_product_code = ""
                self.new_expiry_date = ""
                self.new_notes = ""
                self.new_image_url = ""
                self.selected_type_code = ""
                self.uploaded_image_preview = ""
                self.new_price = ""
                 # Thêm dòng này để xóa preview
                self.load_products()
                self.load_all_images()
                rx.window_alert("thêm thành công")
        except Exception as e:
            print(f"Lỗi khi thêm sản phẩm {e}")
            return rx.window_alert(f"Đã xảy ra lỗi: {e}")

    # --- Event Handlers for input changes ---
    def set_selected_type_code(self, code: str):
        self.selected_type_code = code

    def set_new_product_code(self, code: str):
        self.new_product_code = code

    def set_new_product_name(self, name: str):
        self.new_product_name = name

    def set_new_expiry_date(self, date: str):
        self.new_expiry_date = date

    def set_new_notes(self, notes: str):
        self.new_notes = notes

    def set_new_image_url(self, url: str):
        self.new_image_url = url

    def set_new_price(self, price: str):
        try:
            # Nếu value là chuỗi rỗng "" hoặc không hợp lệ, nó sẽ gây lỗi
            # và nhảy xuống khối except.
            self.new_price = Decimal(price)
        except (InvalidOperation, TypeError):
            # Xử lý trường hợp người dùng xóa hết số trong input
            self.new_price = Decimal("0.0")

    def set_edited_type_code(self, code: str):
        self.edited_type_code = code

    def set_edited_code(self, code: str):
        self.edited_code = code

    def set_edited_name(self, name: str):
        self.edited_name = name

    def set_edited_expiry_date(self, date: str):
        self.edited_expiry_date = date

    def set_edited_notes(self, notes: str):
        self.edited_notes = notes

    def set_edited_image_url(self, url: str):
        self.edited_image_url = url

    def set_search_query(self, query: str):
        self.search_query = query

    def set_edited_primary_image_url(self, url: str):
        self.edited_primary_image_url = url


    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.search_products()
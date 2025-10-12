# product_category_backend.py

import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
import datetime
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

    # --- BIẾN STATE CHO CHỌN NHIỀU MỤC (GIỐNG product_types) ---
    selected_product_ids: list[int] = []
    all_selected: bool = False
    search_query: str = ""
    
    # --- Biến cho form "Sửa" ---
    edited_code: str = ""
    edited_name: str = ""
    edited_type_code: str = ""
    edited_expiry_date: str = ""
    edited_notes: str = ""
    edited_primary_image_url: str = ""
    edited_price: Decimal = Decimal("0.0")

    all_images_options: list[str] = []

    # --- COMPUTED PROPERTIES (TÍNH TOÁN DỰA TRÊN STATE) ---
    @rx.var
    def is_only_one_selected(self) -> bool:
        """Kiểm tra xem chỉ có đúng một mục được chọn hay không."""
        return len(self.selected_product_ids) == 1

    @rx.var
    def product_to_edit(self) -> dict | None:
        """Lấy sản phẩm duy nhất được chọn để hiển thị trong khung chỉnh sửa."""
        if self.is_only_one_selected:
            product_id = self.selected_product_ids[0]
            for product in self.products:
                if product["id"] == product_id:
                    return product
        return None
    
    @rx.var
    def get_new_price_str(self) -> str:
        return "" if self.new_price == Decimal("0.0") else str(self.new_price) 
    
    @rx.var
    def get_edited_price_str(self) -> str:
        if self.product_to_edit:
            # Lấy giá trị từ state edited_price, không phải từ product_to_edit
            return "" if self.edited_price == Decimal("0.0") else str(self.edited_price)
        return ""


    # --- KHỞI TẠO VÀ TẢI DỮ LIỆU ---
    def on_page_load(self):
        self.load_products()
        self.load_product_types_code()
        self.load_all_images()

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        file = files[0]
        upload_data = await file.read()
        outfile = f".web/public/{file.filename}"
        with open(outfile, "wb") as file_object:
            file_object.write(upload_data)
        self.new_image_url = f"/{file.filename}"
        self.uploaded_image_preview = self.new_image_url
        yield

    def load_products(self):
        self.selected_product_ids = []
        self.all_selected = False
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
                        row.ExpiryDate.strftime("%Y-%m-%d") if isinstance(row.ExpiryDate, datetime.date) else ""
                    )
                    price_value = Decimal(str(row.Price)) if row.Price is not None else Decimal("0.0")
                    self.products.append({
                        "id": row.ID, "code": row.ProductCode or "", "name": row.Name or "",
                        "producttype": row.ProductType or "", "expirydate": expiry_date_str,
                        "primary_image_url": row.PrimaryImageURL or "", "primary_image_id": row.PrimaryImageID,
                        "notes": row.Notes or "", "price": price_value
                    })
        except Exception as e:
            print(f"Lỗi khi tải sản phẩm {e}")

    def load_product_types_code(self):
        self.product_types_options = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Code FROM ProductTypes ORDER BY Code")
                self.product_types_options = [row.Code for row in cursor.fetchall()]
        except Exception as e:
            print(f"Lỗi khi tải mã loại hàng {e}")

    def load_all_images(self):
        self.all_images_options = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ImageURL FROM Images ORDER BY STT DESC")
                self.all_images_options = [row.ImageURL for row in cursor.fetchall()]
        except Exception as e:
            print(f"Lỗi khi tải danh sách ảnh: {e}")

    # --- HÀM XỬ LÝ CHỌN (CHECKBOX) ---
    def select_product(self, item: dict, checked: bool):
        item_id = item["id"]
        if checked:
            if item_id not in self.selected_product_ids:
                self.selected_product_ids.append(item_id)
        else:
            if item_id in self.selected_product_ids:
                self.selected_product_ids.remove(item_id)
        
        self.all_selected = (len(self.products) > 0 and len(self.selected_product_ids) == len(self.products))
        self._update_edit_fields()

    def select_all_products(self, checked: bool):
        self.all_selected = checked
        if checked:
            self.selected_product_ids = [p['id'] for p in self.products]
        else:
            self.selected_product_ids = []
        self._update_edit_fields()

    def select_single_product_for_edit(self, item: dict):
        """Chọn một mục duy nhất từ nút Sửa icon."""
        self.selected_product_ids = [item["id"]]
        self.all_selected = False
        self._update_edit_fields()

    def _update_edit_fields(self):
        """Hàm nội bộ để cập nhật các trường chỉnh sửa dựa trên lựa chọn."""
        if self.is_only_one_selected:
            product = self.product_to_edit
            self.edited_code = product.get("code", "")
            self.edited_name = product.get("name", "")
            self.edited_type_code = product.get("producttype", "")
            self.edited_expiry_date = product.get("expirydate", "")
            self.edited_notes = product.get("notes", "")
            self.edited_primary_image_url = product.get("primary_image_url", "")
            self.edited_price = product.get("price", Decimal("0.0"))
        else:
            self.edited_code = ""
            self.edited_name = ""
            self.edited_type_code = ""
            self.edited_expiry_date = ""
            self.edited_notes = ""
            self.edited_primary_image_url = ""
            self.edited_price = Decimal("0.0")

    # --- HÀM THÊM / SỬA / XÓA ---
    def update_product(self):
        if not self.is_only_one_selected:
            return
        
        product_id = self.product_to_edit["id"]
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                image_stt = None
                if self.edited_primary_image_url:
                    cursor.execute("SELECT STT FROM Images WHERE ImageURL = ?", self.edited_primary_image_url)
                    image_row = cursor.fetchone()
                    if image_row: image_stt = image_row.STT

                product_type_id = None
                if self.edited_type_code:
                    cursor.execute("SELECT ID FROM ProductTypes WHERE Code = ?", self.edited_type_code)
                    row = cursor.fetchone()
                    if row: product_type_id = row.ID

                cursor.execute(
                    """UPDATE Products SET Name = ?, ProductCode = ?, ProductType = ?, ProductTypeID = ?, Notes = ?, ExpiryDate = ?, PrimaryImageID = ?, Price = ? WHERE ID = ?""",
                    (
                        self.edited_name, self.edited_code, self.edited_type_code, product_type_id, 
                        self.edited_notes, self.edited_expiry_date or None, image_stt,
                        self.edited_price, product_id
                    ),
                )
                conn.commit()
            
            self.selected_product_ids = [] # Xóa lựa chọn sau khi cập nhật
            self._update_edit_fields()
            self.load_products()
        except Exception as e:
            print(f"Lỗi khi cập nhật: {e}")

    def delete_selected_products(self):
        if not self.selected_product_ids:
            return
        
        id_list = tuple(self.selected_product_ids)
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(id_list))
                sql = f"DELETE FROM Products WHERE ID IN ({placeholders})"
                cursor.execute(sql, id_list)
                conn.commit()
            
            self.selected_product_ids = []
            self._update_edit_fields()
            self.load_products()
        except Exception as e:
            print(f"Lỗi khi xóa các mục đã chọn: {e}")

    def delete_product_by_id(self, item_id: int):
        """Xóa một mục từ nút Xóa icon."""
        self.selected_product_ids = [item_id]
        return self.delete_selected_products()
    
    def add_products(self):
        if not self.new_product_name.strip() or not self.selected_type_code:
            return rx.window_alert("Vui lòng chọn loại hàng và nhập tên hàng hóa.")
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                new_image_id = None
                if self.new_image_url:
                    cursor.execute("INSERT INTO Images (ImageURL) OUTPUT INSERTED.STT VALUES (?)", (self.new_image_url,))
                    new_image_id = cursor.fetchone()[0]

                cursor.execute("SELECT ID FROM ProductTypes WHERE Code = ?", self.selected_type_code)
                row = cursor.fetchone()
                if not row: return rx.window_alert("Loại hàng không hợp lệ")
                
                product_type_id = row.ID
                cursor.execute(
                    """INSERT INTO Products (ProductCode, Name, ProductType, ExpiryDate, Notes, ProductTypeID, PrimaryImageID, Price)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    self.new_product_code.strip() or None, self.new_product_name.strip(), self.selected_type_code,
                    self.new_expiry_date or None, self.new_notes.strip() or None, product_type_id,
                    new_image_id, self.new_price
                )
                conn.commit()
                # Reset form
                self.new_product_name = ""; self.new_product_code = ""; self.new_expiry_date = ""
                self.new_notes = ""; self.new_image_url = ""; self.selected_type_code = ""
                self.uploaded_image_preview = ""; self.new_price = Decimal("0.0")
                self.load_products()
                self.load_all_images()
                rx.window_alert("Thêm thành công")
        except Exception as e:
            print(f"Lỗi khi thêm sản phẩm {e}")
            return rx.window_alert(f"Đã xảy ra lỗi: {e}")

    # --- TÌM KIẾM ---
    def search_products(self):
        query = f"%{self.search_query.strip()}%"
        if not self.search_query.strip():
            self.load_products()
            return
        
        self.products = []
        sql = """
            SELECT p.ID, p.ProductCode, p.Name, p.ProductType, p.ExpiryDate, p.Notes,
                   p.PrimaryImageID, p.Price, i.ImageURL AS PrimaryImageURL
            FROM Products AS p LEFT JOIN Images AS i ON p.PrimaryImageID = i.STT
            WHERE p.ProductCode LIKE ? OR p.Name LIKE ? ORDER BY p.ID DESC
        """
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query, query))
                rows = cursor.fetchall()
                for row in rows:
                    expiry_date_str = (
                        row.ExpiryDate.strftime("%Y-%m-%d") if isinstance(row.ExpiryDate, datetime.date) else ""
                    )
                    price_value = Decimal(str(row.Price)) if row.Price is not None else Decimal("0.0")
                    self.products.append({
                        "id": row.ID, "code": row.ProductCode or "", "name": row.Name or "",
                        "producttype": row.ProductType or "", "expirydate": expiry_date_str,
                        "primary_image_url": row.PrimaryImageURL or "", "primary_image_id": row.PrimaryImageID,
                        "notes": row.Notes or "", "price": price_value 
                    })
            self.selected_product_ids = []
            self.all_selected = False
        except Exception as e:
            print(f"Lỗi khi tìm kiếm {e}")

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.search_products()

    # --- SETTERS (HÀM GÁN GIÁ TRỊ TỪ UI) ---
    def set_selected_type_code(self, code: str): self.selected_type_code = code
    def set_new_product_code(self, code: str): self.new_product_code = code
    def set_new_product_name(self, name: str): self.new_product_name = name
    def set_new_expiry_date(self, date: str): self.new_expiry_date = date
    def set_new_notes(self, notes: str): self.new_notes = notes
    def set_new_image_url(self, url: str): self.new_image_url = url
    def set_edited_type_code(self, code: str): self.edited_type_code = code
    def set_edited_code(self, code: str): self.edited_code = code
    def set_edited_name(self, name: str): self.edited_name = name
    def set_edited_expiry_date(self, date: str): self.edited_expiry_date = date
    def set_edited_notes(self, notes: str): self.edited_notes = notes
    def set_search_query(self, query: str): self.search_query = query
    def set_edited_primary_image_url(self, url: str): self.edited_primary_image_url = url

    def set_new_price(self, price: str):
        try: self.new_price = Decimal(price)
        except (InvalidOperation, TypeError): self.new_price = Decimal("0.0")
    
    def set_edited_price(self, price: str):
        try: self.edited_price = Decimal(price)
        except (InvalidOperation, TypeError): self.edited_price = Decimal("0.0")
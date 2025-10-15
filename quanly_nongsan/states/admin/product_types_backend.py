import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")

class State(rx.State):
    """The app state."""
    products: list[dict] = []
    new_product_type_name: str = ""
    new_product_type_code: str = ""

    # Dùng list để hỗ trợ chọn đa
    selected_product_ids: list[int] = [] 
    edited_code: str = ""
    edited_name: str = ""

    # --- BIẾN STATE CHO TÌM KIẾM VÀ CHỌN TẤT CẢ ---
    search_query: str = ""
    all_selected: bool = False

    # --- COMPUTED PROPERTIES ---
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

    # --- HÀM THÊM / TẢI DỮ LIỆU ---
    def set_search_query(self, query: str):
        self.search_query = query

    def add_product(self):
        label = (self.new_product_type_name or "").strip()
        code = (self.new_product_type_code or "").strip()
        if not label or not code:
            return

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ProductTypes (Name, Code) VALUES (?, ?)", (label, code)
                )
                conn.commit()
            self.new_product_type_name = ""
            self.new_product_type_code = ""
            self.load_products_type()
        except Exception as e:
            print(f"Lỗi khi thêm loại hàng {e}")

    def set_product_type_name(self, v: str):
        self.new_product_type_name = v

    def set_product_type_code(self, v: str):
        self.new_product_type_code = v

    def load_products_type(self):
        self.selected_product_ids = []
        self.all_selected = False 
        self.products = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT ID, Code, Name, CreatedAt FROM ProductTypes ORDER BY ID DESC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    created_at_val = getattr(row, "CreatedAt", None)
                    formatted_date = (
                        created_at_val.strftime("%Y-%m-%d %H:%M:%S")
                        if created_at_val
                        else ""
                    )
                    self.products.append(
                        {
                            "id": row.ID, "code": row.Code, "name": row.Name,
                            "createdat": formatted_date,
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu {e}")

    # --- HÀM CHỌN (CHECKBOX) ---
    def select_product(self, item: dict, checked: bool):
        item_id = item["id"]
        
        if checked:
            if item_id not in self.selected_product_ids:
                self.selected_product_ids.append(item_id)
        else:
            if item_id in self.selected_product_ids:
                self.selected_product_ids.remove(item_id)
                self.all_selected = False

        # Cập nhật trạng thái all_selected
        self.all_selected = (len(self.products) > 0 and len(self.selected_product_ids) == len(self.products))
        
        # Cập nhật trường chỉnh sửa nếu chỉ có 1 mục được chọn
        if self.is_only_one_selected:
            self.edited_code = self.product_to_edit["code"]
            self.edited_name = self.product_to_edit["name"]
        else:
            self.edited_code = ""
            self.edited_name = ""

    # --- HÀM CHỌN MỘT MỤC DUY NHẤT (CHO NÚT SỬA ICON) ---
    def select_single_product_for_edit(self, item: dict):
        """Đặt chỉ một ID vào danh sách chọn và cập nhật trường chỉnh sửa."""
        
        # 1. Bỏ chọn tất cả các mục khác và chỉ chọn mục hiện tại
        self.selected_product_ids = [item["id"]]
        self.all_selected = False
        
        # 2. Cập nhật trường chỉnh sửa ngay lập tức
        self.edited_code = item["code"]
        self.edited_name = item["name"]
        # KHÔNG RETURN GÌ CẢ (FIX LỖI)
        # return self.edited_code
        # KHÔNG CẦN RETURN GÌ CẢ. Việc gán giá trị đã tự động cập nhật UI.
        

    # --- HÀM CHỌN TẤT CẢ ---
    def select_all_products(self, checked: bool):
        self.all_selected = checked
        
        if checked:
            self.selected_product_ids = [p['id'] for p in self.products]
            # Nếu chỉ có 1 mục, cập nhật trường chỉnh sửa
            if self.is_only_one_selected:
                 self.edited_code = self.product_to_edit["code"]
                 self.edited_name = self.product_to_edit["name"]
            else:
                 self.edited_code = ""
                 self.edited_name = ""
        else:
            self.selected_product_ids = []
            self.edited_code = ""
            self.edited_name = ""


    def set_edited_code(self, code: str):
        self.edited_code = code

    def set_edited_name(self, name: str):
        self.edited_name = name

    # --- HÀM CẬP NHẬT ---
    def update_product(self):
        if not self.is_only_one_selected:
            return

        product_id = self.product_to_edit["id"]
        updated_code = self.edited_code
        updated_name = self.edited_name

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE ProductTypes SET Code = ?, Name = ? WHERE ID = ?",
                    (updated_code, updated_name, product_id),
                )
                conn.commit()

            # Cập nhật danh sách products trong state để UI tự cập nhật
            for i, prod in enumerate(self.products):
                if prod["id"] == product_id:
                    self.products[i]["code"] = updated_code
                    self.products[i]["name"] = updated_name
                    break

            # Sau khi cập nhật, xóa lựa chọn
            self.selected_product_ids = []
            self.all_selected = False
            self.edited_code = ""
            self.edited_name = ""

        except Exception as e:
            print(f"Lỗi khi cập nhật: {e}")

    # --- HÀM XÓA NHIỀU MỤC ĐÃ CHỌN ---
    def delete_selected_products(self):
        if not self.selected_product_ids:
            return

        id_list = tuple(self.selected_product_ids)
        
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(id_list))
                sql = f"DELETE FROM ProductTypes WHERE ID IN ({placeholders})"
                
                cursor.execute(sql, id_list)
                conn.commit()
            
            self.selected_product_ids = []
            self.all_selected = False
            self.edited_code = ""
            self.edited_name = ""
            self.load_products_type()

        except Exception as e:
            print(f"Lỗi khi xóa các mục đã chọn: {e}")

    # --- HÀM XÓA MỘT MỤC BẰNG ID (Dùng cho nút Xóa Icon) ---
    def delete_product_by_id(self, item_id: int):
        """Đặt ID vào danh sách chọn và gọi hàm xóa nhiều mục."""
        self.selected_product_ids = [item_id]
        return self.delete_selected_products()

    # --- HÀM TÌM KIẾM ---
    def search_products_type(self):
        query = f"%{self.search_query.strip()}%"
        if not self.search_query.strip():
            self.load_products_type()
            return
            
        self.products = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                sql = "SELECT ID, Code, Name, CreatedAt FROM ProductTypes WHERE Code LIKE ? OR Name LIKE ? ORDER BY ID DESC"
                cursor.execute(sql, (query, query))
                rows = cursor.fetchall()
                for row in rows:
                    created_at_val = getattr(row, "CreatedAt", None)
                    formatted_date = (
                        created_at_val.strftime("%Y-%m-%d %H:%M:%S")
                        if created_at_val
                        else ""
                    )
                    self.products.append(
                        {
                            "id": row.ID, "code": row.Code, "name": row.Name,
                            "createdat": formatted_date,
                        }
                    )
            self.selected_product_ids = []
            self.all_selected = False

        except Exception as e:
            print(f"Lỗi khi tìm kiếm {e}")

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.search_products_type()
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

    selected_product: dict | None = None
    edited_code: str = ""
    edited_name: str = ""

    # --- BIẾN STATE MỚI CHO TÌM KIẾM ---
    search_query: str = ""

    # --- HÀM SETTER MỚI CHO TÌM KIẾM ---
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
        self.selected_product = None
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

    def select_product(self, item: dict, checked: bool):
        if checked:
            self.selected_product = item
            self.edited_code = item["code"]
            self.edited_name = item["name"]
        else:
            self.selected_product = None

    def set_edited_code(self, code: str):
        self.edited_code = code

    def set_edited_name(self, name: str):
        self.edited_name = name

    def update_product(self):
        if not self.selected_product:
            return

        product_id = self.selected_product["id"]
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

            for i, prod in enumerate(self.products):
                if prod["id"] == product_id:
                    self.products[i]["code"] = updated_code
                    self.products[i]["name"] = updated_name
                    break

            self.selected_product = None

        except Exception as e:
            print(f"Lỗi khi cập nhật: {e}")

    def delete_product(self):
        if self.selected_product:
            try:
                with pyodbc.connect(CONNECTION_STRING) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM ProductTypes WHERE ID = ?",
                        (self.selected_product["id"],),
                    )
                    conn.commit()
                self.selected_product = None
                self.load_products_type()
            except Exception as e:
                print(f"Lỗi khi xóa: {e}")

    # --- HÀM TÌM KIẾM ĐÃ SỬA ---
    def search_products_type(self):
        query = f"%{self.search_query.strip()}%"
        if not self.search_query.strip():
            self.load_products_type()
            return
            
        self.products = []
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Tìm kiếm trên cả Code và Name
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
        except Exception as e:
            print(f"Lỗi khi tìm kiếm {e}")

    def search_on_enter(self, key: str):
        if key == "Enter":
            return self.search_products_type()
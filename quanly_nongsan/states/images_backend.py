import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
import os.path

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")

class ImageState(rx.State):
    """
    State để quản lý các hoạt động liên quan đến hình ảnh.
    """
    images: list[dict] = []
    new_image_url: str = ""
    new_alt_text: str = ""
    uploaded_image_preview: str = ""
    new_image_filename: str = ""
    image_search_query: str = ""
    selected_image: dict | None = None

    # Biến state mới để lưu dữ liệu file tạm thời
    uploaded_file_data: bytes | None = None
    original_file_info: dict | None = None

    def load_images(self):
        self.images = []
        sql = "SELECT STT, ImageURL, AltText, CreatedAt FROM Images ORDER BY STT DESC"
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    self.images.append({
                        "stt": row.STT,
                        "image_url": row.ImageURL or "",
                        "alt_text": row.AltText or "",
                        "created_at": row.CreatedAt.strftime("%Y-%m-%d %H:%M:%S") if row.CreatedAt else ""
                    })
        except Exception as e:
            print(f"Lỗi khi tải danh sách ảnh: {e}")

    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        (ĐÃ SỬA) Chỉ đọc dữ liệu file vào state và hiển thị preview.
        Không lưu file vật lý ở bước này.
        """
        if not files:
            return

        file = files[0]
        
        self.uploaded_file_data = await file.read()
        self.original_file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
        }
        
        # Hiển thị ảnh preview ngay lập tức
        self.uploaded_image_preview = f"/{file.filename}"
        yield

    def add_image(self):
        """
        (ĐÃ SỬA) Xử lý toàn bộ logic: tạo tên file, lưu file và cập nhật CSDL.
        """
        if not self.uploaded_file_data or not self.original_file_info:
            return rx.window_alert("Vui lòng upload một hình ảnh trước.")

        try:
            original_filename = self.original_file_info["filename"]
            _, file_extension = os.path.splitext(original_filename)

            custom_name = self.new_image_filename.strip().replace(" ", "-")
            if custom_name:
                final_filename = f"{custom_name}{file_extension}"
            else:
                final_filename = original_filename

            outfile_path = f".web/public/{final_filename}"
            with open(outfile_path, "wb") as file_object:
                file_object.write(self.uploaded_file_data)
            
            final_image_url = f"/{final_filename}"
            
            sql = """
                INSERT INTO Images (ImageURL, AltText, CreatedAt) 
                VALUES (?, ?, ?)
            """
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    final_image_url,
                    self.new_alt_text.strip() or None,
                    datetime.now()
                ))
                conn.commit()

            self.uploaded_file_data = None
            self.original_file_info = None
            self.new_image_url = ""
            self.new_alt_text = ""
            self.uploaded_image_preview = ""
            self.new_image_filename = ""
            self.load_images()

            return rx.window_alert("Thêm ảnh thành công!")
        except Exception as e:
            print(f"Lỗi khi thêm ảnh: {e}")
            return rx.window_alert(f"Đã xảy ra lỗi: {e}")

    def handle_image_selection(self, checked: bool, image: dict):
        if checked:
            self.selected_image = image
        else:
            if self.selected_image and self.selected_image["stt"] == image["stt"]:
                self.selected_image = None

    def delete_image(self):
        if not self.selected_image:
            return rx.window_alert("Vui lòng chọn một ảnh để xóa.")

        try:
            url_to_delete = self.selected_image["image_url"]
            
            filename = url_to_delete.strip("/")
            filepath = f".web/public/{filename}"
            if os.path.exists(filepath):
                os.remove(filepath)

            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Images WHERE ImageURL = ?", (url_to_delete,))
                conn.commit()
            
            self.selected_image = None
            self.load_images()
            return rx.window_alert("Xóa ảnh thành công!")
        except Exception as e:
            print(f"Lỗi khi xóa ảnh: {e}")
            return rx.window_alert(f"Đã xảy ra lỗi: {e}")

    def search_images(self):
        query = f"%{self.image_search_query.strip()}%"
        if not self.image_search_query.strip():
            self.load_images()
            return

        self.images = []
        sql = "SELECT STT, ImageURL, AltText, CreatedAt FROM Images WHERE ImageURL LIKE ? ORDER BY STT DESC"
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query,))
                rows = cursor.fetchall()
                for row in rows:
                    self.images.append({
                        "stt": row.STT, "image_url": row.ImageURL or "", "alt_text": row.AltText or "",
                        "created_at": row.CreatedAt.strftime("%Y-%m-%d %H:%M:%S") if row.CreatedAt else ""
                    })
        except Exception as e:
            print(f"Lỗi khi tìm kiếm ảnh: {e}")
            
    def search_images_on_enter(self, key: str):
        if key == "Enter":
            return self.search_images()
        
    def set_image_search_query(self, query: str):
        self.image_search_query = query
        
    def set_new_image_filename(self, filename: str):
        self.new_image_filename = filename

    def set_new_alt_text(self, text: str):
        self.new_alt_text = text
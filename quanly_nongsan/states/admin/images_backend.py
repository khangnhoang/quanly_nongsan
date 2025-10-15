import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
import os.path
import base64

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
    
    # Biến state mới để lưu dữ liệu file tạm thời
    uploaded_file_data: bytes | None = None
    original_file_info: dict | None = None
    
    # --- BIẾN STATE MỚI CHO CHỌN NHIỀU VÀ CHỌN TẤT CẢ ---
    selected_image_stt_list: list[int] = [] # Thay thế selected_image bằng danh sách STT
    all_selected: bool = False
    # --- END BIẾN STATE MỚI ---

    def load_images(self):
        # Thiết lập lại trạng thái chọn khi tải lại
        self.selected_image_stt_list = []
        self.all_selected = False
        self.images = []
        
        sql = "SELECT STT, ImageURL, AltText, CreatedAt FROM Images ORDER BY STT DESC"
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    self.images.append(
                        {
                            "stt": row.STT,
                            "image_url": row.ImageURL or "",
                            "alt_text": row.AltText or "",
                            "created_at": (
                                row.CreatedAt.strftime("%Y-%m-%d %H:%M:%S")
                                if row.CreatedAt
                                else ""
                            ),
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải danh sách ảnh: {e}")

    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        Đọc dữ liệu file, tạo Data URL để preview ngay lập tức.
        """
        if not files:
            return

        file = files[0]

        # 1. Đọc dữ liệu file và lưu thông tin vào state
        self.uploaded_file_data = await file.read()
        self.original_file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
        }

        # 2. Tạo Data URL để preview
        base64_data = base64.b64encode(self.uploaded_file_data).decode("utf-8")
        content_type = self.original_file_info["content_type"]
        data_url = f"data:{content_type};base64,{base64_data}"

        # 3. Gán Data URL cho biến preview
        self.uploaded_image_preview = data_url
        yield

    def add_image(self):
        """
        Xử lý toàn bộ logic: tạo tên file, lưu file và cập nhật CSDL.
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
                cursor.execute(
                    sql,
                    (
                        final_image_url,
                        self.new_alt_text.strip() or None,
                        datetime.now(),
                    ),
                )
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

    # --- HÀM CHỌN (CHECKBOX) ---
    def handle_image_selection(self, checked: bool, image: dict):
        image_stt = image["stt"]
        
        if checked:
            if image_stt not in self.selected_image_stt_list:
                self.selected_image_stt_list.append(image_stt)
        else:
            if image_stt in self.selected_image_stt_list:
                self.selected_image_stt_list.remove(image_stt)
                self.all_selected = False # Bỏ chọn một mục thì bỏ chọn tất cả

        # Cập nhật trạng thái all_selected
        self.all_selected = (len(self.images) > 0 and len(self.selected_image_stt_list) == len(self.images))
        
    # --- HÀM CHỌN TẤT CẢ ---
    def select_all_images(self, checked: bool):
        self.all_selected = checked
        
        if checked:
            self.selected_image_stt_list = [img['stt'] for img in self.images]
        else:
            self.selected_image_stt_list = []

    # --- HÀM XÓA NHIỀU MỤC ĐÃ CHỌN ---
    def delete_selected_images(self):
        if not self.selected_image_stt_list:
            return rx.window_alert("Vui lòng chọn ít nhất một ảnh để xóa.")

        try:
            # 1. Lấy ImageURL của các ảnh đã chọn để xóa file
            stt_list = tuple(self.selected_image_stt_list)
            urls_to_delete = []
            
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                
                # Lấy URL
                placeholders = ','.join(['?'] * len(stt_list))
                sql_select = f"SELECT ImageURL FROM Images WHERE STT IN ({placeholders})"
                cursor.execute(sql_select, stt_list)
                urls_to_delete = [row.ImageURL for row in cursor.fetchall()]
                
                # Xóa trong CSDL
                sql_delete = f"DELETE FROM Images WHERE STT IN ({placeholders})"
                cursor.execute(sql_delete, stt_list)
                conn.commit()

            # 2. Xóa các file vật lý
            for url in urls_to_delete:
                if url:
                    filename = url.strip("/")
                    filepath = f".web/public/{filename}"
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            # 3. Reset state và tải lại danh sách
            self.selected_image_stt_list = []
            self.all_selected = False
            self.load_images()
            return rx.window_alert("Xóa ảnh thành công!")

        except Exception as e:
            print(f"Lỗi khi xóa ảnh: {e}")
            return rx.window_alert(f"Đã xảy ra lỗi: {e}")

    # --- HÀM XÓA MỘT MỤC BẰNG STT (Dùng cho nút Xóa Icon) ---
    def delete_single_image_by_stt(self, stt: int):
        """Đặt STT vào danh sách chọn và gọi hàm xóa nhiều mục."""
        self.selected_image_stt_list = [stt]
        return self.delete_selected_images()

    def search_images(self):
        query = f"%{self.image_search_query.strip()}%"
        if not self.image_search_query.strip():
            self.load_images()
            return

        # Reset selection state before search
        self.selected_image_stt_list = []
        self.all_selected = False
            
        self.images = []
        sql = "SELECT STT, ImageURL, AltText, CreatedAt FROM Images WHERE ImageURL LIKE ? OR AltText LIKE ? ORDER BY STT DESC"
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (query, query))
                rows = cursor.fetchall()
                for row in rows:
                    self.images.append(
                        {
                            "stt": row.STT,
                            "image_url": row.ImageURL or "",
                            "alt_text": row.AltText or "",
                            "created_at": (
                                row.CreatedAt.strftime("%Y-%m-%d %H:%M:%S")
                                if row.CreatedAt
                                else ""
                            ),
                        }
                    )
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

    # Xóa hàm cũ vì không còn dùng (thay bằng delete_selected_images)
    # def delete_image(self):
    #     if not self.selected_image:
    #         return rx.window_alert("Vui lòng chọn một ảnh để xóa.")
    #     ... (logic cũ)
    
    # Xóa biến state cũ
    # selected_image: dict | None = None
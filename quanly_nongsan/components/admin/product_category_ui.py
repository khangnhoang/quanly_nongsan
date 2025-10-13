# product_category_ui.py

import reflex as rx
from ...states.state import State
from .sidebar_ui import sidebar

# TẠO CÁC HÀM HELPER GIỐNG product_types_ui
def select_for_edit(item: dict):
    return State.productState2.select_single_product_for_edit(item)

def delete_single_product_by_id(item_id: int):
    return State.productState2.delete_product_by_id(item_id)

def main_content():
    # Lambda để kiểm tra một mục có được chọn hay không
    is_selected = lambda item: (
        State.productState2.selected_product_ids.contains(item["id"])
    )

    headers = [
        "ID", "Mã Hàng Hóa", "Tên Hàng Hóa", "Loại Hàng", 
        "URL Hình Ảnh", "Ngày Hết Hạn", "Ghi Chú", "Giá", "Hành động"
    ]
    
    edit_headers = [
        "ID", "Mã Hàng Hóa", "Tên Hàng Hóa", "Loại Hàng", 
        "Ảnh sản phẩm", "Ngày Hết Hạn", "Ghi Chú", "Giá"
    ]

    return rx.vstack(
        # --- THANH MENU ĐIỀU HƯỚNG ---
        rx.center(
            rx.hstack(
                rx.button("Phân loại hàng hóa", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/product_types")),
                rx.button("Danh mục hàng hóa", bg="red", color="white", padding="12px", cursor="pointer", on_click=rx.redirect("/product_category")),
                rx.button("Danh sách khách hàng", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/customer")),
                rx.button("Quản lý hình ảnh", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/image_page")),
                spacing="0",
            ),
            width="100%", marginBottom="2%",
        ),
        
        # --- FORM THÊM HÀNG HÓA ---
        rx.heading("Thêm hàng hóa", size="7"),
        rx.divider(border_color="red"),
        # ... (Toàn bộ form thêm sản phẩm giữ nguyên)
        rx.hstack(
            rx.vstack(
                rx.text("Chọn loại hàng (*)", size="1"),
                rx.select(
                    State.productState2.product_types_options, placeholder="-- Chọn loại hàng --", width="100%",
                    background_color="whitesmoke", color="black", value=State.productState2.selected_type_code,
                    on_change=State.productState2.set_selected_type_code,
                ),
            ),
            rx.vstack(
                rx.text("Mã hàng hóa", size="1"),
                rx.input(bg="whitesmoke", color="black", value=State.productState2.new_product_code, on_change=State.productState2.set_new_product_code),
            ),
            rx.vstack(
                rx.text("Tên hàng hóa", size="1"),
                rx.input(bg="whitesmoke", color="black", width="100%", value=State.productState2.new_product_name, on_change=State.productState2.set_new_product_name),
                width="20%",
            ),
            rx.vstack(
                rx.text("Ngày hết hạn", size="1"),
                rx.input(type_="date", bg="whitesmoke", color="black", width="100%", value=State.productState2.new_expiry_date, on_change=State.productState2.set_new_expiry_date),
                width="20%",
            ),
            rx.vstack(
                rx.text("Ghi chú", size="1"),
                rx.input(bg="whitesmoke", color="black", width="100%", value=State.productState2.new_notes, on_change=State.productState2.set_new_notes),
                width="20%",
            ),
            rx.vstack(
                rx.text("Giá", size="1"),
                rx.input(type_="number", bg="whitesmoke", color="black", width="100%", value=State.productState2.get_new_price_str, on_change=State.productState2.set_new_price),
            ),
            width="100%", spacing="4"
        ),
        rx.vstack(
            rx.text("Ảnh sản phẩm", size="1"),
            rx.upload(
                rx.hstack(
                    rx.icon("upload", size=30),
                    rx.vstack(rx.text("Kéo và thả file vào đây"), rx.text("Chỉ nhận file . PNG, JPG, JPEG"), align="start"),
                    rx.button("Duyệt file", cursor="pointer"),
                    justify="between", align="center", width="100%",
                ),
                id="product_image_upload", padding="12px", width="100%", border="1px solid #ddd", border_radius="12px",
                on_drop=State.productState2.handle_upload(rx.upload_files(upload_id="product_image_upload")),
            ),
            rx.cond(
                State.productState2.uploaded_image_preview != "",
                rx.image(src=State.productState2.uploaded_image_preview, height="5em", margin_top="10px"),
            ),
            align_items="start", width="100%",
        ),
        rx.button("Thêm sản phẩm", bg="red", color="white", on_click=State.productState2.add_products, cursor="pointer", marginTop="10px"),

        # --- DANH SÁCH HÀNG HÓA ---
        rx.heading("Danh mục hàng hóa", size="7", marginTop="3%"),
        rx.divider(border_color="red"),

        rx.vstack(
            rx.text("Gõ tìm kiếm và nhấn Enter", size="2"),
            rx.input(
                width="100%", bg="#f1f4f9", color="black", placeholder="Tìm theo mã hoặc tên...",
                value=State.productState2.search_query,
                on_change=State.productState2.set_search_query,
                on_key_down=State.productState2.search_on_enter,
            ),
            width="100%",
        ),
        rx.heading("Kết quả tìm kiếm", size="3"),

        # --- NÚT XÓA NHIỀU MỤC ĐÃ CHỌN ---
        rx.hstack(
            rx.button(
                "Xóa các mục đã chọn", bg="red", color="white", 
                on_click=State.productState2.delete_selected_products, 
                cursor="pointer",
                is_disabled=State.productState2.selected_product_ids.length() == 0
            ),
            justify="start", width="100%", margin_bottom="10px",
        ),

        # --- BẢNG DỮ LIỆU ---
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.checkbox(
                            checked=State.productState2.all_selected,
                            on_change=State.productState2.select_all_products,
                        ),
                        color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7", width="5%"
                    ),
                    *[rx.table.column_header_cell(h, color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7") for h in headers]
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.productState2.products,
                    lambda product: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                checked=is_selected(product),
                                on_change=lambda checked: State.productState2.select_product(product, checked)
                            ),
                            border="0.5px solid #C1C1C1",
                            bg=rx.cond(is_selected(product), "#f0f8ff", "white")
                        ),
                        rx.table.cell(product["id"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(product["code"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(product["name"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(product["producttype"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(rx.image(src=product["primary_image_url"], height="3em", width="auto", fallback="/no-image.png"), border="0.5px solid #C1C1C1"),
                        rx.table.cell(product["expirydate"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(product["notes"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(product["price"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(
                            rx.hstack(
                                rx.button(rx.icon("pencil"), on_click=select_for_edit(product), size="1", color_scheme="blue"),
                                rx.button(rx.icon("trash-2"), on_click=delete_single_product_by_id(product["id"]), size="1", color_scheme="red"),
                                spacing="2", justify="center"
                            ),
                            border="0.5px solid #C1C1C1", text_align="center"
                        ),
                        key=product["id"],
                    ),
                )
            ),
            width="100%",
        ),

        # --- KHUNG DỮ LIỆU SỬA (CHỈ HIỂN THỊ KHI is_only_one_selected LÀ TRUE) ---
        rx.cond(
            State.productState2.is_only_one_selected,
            rx.vstack(
                rx.heading("Dữ liệu đã chọn", size="5", marginTop="20px"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(*[rx.table.column_header_cell(h, color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7") for h in edit_headers])
                    ),
                    rx.table.body(
                        rx.table.row(
                            rx.table.cell(State.productState2.product_to_edit.get("id", ""), border="0.5px solid #C1C1C1", color="black"),
                            rx.table.cell(rx.input(value=State.productState2.edited_code, on_change=State.productState2.set_edited_code, bg="white", color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.input(value=State.productState2.edited_name, on_change=State.productState2.set_edited_name, bg="white", color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.select(State.productState2.product_types_options, value=State.productState2.edited_type_code, on_change=State.productState2.set_edited_type_code, bg="whitesmoke", color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.select(State.productState2.all_images_options, placeholder="-- Chọn ảnh --", value=State.productState2.edited_primary_image_url, on_change=State.productState2.set_edited_primary_image_url, color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.input(type_="date", value=State.productState2.edited_expiry_date, on_change=State.productState2.set_edited_expiry_date, bg="white", color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.input(value=State.productState2.edited_notes, on_change=State.productState2.set_edited_notes, bg="white", color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.input(value=State.productState2.get_edited_price_str, on_change=State.productState2.set_edited_price, type="number", bg="white", color="black"), border="0.5px solid #C1C1C1"),
                        )
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.button("Cập nhật thông tin", on_click=State.productState2.update_product, cursor="pointer"),
                    spacing="4", marginTop="10px",
                ),
                width="100%", align="center", padding="15px", border="1px solid #ddd", border_radius="8px", marginTop="20px", bg="#fafafa",
            ),
        ),
        
        width="100%", height="100%", bg="white", color="black",
        padding="20px", overflow_y="auto",
    )

def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        gap="0", width="100%", height="100vh",
        on_mount=[State.LoginState.try_auto_login, State.productState2.on_page_load]
    )
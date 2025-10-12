import reflex as rx
from ..states.state import State
from .sidebar_ui import sidebar

# TẠO HÀM RIÊNG BIỆT ĐỂ XỬ LÝ VIỆC CHỌN VÀ CHỈNH SỬA TỪ NÚT SỬA ICON
def select_for_edit(item: dict):
    # GỌI HÀM MỚI: Chỉ chọn mục này, đảm bảo is_only_one_selected là True
    return State.productState.select_single_product_for_edit(item)

# TẠO HÀM RIÊNG BIỆT ĐỂ XỬ LÝ VIỆC XÓA TỪ NÚT XÓA ICON
def delete_single_product_by_id(item_id: int):
    # Gọi hàm backend để xóa mục
    return State.productState.delete_product_by_id(item_id)

def main_content():
    # Kiểm tra xem ID của item có trong danh sách ID đã chọn hay không.
    is_selected = lambda item: (
        State.productState.selected_product_ids.contains(item["id"])
    )
    
    return rx.vstack(
        rx.center(
            rx.hstack(
                rx.button("Phân loại hàng hóa", bg="red", color="white", padding="12px", cursor="pointer", on_click=rx.redirect("/product_types")),
                rx.button("Danh mục hàng hóa", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/product_category")),
                rx.button("Danh sách khách hàng", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/customer")),
                rx.button("Quản lý hình ảnh", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/image_page")),
                spacing="0",
            ),
            width="100%", marginBottom="2%",
        ),
        rx.heading("Thêm loại hàng", size="7"),
        rx.divider(border_color="red"),
        rx.hstack(
            rx.vstack(
                rx.text("Mã loại hàng", size="2"),
                rx.input(bg="#f1f4f9", color="black", value=State.productState.new_product_type_code, on_change=State.productState.set_product_type_code),
            ),
            rx.vstack(
                rx.text("Tên loại hàng", size="2"),
                rx.input(width="100%", bg="#f1f4f9", color="black", value=State.productState.new_product_type_name, on_change=State.productState.set_product_type_name),
                width="100%",
            ),
            width="100%",
        ),
        rx.button("Thêm loại hàng", bg="red", color="white", on_click=State.productState.add_product, cursor="pointer"),
        rx.heading("Danh sách loại hàng", size="7", marginTop="3%"),
        rx.divider(border_color="red"),
        
        rx.vstack(
            rx.text("Gõ tìm kiếm và nhấn Enter", size="2"),
            rx.input(
                width="100%", bg="#f1f4f9", color="black",
                placeholder="Tìm theo mã hoặc tên...",
                value=State.productState.search_query,
                on_change=State.productState.set_search_query,
                on_key_down=State.productState.search_on_enter,
            ),
            width="100%",
        ),
        rx.heading("Kết quả tìm kiếm", size="3"),
        
        # --- NÚT XÓA NHIỀU MỤC ĐÃ CHỌN ---
        rx.hstack(
            rx.button(
                "Xóa các mục đã chọn", 
                bg="red", 
                color="white", 
                on_click=State.productState.delete_selected_products, 
                cursor="pointer",
                is_disabled=State.productState.selected_product_ids.length == 0
            ),
            justify="start", 
            width="100%",
            margin_bottom="10px",
        ),
        # ------------------------------------
        
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell( 
                        rx.vstack(
                            rx.checkbox(
                                checked=State.productState.all_selected,
                                on_change=State.productState.select_all_products,
                            ),
                            spacing="1",
                        ),
                        color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"
                    ),
                    rx.table.column_header_cell("ID", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                    rx.table.column_header_cell("Mã loại hàng", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                    rx.table.column_header_cell("Tên loại hàng", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                    rx.table.column_header_cell("Thời gian tạo", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                    # --- CỘT HÀNH ĐỘNG MỚI ---
                    rx.table.column_header_cell("Hành động", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7", text_align="center"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.productState.products,
                    lambda item: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                # Checkbox này được chọn nếu ID của nó có trong danh sách ID đã chọn
                                checked=is_selected(item), 
                                on_change=lambda checked: State.productState.select_product(item, checked)
                            ), 
                            border="0.5px solid #C1C1C1", 
                            bg=rx.cond(
                                is_selected(item), 
                                "#f0f8ff", # Màu nền sáng khi được chọn
                                "white"
                            )
                        ),
                        rx.table.cell(item["id"], color="black", border="0.5px solid #C1C1C1"),
                        rx.table.cell(item["code"], color="black", border="0.5px solid #C1C1C1"),
                        rx.table.cell(item["name"], color="black", border="0.5px solid #C1C1C1"),
                        rx.table.cell(item["createdat"], color="black", border="0.5px solid #C1C1C1"),
                        # --- CỘT HÀNH ĐỘNG DATA ---
                        rx.table.cell(
                            rx.hstack(
                                rx.button(
                                    rx.icon("pencil"),
                                    on_click=select_for_edit(item), # GỌI HÀM CHỌN DUY NHẤT
                                    size="1",
                                    color_scheme="blue",
                                ),
                                rx.button(
                                    rx.icon("trash-2"),
                                    on_click=delete_single_product_by_id(item["id"]),
                                    size="1",
                                    color_scheme="red",
                                ),
                                spacing="2",
                                justify="center"
                            ),
                            border="0.5px solid #C1C1C1",
                            text_align="center"
                        ),
                        key=item["id"],
                    ),
                )
            ),
            width="100%",
        ),
        
        # KHUNG DỮ LIỆU ĐÃ CHỌN (CHỈ HIỂN THỊ KHI is_only_one_selected LÀ TRUE)
        rx.cond(
            State.productState.is_only_one_selected,
            rx.vstack(
                rx.heading("Dữ liệu đã chọn", size="5", marginTop="20px"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ID", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                            rx.table.column_header_cell("Mã loại hàng", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                            rx.table.column_header_cell("Tên loại hàng", color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"),
                        )
                    ),
                    rx.table.body(
                        rx.table.row(
                            # Sử dụng product_to_edit để lấy thông tin
                            rx.table.cell(State.productState.product_to_edit.get("id", ""), color="black", border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.input(value=State.productState.edited_code, on_change=State.productState.set_edited_code, bg="white", color="black"), border="0.5px solid #C1C1C1"),
                            rx.table.cell(rx.input(value=State.productState.edited_name, on_change=State.productState.set_edited_name, bg="white", color="black"), border="0.5px solid #C1C1C1"),
                        )
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.button("Cập nhật thông tin", on_click=State.productState.update_product, cursor="pointer"),
                    spacing="4", marginTop="10px",
                ),
                width="100%", align="center", padding="15px", border="1px solid #ddd", border_radius="8px", marginTop="20px", bg="#fafafa",
            ),
        ),
        width="100%",
        height="100%",
        bg="white",
        color="black",
        padding="20px",
        overflow_y="auto",
    )

def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        gap="0",
        width="100%",
        height="100vh",
        on_mount=[State.LoginState.try_auto_login, State.productState.load_products_type]
    )
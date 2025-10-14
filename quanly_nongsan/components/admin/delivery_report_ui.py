# delivery_report_ui.py

import reflex as rx
from ...states.state import State
from .sidebar_ui import sidebar
from ...states.admin.delivery_report_backend import DeliveryState 
# --- HÀM HELPER CHO CÁC NÚT HÀNH ĐỘNG ---
def select_for_edit(order: dict):
    # Sử dụng DeliveryState
    return DeliveryState.select_single_order_for_edit(order) 

def delete_single_order_by_id(order_id: int):
    # Sử dụng DeliveryState
    return DeliveryState.delete_order_by_id(order_id)


def main_content():
    # Lambda để kiểm tra một đơn hàng có được chọn hay không
    is_selected = lambda order: (
        DeliveryState.selected_order_ids.contains(order["id"])
    )

    # Thêm "Hành động" vào danh sách header
    HEADERS = [
        "Mã ĐH", "Tên Khách", "SĐT Người Nhận", "Địa Chỉ Giao Hàng", 
        "Ngày Đặt", "Ngày Giao", "Trạng Thái", "Ghi Chú", "Hành động"
    ]
    
    # Header cho form sửa (không cần cột hành động)
    EDIT_HEADERS = [
        "Mã ĐH", "Tên Khách", "SĐT Người Nhận", "Địa Chỉ Giao Hàng", 
        "Ngày Đặt", "Trạng Thái", "Ngày Giao", "Ghi Chú" # Thay đổi thứ tự để sửa
    ]

    # Các trạng thái mặc định cho Dropdown
    STATUS_OPTIONS = ["Đang xử lý", "Đã xác nhận", "Đang giao hàng", "Đã giao hàng", "Đã hủy"]

    return rx.vstack(
        # --- THANH MENU ĐIỀU HƯỚNG ---
        rx.center(
            rx.hstack(
                # Thêm nút Báo cáo giao hàng
                rx.button("Báo cáo giao hàng", bg="red", color="white", on_click=rx.redirect("/delivery_report")),
                spacing="0", padding="12px"
            ),
            width="100%", marginBottom="2%",
        ),
        
        # --- BÁO CÁO GIAO HÀNG ---
        rx.heading("Báo cáo giao hàng", size="7"),
        rx.divider(border_color="red"),

        # --- TÌM KIẾM ---
        rx.vstack(
            rx.text("Gõ tìm kiếm và nhấn Enter", size="2"),
            rx.input(
                # Sử dụng DeliveryState
                value=DeliveryState.search_query, on_change=DeliveryState.set_search_query,
                on_key_down=DeliveryState.search_on_enter, width="100%", bg="#f1f4f9", color="black",
                placeholder="Tìm theo Mã ĐH, Tên người nhận, SĐT, Địa chỉ, Trạng thái...",
            ),
            width="100%",
        ),
        rx.heading("Kết quả tìm kiếm", size="3"),

        # --- NÚT XÓA NHIỀU MỤC ĐÃ CHỌN ---
        rx.hstack(
            rx.button(
                "Xóa các mục đã chọn", bg="red", color="white",
                # Sử dụng DeliveryState
                on_click=DeliveryState.delete_selected_orders, cursor="pointer",
                is_disabled=DeliveryState.selected_order_ids.length() == 0
            ),
            justify="start", width="100%", margin_bottom="10px",
        ),
        
        # --- BẢNG DỮ LIỆU ---
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        # Sử dụng DeliveryState
                        rx.checkbox(checked=DeliveryState.all_selected, on_change=DeliveryState.select_all_orders),
                        color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7", width="5%"
                    ),
                    *[rx.table.column_header_cell(h, color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7") for h in HEADERS]
                )
            ),
            rx.table.body(
                # Sử dụng DeliveryState.orders
                rx.foreach(
                    DeliveryState.orders,
                    lambda order: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                checked=is_selected(order),
                                on_change=lambda checked: DeliveryState.select_order(order, checked)
                            ),
                            border="0.5px solid #C1C1C1", bg=rx.cond(is_selected(order), "#f0f8ff", "white")
                        ),
                        rx.table.cell(order["id"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(order["recipient_name"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(order["recipient_phone"], border="0.5px solid #C1C1C1", color="black"),
                        # Có thể hiển thị nhiều hơn: rx.table.cell(order["shipping_address"], ...)
                        rx.table.cell(order["shipping_address"], border="0.5px solid #C1C1C1", color="black", max_width="200px", overflow="hidden", text_overflow="ellipsis"),
                        rx.table.cell(order["order_date"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(order["delivery_date"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(order["status"], border="0.5px solid #C1C1C1", color="black"),
                        rx.table.cell(order["notes"], border="0.5px solid #C1C1C1", color="black", max_width="150px", overflow="hidden", text_overflow="ellipsis"),
                        rx.table.cell(
                            rx.hstack(
                                rx.button(rx.icon("trash-2"), on_click=delete_single_order_by_id(order["id"]), size="1", color_scheme="red"),
                                spacing="2", justify="center"
                            ),
                            border="0.5px solid #C1C1C1", text_align="center"
                        ),
                        key=order["id"],
                    ),
                )
            ),
            width="100%",
        ),

        # --- KHUNG DỮ LIỆU SỬA (CHỈ HIỂN THỊ KHI is_only_one_selected LÀ TRUE) ---
        rx.cond(
            DeliveryState.is_only_one_selected,
            rx.vstack(
                rx.heading("Dữ liệu đã chọn", size="5"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(*[rx.table.column_header_cell(h, color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7") for h in EDIT_HEADERS])
                    ),
                    rx.table.body(
                        rx.table.row(
                            # Các ô chỉ hiển thị (thông tin người nhận/đặt)
                            rx.table.cell(DeliveryState.order_to_edit.get("id", ""), border="0.5px solid #C1C1C1", color="black"),
                            rx.table.cell(DeliveryState.order_to_edit.get("recipient_name", ""), border="0.5px solid #C1C1C1", color="black"),
                            rx.table.cell(DeliveryState.order_to_edit.get("recipient_phone", ""), border="0.5px solid #C1C1C1", color="black"),
                            rx.table.cell(DeliveryState.order_to_edit.get("shipping_address", ""), border="0.5px solid #C1C1C1", color="black"),
                            rx.table.cell(DeliveryState.order_to_edit.get("order_date", ""), border="0.5px solid #C1C1C1", color="black"),
                            
                            # Ô chỉnh sửa Trạng thái (Dropdown)
                            rx.table.cell(
                                rx.select(
                                    STATUS_OPTIONS,
                                    value=DeliveryState.edited_status,
                                    on_change=DeliveryState.set_edited_status,
                                    placeholder="Chọn Trạng Thái",
                                ),
                                border="0.5px solid #C1C1C1"
                            ),
                            # Ô chỉnh sửa Ngày giao hàng (Input date)
                            rx.table.cell(
                                rx.input(
                                    value=DeliveryState.edited_delivery_date, 
                                    on_change=DeliveryState.set_edited_delivery_date, 
                                    bg="white", color="black", type="date"
                                ), 
                                border="0.5px solid #C1C1C1"
                            ),
                            # Ô chỉnh sửa Ghi chú
                            rx.table.cell(
                                rx.input(
                                    value=DeliveryState.edited_notes, 
                                    on_change=DeliveryState.set_edited_notes, 
                                    bg="white", color="black"
                                ), 
                                border="0.5px solid #C1C1C1"
                            ),
                        )
                    ),
                    width="100%",
                ),
                rx.hstack(
                    # Sử dụng DeliveryState
                    rx.button("Cập nhật thông tin", on_click=DeliveryState.update_order, cursor="pointer"),
                    spacing="4", marginTop="10px",
                ),
                width="100%", align="center", padding="15px", border="1px solid #ddd", border_radius="8px", marginTop="20px", bg="#fafafa",
            ),
        ),
        width="100%", height="100%", bg="white", color="black", padding="20px", overflow_y="auto", align_items="start",
    )


def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        # Tải danh sách đơn hàng khi mount
        on_mount=[State.LoginState.try_auto_login, DeliveryState.load_orders],
        gap="0", width="100%", height="100vh",
    )
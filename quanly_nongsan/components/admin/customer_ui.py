# customer_ui.py

import reflex as rx
from ...states.state import State
from .sidebar_ui import sidebar


# --- HÀM HELPER CHO CÁC NÚT HÀNH ĐỘNG ---
def select_for_edit(user: dict):
    return State.UserState.select_single_user_for_edit(user)


def delete_single_user_by_id(user_id: int):
    return State.UserState.delete_user_by_id(user_id)


def main_content():
    # Lambda để kiểm tra một khách hàng có được chọn hay không
    is_selected = lambda user: (State.UserState.selected_user_ids.contains(user["id"]))

    # Thêm "Hành động" vào danh sách header
    HEADERS = [
        "ID",
        "Username",
        "Tên khách hàng",
        "Vai trò",
        "Số điện thoại",
        "Địa chỉ",
        "Hành động",
    ]

    # Header cho form sửa (không cần cột hành động)
    EDIT_HEADERS = [
        "ID",
        "Username",
        "Tên khách hàng",
        "Vai trò",
        "Số điện thoại",
        "Địa chỉ",
    ]

    return rx.vstack(
        # --- THANH MENU ĐIỀU HƯỚNG ---
        rx.center(
            rx.hstack(
                rx.button(
                    "Phân loại hàng hóa",
                    bg="whitesmoke",
                    color="black",
                    on_click=rx.redirect("/product_types"),
                    cursor="pointer",
                ),
                rx.button(
                    "Danh mục hàng hóa",
                    bg="whitesmoke",
                    color="black",
                    on_click=rx.redirect("/product_category"),
                    cursor="pointer",
                ),
                rx.button(
                    "Danh sách khách hàng",
                    bg="red",
                    color="white",
                    on_click=rx.redirect("/customer"),
                    cursor="pointer",
                ),
                rx.button(
                    "Quản lý hình ảnh",
                    bg="whitesmoke",
                    color="black",
                    on_click=rx.redirect("/image_page"),
                    cursor="pointer",
                ),
                spacing="0",
                padding="12px",
            ),
            width="100%",
            marginBottom="2%",
        ),
        # --- FORM THÊM KHÁCH HÀNG ---
        rx.heading("Thêm khách hàng", size="7"),
        rx.divider(border_color="red"),
        rx.hstack(
            rx.vstack(
                rx.text("Tên khách hàng", size="1"),
                rx.input(
                    value=State.UserState.new_user_full_name,
                    on_change=State.UserState.set_new_user_full_name,
                    bg="whitesmoke",
                    color="black",
                ),
            ),
            rx.vstack(
                rx.text("Địa chỉ", size="1"),
                rx.input(
                    value=State.UserState.new_user_address,
                    on_change=State.UserState.set_new_user_address,
                    bg="whitesmoke",
                    color="black",
                    width="100%",
                ),
            ),
            rx.vstack(
                rx.text("SĐT", size="1"),
                rx.input(
                    value=State.UserState.new_user_phone_number,
                    on_change=State.UserState.set_new_user_phone_number,
                    bg="whitesmoke",
                    color="black",
                    width="100%",
                ),
            ),
            width="100%",
            spacing="4",
        ),
        rx.button(
            "Thêm khách hàng",
            bg="red",
            color="white",
            cursor="pointer",
            on_click=State.UserState.add_user,
            marginTop="10px",
        ),
        # --- DANH SÁCH KHÁCH HÀNG ---
        rx.heading("Danh sách khách hàng", size="7", marginTop="3%"),
        rx.divider(border_color="red"),
        rx.vstack(
            rx.text("Gõ tìm kiếm và nhấn Enter", size="2"),
            rx.input(
                value=State.UserState.search_query,
                on_change=State.UserState.set_search_query,
                on_key_down=State.UserState.search_on_enter,
                width="100%",
                bg="#f1f4f9",
                color="black",
                placeholder="Tìm theo tên, SĐT, username...",
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
                on_click=State.UserState.delete_selected_users,
                cursor="pointer",
                is_disabled=State.UserState.selected_user_ids.length() == 0,
            ),
            justify="start",
            width="100%",
            margin_bottom="10px",
        ),
        # --- BẢNG DỮ LIỆU ---
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.checkbox(
                            checked=State.UserState.all_selected,
                            on_change=State.UserState.select_all_users,
                        ),
                        color="black",
                        border="0.5px solid #C1C1C1",
                        bg="#E4E6E7",
                        width="5%",
                    ),
                    *[
                        rx.table.column_header_cell(
                            h, color="black", border="0.5px solid #C1C1C1", bg="#E4E6E7"
                        )
                        for h in HEADERS
                    ]
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.UserState.users,
                    lambda user: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                checked=is_selected(user),
                                on_change=lambda checked: State.UserState.select_user(
                                    user, checked
                                ),
                            ),
                            border="0.5px solid #C1C1C1",
                            bg=rx.cond(is_selected(user), "#f0f8ff", "white"),
                        ),
                        rx.table.cell(
                            user["id"], border="0.5px solid #C1C1C1", color="black"
                        ),
                        rx.table.cell(
                            user["username"],
                            border="0.5px solid #C1C1C1",
                            color="black",
                        ),
                        rx.table.cell(
                            user["full_name"],
                            border="0.5px solid #C1C1C1",
                            color="black",
                        ),
                        rx.table.cell(
                            user["role"], border="0.5px solid #C1C1C1", color="black"
                        ),
                        rx.table.cell(
                            user["phone_number"],
                            border="0.5px solid #C1C1C1",
                            color="black",
                        ),
                        rx.table.cell(
                            user["address"], border="0.5px solid #C1C1C1", color="black"
                        ),
                        rx.table.cell(
                            rx.hstack(
                                rx.button(
                                    rx.icon("pencil"),
                                    on_click=select_for_edit(user),
                                    size="1",
                                    color_scheme="blue",
                                ),
                                rx.button(
                                    rx.icon("trash-2"),
                                    on_click=delete_single_user_by_id(user["id"]),
                                    size="1",
                                    color_scheme="red",
                                ),
                                spacing="2",
                                justify="center",
                            ),
                            border="0.5px solid #C1C1C1",
                            text_align="center",
                        ),
                        key=user["id"],
                    ),
                )
            ),
            width="100%",
        ),
        # --- KHUNG DỮ LIỆU SỬA (CHỈ HIỂN THỊ KHI is_only_one_selected LÀ TRUE) ---
        rx.cond(
            State.UserState.is_only_one_selected,
            rx.vstack(
                rx.heading("Dữ liệu đã chọn", size="5"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            *[
                                rx.table.column_header_cell(
                                    h,
                                    color="black",
                                    border="0.5px solid #C1C1C1",
                                    bg="#E4E6E7",
                                )
                                for h in EDIT_HEADERS
                            ]
                        )
                    ),
                    rx.table.body(
                        rx.table.row(
                            rx.table.cell(
                                State.UserState.user_to_edit.get("id", ""),
                                border="0.5px solid #C1C1C1",
                                color="black",
                            ),
                            rx.table.cell(
                                State.UserState.user_to_edit.get("username", ""),
                                border="0.5px solid #C1C1C1",
                                color="black",
                            ),
                            rx.table.cell(
                                State.UserState.user_to_edit.get("full_name", ""),
                                border="0.5px solid #C1C1C1",
                                color="black",
                            ),
                            rx.table.cell(
                                State.UserState.user_to_edit.get("role", ""),
                                border="0.5px solid #C1C1C1",
                                color="black",
                            ),
                            rx.table.cell(
                                rx.input(
                                    value=State.UserState.edited_phone_number,
                                    on_change=State.UserState.set_edited_phone_number,
                                    bg="white",
                                    color="black",
                                ),
                                border="0.5px solid #C1C1C1",
                            ),
                            rx.table.cell(
                                rx.input(
                                    value=State.UserState.edited_address,
                                    on_change=State.UserState.set_edited_address,
                                    bg="white",
                                    color="black",
                                ),
                                border="0.5px solid #C1C1C1",
                            ),
                        )
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Cập nhật thông tin",
                        on_click=State.UserState.update_user,
                        cursor="pointer",
                    ),
                    spacing="4",
                    marginTop="10px",
                ),
                width="100%",
                align="center",
                padding="15px",
                border="1px solid #ddd",
                border_radius="8px",
                marginTop="20px",
                bg="#fafafa",
            ),
        ),
        width="100%",
        height="100%",
        bg="white",
        color="black",
        padding="20px",
        overflow_y="auto",
        align_items="start",
    )


def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        on_mount=[State.LoginState.try_auto_login, State.UserState.load_users],
        gap="0",
        width="100%",
        height="100vh",
    )

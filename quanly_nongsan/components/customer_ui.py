import reflex as rx
from ..states.state import State
from .sidebar_ui import sidebar

HEADERS = [
    "Chọn",
    "ID",
    "Username",
    "Tên khách hàng",
    "Vai trò",
    "Số điện thoại",
    "Địa chỉ",
]


def customers_rows():
    CELL_STYLE = {
        "border": "0.5px solid #C1C1C1",
        "color": "black",
        "padding": "8px",
        "vertical_align": "middle",
    }

    is_selected = lambda user: (
        State.UserState.selected_user.is_not_none()
        & (State.UserState.selected_user["id"] == user["id"])
    )

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                *[
                    rx.table.column_header_cell(h, style=CELL_STYLE, bg="#E4E6E7")
                    for h in HEADERS
                ],
            ),
        ),
        rx.table.body(
            rx.foreach(
                State.UserState.users,
                lambda user: rx.table.row(
                    rx.table.cell(
                        rx.checkbox(
                            checked=is_selected(user),
                            on_change=lambda checked: State.UserState.handle_user_selection(
                                checked, user
                            ),
                            cursor="pointer",
                        ),
                        style=CELL_STYLE,
                    ),
                    rx.table.cell(user["id"], style=CELL_STYLE),
                    rx.table.cell(user["username"], style=CELL_STYLE),
                    rx.table.cell(user["full_name"], style=CELL_STYLE),
                    rx.table.cell(user["role"], style=CELL_STYLE),
                    rx.table.cell(user["phone_number"], style=CELL_STYLE),
                    rx.table.cell(user["address"], style=CELL_STYLE),
                ),
            )
        ),
        width="100%",
    )


def edit_delete_form():
    """Form chỉnh sửa và xóa, chỉ hiện khi có khách hàng được chọn."""
    CELL_STYLE = {"border": "0.5px solid #C1C1C1", "color": "black"}
    HEADERS_FOR_DISPLAY = [
        "ID",
        "Username",
        "Tên khách hàng",
        "Vai trò",
        "Số điện thoại",
        "Địa chỉ",
    ]

    return rx.cond(
        State.UserState.selected_user,
        # --- SỬA: Thêm style cho vstack để giống các trang khác ---
        rx.vstack(
            rx.heading("Dữ liệu đã chọn", size="5"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        *[
                            rx.table.column_header_cell(
                                h, style=CELL_STYLE, bg="#E4E6E7"
                            )
                            for h in HEADERS_FOR_DISPLAY
                        ],
                    ),
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.cell(
                            State.UserState.selected_user.get("id", ""),
                            style=CELL_STYLE,
                        ),
                        rx.table.cell(
                            State.UserState.selected_user.get("username", ""),
                            style=CELL_STYLE,
                        ),
                        rx.table.cell(
                            State.UserState.selected_user.get("full_name", ""),
                            style=CELL_STYLE,
                        ),
                        rx.table.cell(
                            State.UserState.selected_user.get("role", ""),
                            style=CELL_STYLE,
                        ),
                        rx.table.cell(
                            rx.input(
                                value=State.UserState.edited_phone_number,
                                on_change=State.UserState.set_edited_phone_number,
                                bg="white",
                                color="black",
                                width="100%",
                            ),
                            style=CELL_STYLE,
                        ),
                        rx.table.cell(
                            rx.input(
                                value=State.UserState.edited_address,
                                on_change=State.UserState.set_edited_address,
                                bg="white",
                                color="black",
                                width="100%",
                            ),
                            style=CELL_STYLE,
                        ),
                    ),
                ),
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Cập nhật thông tin",
                    on_click=State.UserState.update_user,
                    cursor="pointer",
                ),
                rx.button(
                    "Xóa khách hàng",
                    on_click=State.UserState.delete_user,
                    color_scheme="red",
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
    )


def main_content():
    return rx.vstack(
        rx.center(
            rx.hstack(
                rx.button(
                    "Phân loại hàng hóa",
                    bg="whitesmoke",
                    color="black",
                    padding="12px",
                    cursor="pointer",
                    on_click=rx.redirect("/product_types"),
                ),
                rx.button(
                    "Danh mục hàng hóa",
                    bg="whitesmoke",
                    color="black",
                    padding="12px",
                    cursor="pointer",
                    on_click=rx.redirect("/product_category"),
                ),
                rx.button(
                    "Danh sách khách hàng",
                    bg="red",
                    color="white",
                    padding="12px",
                    cursor="pointer",
                    on_click=rx.redirect("/customer"),
                ),
                rx.button(
                    "Quản lý hình ảnh",
                    bg="whitesmoke",
                    color="black",
                    padding="12px",
                    cursor="pointer",
                    on_click=rx.redirect("/image_page"),
                ),
                spacing="0",
            ),
            width="100%",
            marginBottom="2%",
        ),
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
        ),
        rx.button(
            "Thêm khách hàng",
            bg="red",
            color="white",
            cursor="pointer",
            on_click=State.UserState.add_user,
        ),
        rx.heading("Danh sách khách hàng", size="7", marginTop="2%"),
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
                placeholder="Tìm theo tên, SĐT, địa chỉ...",
            ),
            width="100%",
        ),
        rx.heading("Kết quả tìm kiếm", size="3"),
        # --- SỬA: Tách biệt bảng và form để có cấu trúc rõ ràng ---
        customers_rows(),
        edit_delete_form(),
        # --- SỬA: Áp dụng layout full-page đúng cách ---
        width="100%",
        height="100%",  # Con dùng 100%
        bg="white",
        color="black",
        padding="20px",
        overflow_y="auto",  # Thêm thanh cuộn
        align_items="start",  # Căn chỉnh các item về đầu trọc
    )


def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        on_mount=[State.LoginState.try_auto_login, State.UserState.load_users],
        gap="0",
        width="100%",
        # --- SỬA: Cha dùng 100vh ---
        height="100vh",
    )

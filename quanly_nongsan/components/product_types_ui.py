import reflex as rx
from ..states.state import State
from .sidebar_ui import sidebar


def main_content():
    return rx.vstack(
        rx.vstack(
            rx.center(
                rx.hstack(
                    rx.button(
                        "Phân loại hàng hóa",
                        bg="red",
                        color="white",
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
                        bg="whitesmoke",
                        color="black",
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
            rx.heading("Thêm loại hàng", size="7"),
            rx.box(
                style={
                    "height": "2px",
                    "backgroundColor": "blue",
                    "width": "100%",
                    "marginTop": "3px",
                }
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Mã loại hàng", size="2"),
                    rx.input(
                        bg="#f1f4f9",
                        color="black",
                        value=State.productState.new_product_type_code,
                        on_change=State.productState.set_product_type_code,
                    ),
                ),
                rx.vstack(
                    rx.text("Tên loại hàng", size="2"),
                    rx.input(
                        width="100%",
                        bg="#f1f4f9",
                        color="black",
                        value=State.productState.new_product_type_name,
                        on_change=State.productState.set_product_type_name,
                    ),
                    width="100%",
                ),
                width="100%",
            ),
            rx.button(
                "Thêm loại hàng",
                bg="red",
                color="white",
                on_click=State.productState.add_product,
                cursor="pointer",
            ),
            rx.heading("Danh sách loại hàng", size="7", marginTop="3%"),
            rx.box(
                style={
                    "height": "2px",
                    "backgroundColor": "blue",
                    "width": "100%",
                    "marginTop": "3px",
                }
            ),
            rx.vstack(
                rx.text("Gõ tìm kiếm và nhấn Enter", size="2"),
                rx.input(
                    width="100%",
                    bg="#f1f4f9",
                    color="black",
                    value=State.productState.new_product_type_code,
                    on_change=State.productState.set_product_type_code,
                    on_key_down=State.productState.search_on_enter,
                ),
                width="100%",
            ),
            rx.heading("Kết quả tìm kiếm", size="3"),
            # Bảng danh sách sản phẩm
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(
                            "Select",
                            color="black",
                            border="0.5px solid #C1C1C1",
                            bg="#E4E6E7",
                        ),
                        rx.table.column_header_cell(
                            "ID",
                            color="black",
                            border="0.5px solid #C1C1C1",
                            bg="#E4E6E7",
                        ),
                        rx.table.column_header_cell(
                            "Mã loại hàng",
                            color="black",
                            border="0.5px solid #C1C1C1",
                            bg="#E4E6E7",
                        ),
                        rx.table.column_header_cell(
                            "Tên loại hàng",
                            color="black",
                            border="0.5px solid #C1C1C1",
                            bg="#E4E6E7",
                        ),
                        rx.table.column_header_cell(
                            "Thời gian tạo",
                            color="black",
                            border="0.5px solid #C1C1C1",
                            bg="#E4E6E7",
                        ),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        State.productState.products,
                        lambda item: rx.table.row(
                            rx.table.cell(
                                rx.checkbox(
                                    checked=rx.cond(
                                        State.productState.selected_product,
                                        State.productState.selected_product["id"]
                                        == item["id"],
                                        False,
                                    ),
                                    on_change=lambda checked: State.productState.select_product(
                                        item, checked
                                    ),
                                ),
                                border="0.5px solid #C1C1C1",
                            ),
                            rx.table.cell(
                                item["id"], color="black", border="0.5px solid #C1C1C1"
                            ),
                            rx.table.cell(
                                item["code"],
                                color="black",
                                border="0.5px solid #C1C1C1",
                            ),
                            rx.table.cell(
                                item["name"],
                                color="black",
                                border="0.5px solid #C1C1C1",
                            ),
                            rx.table.cell(
                                item["createdat"],
                                color="black",
                                border="0.5px solid #C1C1C1",
                            ),
                            key=item["id"],
                        ),
                    ),
                ),
                border="0.5px solid #C1C1C1",
                border_radius="4px",
                # Thêm thuộc tính này để viền đẹp hơn
                border_collapse="collapse",
                width="100%",
            ),
            # === KHU VỰC CHỈNH SỬA ĐÃ CẬP NHẬT GIAO DIỆN ===
            rx.cond(
                State.productState.selected_product,
                rx.vstack(
                    rx.heading("Dữ liệu đã chọn", size="5", marginTop="20px"),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    "ID",
                                    color="black",
                                    border="0.5px solid #C1C1C1",
                                    bg="#E4E6E7",
                                ),
                                rx.table.column_header_cell(
                                    "Mã loại hàng",
                                    color="black",
                                    border="0.5px solid #C1C1C1",
                                    bg="#E4E6E7",
                                ),
                                rx.table.column_header_cell(
                                    "Tên loại hàng",
                                    color="black",
                                    border="0.5px solid #C1C1C1",
                                    bg="#E4E6E7",
                                ),
                            )
                        ),
                        rx.table.body(
                            rx.table.row(
                                rx.table.cell(
                                    State.productState.selected_product["id"],
                                    color="black",
                                    border="0.5px solid #C1C1C1",
                                ),
                                rx.table.cell(
                                    rx.input(
                                        value=State.productState.edited_code,
                                        on_change=State.productState.set_edited_code,
                                        bg="#f1f4f9",
                                        color="black",
                                    ),
                                    border="0.5px solid #C1C1C1",
                                ),
                                rx.table.cell(
                                    rx.input(
                                        value=State.productState.edited_name,
                                        on_change=State.productState.set_edited_name,
                                        bg="#f1f4f9",
                                        color="black",
                                    ),
                                    border="0.5px solid #C1C1C1",
                                ),
                            )
                        ),
                        border="0.5px solid #C1C1C1",
                        border_collapse="collapse",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cập nhật thông tin",
                            on_click=State.productState.update_product,
                            cursor="pointer",
                        ),
                        rx.button(
                            "Xóa loại hàng",
                            on_click=State.productState.delete_product,
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
            ),
            width="100%",
            max_width="1400px",
        ),
        width="100%",
        height="100vh",
        bg="white",
        color="black",
        padding = "20px"
    )


def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        gap="0",
        width="100%",
        height="100vh",
        on_mount=[State.LoginState.try_auto_login, State.productState.load_products_type,]
    )

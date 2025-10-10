import reflex as rx
from ..states.state import State
from .sidebar_ui import sidebar

# --- Nội dung chính ---
def main_content() -> rx.Component:
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
                    bg="whitesmoke",
                    color="black",
                    padding="12px",
                    cursor="pointer",
                    on_click=rx.redirect("/customer"),
                ),
                rx.button(
                    "Quản lý hình ảnh",
                    bg="red",
                    color="white",
                    padding="12px",
                    cursor="pointer",
                    on_click=rx.redirect("/image_page"),
                ),
                spacing="0",
            ),
            width="100%",
            marginBottom="2%",
        ),
        # Tiêu đề trang và form thêm ảnh
        rx.heading("Thêm ảnh", size="7"),
        rx.divider(border_color="rainbow"),
        rx.vstack(
            rx.text("Ảnh sản phẩm", align_self="flex-start", margin_bottom="-10px"),
            rx.upload(
                rx.hstack(
                    rx.icon("cloud_upload"),
                    rx.vstack(
                        rx.text("Drag and drop file here"),
                        rx.text("Limit 200MB per file • PNG, JPG, JPEG", size="2"),
                        align="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.button("Browse files", cursor="pointer", bg="#FF0000"),
                    align="center",
                    width="100%",
                ),
                border="1px solid whitesmoke",
                bg="whitesmoke",
                border_radius="12px",
                padding="1.5em",
                width="100%",
                on_drop=State.ImageState.handle_upload(rx.upload_files()),
            ),
            rx.cond(
                State.ImageState.uploaded_image_preview != "",
                rx.image(
                    src=State.ImageState.uploaded_image_preview,
                    height="5em",
                    margin_top="10px",
                ),
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Đặt tên ảnh", align_self="flex-start", margin_bottom="-10px"),
            rx.input(
                placeholder="Nhập tên file bạn muốn đặt (ví dụ: hinh-san-pham-moi)",
                value=State.ImageState.new_image_filename,
                on_change=State.ImageState.set_new_image_filename,
                width="100%",
                bg="whitesmoke",
                border="1px solid whitesmoke",
                style={"input::placeholder": {"color": "#ccc"}},
                color="black"
            ),
            width="100%",
        ),
        rx.button(
            "Thêm ảnh",
            on_click=State.ImageState.add_image,
            width="150px",
            align_self="flex-end",
            margin_top="1em",
            bg="#FF0000",
            cursor="pointer",
        ),
        # Phần thư viện ảnh, tìm kiếm và xóa
        rx.heading("Thư viện ảnh", size="5", margin_top="2em"),
        rx.divider(border_color="rainbow"),
        rx.hstack(
            rx.input(
                placeholder="Tìm ảnh theo đường dẫn (URL) và nhấn Enter...",
                value=State.ImageState.image_search_query,
                on_change=State.ImageState.set_image_search_query,
                on_key_down=State.ImageState.search_images_on_enter,
                width="100%",
                bg="whitesmoke",
                style={"input::placeholder": {"color": "#ccc"}},
                color = "black"
            ),
            rx.cond(
                State.ImageState.selected_image,
                rx.button(
                    "Xóa ảnh đã chọn",
                    on_click=State.ImageState.delete_image,
                    color_scheme="red",
                ),
            ),
            spacing="4",
            width="100%",
            padding_y="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        "Chọn", color="black", border="1px solid #C1C1C1"
                    ),
                    rx.table.column_header_cell(
                        "STT", color="black", border="1px solid #C1C1C1"
                    ),
                    rx.table.column_header_cell(
                        "Ảnh", color="black", border="1px solid #C1C1C1"
                    ),
                    rx.table.column_header_cell(
                        "Đường dẫn", color="black", border="1px solid #C1C1C1"
                    ),
                    rx.table.column_header_cell(
                        "Mô tả (Alt Text)", color="black", border="1px solid #C1C1C1"
                    ),
                    rx.table.column_header_cell(
                        "Ngày tạo", color="black", border="1px solid #C1C1C1"
                    ),
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.ImageState.images,
                    lambda image: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                checked=(
                                    State.ImageState.selected_image.is_not_none()
                                    & (
                                        State.ImageState.selected_image["stt"]
                                        == image["stt"]
                                    )
                                ),
                                on_change=lambda checked: State.ImageState.handle_image_selection(
                                    checked, image
                                ),
                            ),
                            border="1px solid #C1C1C1",
                        ),
                        rx.table.cell(
                            image["stt"], color="black", border="1px solid #C1C1C1"
                        ),
                        rx.table.cell(
                            rx.image(src=image["image_url"], height="3em"),
                            border="1px solid #C1C1C1",
                        ),
                        rx.table.cell(
                            rx.code(image["image_url"], color="black"),
                            border="1px solid #C1C1C1",
                        ),
                        rx.table.cell(
                            image["alt_text"], color="black", border="1px solid #C1C1C1"
                        ),
                        rx.table.cell(
                            image["created_at"],
                            color="black",
                            border="1px solid #C1C1C1",
                        ),
                    ),
                )
            ),
            variant="surface",
            width="100%",
        ),
        # Style chung cho khu vực nội dung
        width="100%",
        height="100vh",
        bg="white",
        color="black",
        padding="20px",
        spacing="5",
        align="start",
        overflow_y="auto",
    )


# --- Trang Hoàn Chỉnh ---
def image_page() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        gap="0",
        width="100%",
        height="100vh",
        on_mount=[State.LoginState.try_auto_login, State.ImageState.load_images,]
    )

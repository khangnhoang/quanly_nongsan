import reflex as rx

# Import State của bạn
from .main_page_backend import MainPageState


def product_type_item(item: rx.Var[dict]) -> rx.Component:
    """
    Component để hiển thị một loại sản phẩm duy nhất.
    Nhận vào một item từ danh sách state.
    """
    return rx.link(
        rx.vstack(
            rx.image(
                src=item["image_url"],  # Lấy URL ảnh từ state
                width="70%",
                height="50%",
                max_height="152px",
                aspect_ratio="1 / 1",  # Giúp ảnh vuông vắn hơn
            ),
            rx.text(item["name"]),  # Lấy tên loại sản phẩm từ state
            align_items="center",
        ),
        width="30%",  # Giữ nguyên layout 3 cột của bạn
        href="#",  # Thêm đường dẫn sau này
    )


def header() -> rx.Component:
    """Component cho phần header đầu trang."""
    return rx.hstack(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/logonongsan.png", width="90px", height="90px"),
                    rx.center(
                        rx.text("MyWorldtoFarm.com"),
                    ),
                    align_items="center",
                ),
                width="30%",
                href="/",  # Link về trang chủ
            ),
            rx.hstack(
                rx.center(
                    rx.input(placeholder="Tìm kiếm", width="100%", height="40px"),
                    rx.button(rx.icon(tag="search"), height="40px"),
                    width="60%",
                    align_items="center",
                ),
                width="100%",
                align_items="center",
            ),
            rx.hstack(
                rx.link(
                    rx.vstack(
                        rx.icon(tag="shopping-bag"),
                        rx.text("Cart"),
                        width="100%",
                        color="white",
                    ),
                    href="/cart",  # Link tới giỏ hàng
                ),
                rx.link(
                    rx.vstack(
                        rx.icon(tag="user"),
                        rx.text("Login"),
                        width="100%",
                        color="white",
                    ),
                    href="/login_page",  # Link tới trang đăng nhập
                ),
            ),
            align_items = "center",
            width="100%",
        ),
        height="100px",
        width="100%",
        bg="#0069D1",
        padding_x="2%",  # Dùng padding_x cho gọn
        align_items="center",
        justify="between",
    )


def navigation() -> rx.Component:
    """Component cho thanh điều hướng."""
    return rx.hstack(
        rx.hstack(
            rx.hstack(
                rx.icon(tag="align-justify"),
                rx.text("DANH MỤC SẢN PHẨM", size="4", font_weight="bold"),
                padding="12px",
            ),
            rx.hstack(
                rx.text("RAU CỦ SẠCH", size="2"),
                rx.text("BÚN, MIẾN", size="2"),
                rx.text("GẠO CÁC LOẠI", size="2"),
                rx.text("THỰC PHẨM ĐÃ CHẾ BIẾN", size="2"),
                rx.text("NÔNG SẢN SẠCH", size="2"),
                rx.text("CÁC LOẠI ĐẶC SẢN ĐỒ KHÔ", size="2"),
                font_weight="bold",
                align_items="center",
                padding="12px",
            ),
            width="100%",
            align_items="center",
        ),
        align_items="center",
        height="45px",
        width="100%",
        bg="#0069D1",
        padding_x="2%",
    )


def index() -> rx.Component:
    """Hàm dựng giao diện chính của trang chủ."""
    return rx.vstack(
        header(),  # Gọi component header
        rx.box(border="0.5px solid whitesmoke", width="100%"),
        navigation(),
        rx.hstack(
            rx.foreach(MainPageState.product_types_with_images, product_type_item),
            margin_top="12px",
            width="100%",
            align_items="center",
            justify_content="center",
            flex_wrap="wrap",
            gap="20px",
            height="100%",
        ),
        gap="0",
        on_mount=MainPageState.load_product_types,
    )

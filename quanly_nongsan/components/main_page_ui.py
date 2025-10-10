import reflex as rx
from .main_page_and_cart_header import header

# Import State của bạn
from ..state import State


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


# --- PHẦN ĐƯỢC SỬA LẠI ---


def product_item(product: rx.Var[dict]) -> rx.Component:
    """Component để hiển thị một item sản phẩm duy nhất."""
    return rx.vstack(
        # Link bọc toàn bộ sản phẩm, khi click sẽ đi đến trang chi tiết
        rx.link(
            rx.image(
                src=product["image_url"],
                width="100%",
                aspect_ratio="1 / 1",
                object_fit="cover",
            ),
            rx.vstack(
                rx.text(product["name"], color="black", font_weight="bold", size="2"),
                rx.text(product["price"], color="red", size="3"),
                align_items="start",
                spacing="1",
                width="100%",
                padding="8px",
            ),
            href="#",  # Link chi tiết sản phẩm
        ),
        # Nút thêm vào giỏ hàng
        rx.button(
            "Thêm vào giỏ hàng",
            on_click=State.MainPageState.check_login_and_add_to_cart(product),
            width="100%",
            margin_top="auto",  # Đẩy nút xuống dưới cùng
            cursor="pointer",
        ),
        bg="#FFFFFF",
        border="1px solid #eee",
        border_radius="5px",
        overflow="hidden",
        _hover={"box_shadow": "0px 4px 10px rgba(0, 0, 0, 0.1)"},
        height="100%",  # Đảm bảo các card có chiều cao bằng nhau
    )


def product_buyed(product: rx.Var[dict]):
    """
    Component để hiển thị một sản phẩm đã từng mua.
    (Tăng kích thước ảnh để khớp với product_item)
    """
    return rx.vstack(
        # Link bọc toàn bộ sản phẩm
        rx.link(
            rx.image(
                src=product["image_url"],
                width="100%",
                # Sửa: Tăng chiều cao ảnh, đảm bảo tỷ lệ 1/1
                aspect_ratio="1 / 1",
                object_fit="cover",
            ),
            rx.vstack(
                # Sửa: Dùng size 2 và font_weight bold như product_item
                rx.text(product["name"], color="black", font_weight="bold", size="2"),
                # Sửa: Dùng size 3 như product_item
                rx.text(product["price"], color="red", size="3"),
                align_items="start",
                spacing="1",
                width="100%",
                padding="8px",  # Dùng padding 8px như product_item
            ),
            href="#",
        ),
        # Nút Mua lại (Thêm vào giỏ hàng) - ĐÃ CÓ CHỨC NĂNG
        rx.button(
            "Mua lại",
            on_click=State.MainPageState.check_login_and_add_to_cart(product),
            width="100%",
            margin_top="auto",
            cursor="pointer",
        ),
        bg="#FFFFFF",
        border="1px solid #eee",
        border_radius="5px",
        overflow="hidden",
        _hover={"box_shadow": "0px 4px 10px rgba(0, 0, 0, 0.1)"},
        height="100%",
    )

# File: main_page_ui.py

# ... (Các hàm khác giữ nguyên)

def purchased_slider():
    """
    Component hiển thị các sản phẩm đã từng mua dưới dạng lưới (grid) 6 cột,
    cuộn dọc (mặc định) và loại bỏ thanh cuộn ngang không cần thiết.
    """
    return rx.cond(
        State.MainPageState.recently_purchased_products.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.heading("Sản phẩm từng mua", size="5", color="#2287DF"),
                border="1px solid #eee",
                border_radius="4px",
                width="30%",
                height="35px",
                align_items="center",
                justify="center",
                bg="#FFFFFF",
                padding="4px",
            ),
            # SỬA ĐỔI LỚN: Thay thế rx.box cuộn ngang bằng rx.vstack
            rx.vstack( 
                rx.grid(
                    rx.foreach(
                        State.MainPageState.recently_purchased_products,
                        product_buyed,
                    ),
                    # Đặt cố định 6 cột, giúp sản phẩm không tràn ra ngoài
                    grid_template_columns="repeat(6, 1fr)",
                    # Xóa width tính toán (grid_width)
                    gap="16px",
                    padding="10px",
                    width="100%", # Đảm bảo grid chiếm hết chiều rộng
                    justify="start",
                ),
                # Xóa overflow_x="auto"
                width="100%",
            ),
            align_items="center",
            color="black",
            width="100%",
            bg="#519CE3",
            padding="40px",
            margin_bottom="4px",
        ),
    )

# ... (Phần còn lại của file giữ nguyên)

def content() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.hstack(
                rx.heading(
                    "CÁC LOẠI NÔNG SẢN SẠCH VÙNG MIỀN",
                    size="3",
                    font_weight="500",
                ),
                rx.link("Xem thêm >"),
                color="#0569D1",
                bg="#FFFFFF",
                justify="between",
                width="100%",
                padding="16px",
                align_items="center",
                border_bottom="3px solid #007CBA",
                border_radius="0",
            ),
            # Dùng rx.foreach để lặp qua danh sách sản phẩm từ state
            rx.grid(
                rx.foreach(State.MainPageState.products, product_item),
                grid_template_columns="repeat(6, 1fr)",
                gap="16px",
                width="100%",
                padding_top="16px",
            ),
        ),
        align_items="center",
        width="100%",
        padding_x="3%",
        margin_top = "8px",
    )


# --- KẾT THÚC PHẦN SỬA ---


def footer():
    # ... (Nội dung hàm footer giữ nguyên)
    return rx.vstack(
        rx.box(
            border="1px solid #eee",
            width="100%",
        ),
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Danh mục",
                    size="3",
                    color="#737675",
                    font_weight="bold",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.link(
                            rx.text("RAU CỦ SẠCH", size="2", color="#737675"),
                        ),
                        rx.link(
                            rx.text("BÚN, MIẾN", size="2", color="#737675"),
                        ),
                        width="100%",
                        spacing="0",
                        font_weight="bold",
                    ),
                    rx.vstack(
                        rx.link(
                            rx.text("CÁC LOẠI ĐẶC SẢN KHÔ", size="2", color="#737675"),
                        ),
                        rx.link(
                            rx.text("GẠO CÁC LOẠI", size="2", color="#737675"),
                        ),
                        width="100%",
                        spacing="0",
                        font_weight="bold",
                    ),
                    rx.vstack(
                        rx.link(
                            rx.text("NÔNG SẢN SẠCH", size="2", color="#737675"),
                        ),
                        rx.link(
                            rx.text("THỰC PHẨM ĐÃ CHẾ BIẾN", size="2", color="#737675"),
                        ),
                        width="100%",
                        spacing="0",
                        font_weight="bold",
                    ),
                    rx.vstack(
                        rx.link(
                            rx.text(
                                "ĐẶC SẢN TỔNG HỢP - NÔNG SẢN SẠCH",
                                size="2",
                                color="#737675",
                                font_weight="bold",
                            ),
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                width="70%",
            ),
            rx.vstack(
                rx.hstack(
                    rx.unordered_list(
                        rx.list_item("Quy chế hoạt động", font_size="14px"),
                        rx.list_item("Chính sách chung", font_size="14px"),
                        rx.list_item("Hỗ trợ khách hàng", font_size="14px"),
                        rx.list_item("Hợp tác- Liên kết", font_size="14px"),
                        rx.list_item("Phương thức thanh toán", font_size="14px"),
                        rx.list_item("Thông báo chung", font_size="14px"),
                        width="100%",
                    ),
                    rx.unordered_list(
                        rx.list_item("Các câu hỏi thường gặp", font_size="14px"),
                        rx.list_item(
                            "Chương trình tiếp thị liên kết", font_size="14px"
                        ),
                        rx.list_item("Liên hệ truyền thông", font_size="14px"),
                        rx.list_item("Hướng dẫn trả góp", font_size="14px"),
                        rx.list_item(rx.link("Thanh toán"), font_size="14px"),
                        rx.list_item("Đơn vị vận chuyển", font_size="14px"),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.heading(
                            "CÔNG TY THẾ GIỚI NÔNG SẢN 3 NHÂN TÀI",
                            size="3",
                            font_size="16px",
                        ),
                        rx.unordered_list(
                            rx.list_item(
                                "Trụ sở chính: TÒa ĐẠi xỨ QuÁN Mĩ", font_size="14px"
                            ),
                            rx.list_item(
                                "Cửa Hàng 1: Tổ 11 A - Phướng Sông Cầu - Thành Phố Bắc Kạn",
                                font_size="14px",
                            ),
                            rx.list_item(
                                "Cửa Hàng 2: VinHome Tây Mỗ - Hà Nội", font_size="14px"
                            ),
                            rx.list_item("Giấy ĐKKD số: 4700290799", font_size="14px"),
                            rx.list_item(
                                "Email CSKH: tgnsgroup.com@gmail.com", font_size="14px"
                            ),
                            rx.list_item(
                                "Hotline CSKH: 097.3636.888 (Miễn phí, 8-21h kể cả T7, CN)",
                                font_size="14px",
                            ),
                            rx.hstack(
                                rx.text(
                                    "Web đang chạy thử nghiệm các chức năng chưa đi vào hoạt động, chờ xin giấy phép của bộ công thương.",
                                    font_size="13px",
                                    font_weight="bold",
                                ),
                                rx.link(rx.icon(tag="facebook")),
                                rx.link(rx.icon(tag="instagram")),
                                rx.link(rx.icon(tag="youtube")),
                                width="100%",
                            ),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    width="100%",
                    color="black",
                ),
                width="100%",
            ),
        ),
        margin_top="64px",
        padding_x="3%",
        width="100%",
    )


def footer_end():
    # ... (Nội dung hàm footer_end giữ nguyên)
    return (
        rx.box(
            rx.text("Copyright 2025 © TheGioiNongSan.Com", font_size="14px"),
            as_="footer",
            text_align="center",
            padding="16px",
            background_color="#0069D1",
            color="white",
            width="100%",
        ),
    )


def index() -> rx.Component:
    """Hàm dựng giao diện chính của trang chủ."""
    return rx.vstack(
        header(),
        rx.box(border="0.5px solid whitesmoke", width="100%"),
        navigation(),
        rx.hstack(
            rx.foreach(
                State.MainPageState.product_types_with_images, product_type_item
            ),
            margin_top="12px",
            width="100%",
            align_items="center",
            justify_content="center",
            flex_wrap="wrap",
            gap="20px",
            height="100%",
        ),
        purchased_slider(),
        content(),
        footer(),
        footer_end(),
        bg="#F5F5F5",
        gap="0",
        # --- DÒNG SỬA ---
        on_mount=[
            State.LoginState.try_auto_login,
            State.MainPageState.load_product_types,
            State.MainPageState.load_products,
            State.MainPageState.load_recently_purchased_products
        ],
    )

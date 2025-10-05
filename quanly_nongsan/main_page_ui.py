import reflex as rx


def index() -> rx.Component:
    return rx.vstack(
        rx.hstack(
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
                ),
                rx.hstack(
                    rx.center(
                        rx.input(placeholder="Tìm kiếm", width="100%", height="40px"),
                        rx.button(rx.icon(tag="search"), height="40px"),
                        width="70%",
                    ),
                    width="60%",
                ),
                rx.hstack(
                    rx.hstack(
                        rx.link(
                            rx.vstack(
                                rx.icon(tag="shopping-bag"),
                                rx.text("Cart"),
                                width="100%",
                                color="white",
                            ),
                        ),
                        rx.link(
                            rx.vstack(
                                rx.icon(tag="user"),
                                rx.text("Login"),
                                width="100%",
                                color="white",
                            ),
                        ),
                    ),
                ),
                width="100%",
                align_items="center",
            ),
            height="100px",
            width="100%",
            bg="#0069D1",
            padding_left="2%",
            padding_right="2%",
        ),
        rx.box(border="0.5px solid whitesmoke", width="100%"),
        navigation(),
        product_type(),
        gap="0",
    )


def navigation() -> rx.Component:
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
        padding_left="2%",
        padding_right="2%",
    )


def product_type() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.link(
                rx.vstack(rx.image(src="/duachuot.jpg", width="80%", height="50%", max_height = "126px"), rx.text("Rau củ sạch"),align_items="center",),
                width = "30%"
            ),
            rx.link(
                rx.vstack(rx.image(src="/mien.jpg",width="80%", height="50%", max_height = "126px"), rx.text("Bún, Miến"),align_items="center",),
                width = "30%"
            ),
            rx.link(
                rx.vstack(rx.image(src="/Do-kho.jpg", width="80%", height="50%", max_height = "126px"), rx.text("Các Loại Đặc Sản Khô"),align_items="center",),
                width = "30%",
            ),
            margin_top = "12px",
            width = "100%",
            align_items="center",
        ),
        align_items="center",
        height="100%",
        width="100%",
    )

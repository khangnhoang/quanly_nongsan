import reflex as rx
from .main_page_and_cart_header import header


def order_history_no_items() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading(
                    "Đơn hàng từng mua",
                    size="3",
                    padding="4px",
                ),
                justify="center",
                border="1px solid #eee",
                width="100%",
                height="30px",
                border_radius="8px",
                bg="white",
            ),
            rx.vstack(
                rx.link(rx.icon(tag="circle-plus")),
                rx.text("Có vẻ như bạn chưa có đơn hàng nào"),
                justify="center",
                align_items="center",
                border="1px solid #eee",
                width="100%",
                border_radius="8px",
                bg="white",
                height="300px",
            ),
            align_items="center",
            color="black",
            width="50%",
            margin_top="2%",
            bg="#E9EDF0",
            padding="8px",
            border_radius="8px",
        ),
        width="100%",
        padding_x="3%",
    )


def order_history_have_items() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading(
                    "Đơn hàng từng mua",
                    size="3",
                    padding="4px",
                ),
                justify="center",
                border="1px solid #eee",
                width="100%",
                height="30px",
                border_radius="8px",
                bg="white",
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("Đơn hàng #03CD2510755096C9C44", font_weight="bold"),
                        rx.link(
                            "Xem chi tiết >",
                            href="#",
                            color="black",
                            font_weight="medium",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        color="black",
                    ),
                    rx.hstack(
                        rx.text("Giao thành công", color="green"),
                        justify="end",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.image(src="/duachuot.jpg", width="96px", height="96px"),
                        rx.image(src="/duachuot.jpg", width="96px", height="96px"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Tổng đơn hàng: 100.000đ"),
                        justify="end",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.spacer(),
                rx.button(
                    "Mua lại",
                    color="green",
                    width="100%",
                    bg="white",
                    border="1px solid #eee",
                ),
                border="1px solid #eee",
                width="100%",
                border_radius="8px",
                bg="white",
                height="300px",
                padding="8px",
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("Đơn hàng #03CD2510755096C9C44", font_weight="bold"),
                        rx.link(
                            "Xem chi tiết >",
                            href="#",
                            color="black",
                            font_weight="medium",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        color="black",
                    ),
                    rx.hstack(
                        rx.text("Giao thành công", color="green"),
                        justify="end",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.image(src="/duachuot.jpg", width="96px", height="96px"),
                        rx.image(src="/duachuot.jpg", width="96px", height="96px"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Tổng đơn hàng: 100.000đ"),
                        justify="end",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.spacer(),
                rx.button(
                    "Mua lại",
                    color="green",
                    width="100%",
                    bg="white",
                    border="1px solid #eee",
                ),
                border="1px solid #eee",
                width="100%",
                border_radius="8px",
                bg="white",
                height="300px",
                padding="8px",
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("Đơn hàng #03CD2510755096C9C44", font_weight="bold"),
                        rx.link(
                            "Xem chi tiết >",
                            href="#",
                            color="black",
                            font_weight="medium",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        color="black",
                    ),
                    rx.hstack(
                        rx.text("Giao thành công", color="green"),
                        justify="end",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.image(src="/duachuot.jpg", width="96px", height="96px"),
                        rx.image(src="/duachuot.jpg", width="96px", height="96px"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Tổng đơn hàng: 100.000đ"),
                        justify="end",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.spacer(),
                rx.button(
                    "Mua lại",
                    color="green",
                    width="100%",
                    bg="white",
                    border="1px solid #eee",
                ),
                border="1px solid #eee",
                width="100%",
                border_radius="8px",
                bg="white",
                height="300px",
                padding="8px",
            ),
            align_items="center",
            color="black",
            width="50%",
            margin_top="2%",
            bg="#E9EDF0",
            padding="8px",
            border_radius="8px",
        ),
        width="100%",
        padding_x="3%",
    )


def index() -> rx.Component:
    return rx.vstack(
        header(),
        rx.box(
            order_history_have_items(),
            height="calc(100vh - 100px)",  # trừ chiều cao header
            overflow_y="auto",             # vùng cuộn dọc
            width="100%",
        ),
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="100vh",
    )

import reflex as rx


class State(rx.State):
    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1


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
            align_items="center",
            width="100%",
        ),
        height="100px",
        width="100%",
        bg="#0069D1",
        padding_x="2%",  # Dùng padding_x cho gọn
        align_items="center",
        justify="between",
    )


def cart() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Giỏ hàng của Bạn", size="3"),
            rx.vstack(
                rx.image(src="/cart.png", width="300px"),
            ),
            rx.button("Tiếp tục mua hàng", color="white", bg="green", size="3"),
            align_items="center",
            color="black",
            width="100%",
            margin_top="2%",
        ),
        width="100%",
        padding_x="3%",
    )


def cart_product() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.vstack(
                rx.heading("Giỏ hàng", size = "3"), width="100%", align_items="center", bg="white", padding = "4px"
            ),
            rx.vstack(
                rx.text("Giao hàng tận nơi", color="green"),
                border="1px solid #eee",
                align_items="center",
                width="100%",
                border_radius="4px",
                bg="white",
                padding = "4px",
            ),
            rx.vstack(
                rx.text("Đơn hàng có sẵn, giao ngay", size= "2", font_weight="bold"),
                rx.hstack(
                    rx.vstack(rx.image(src="/Do-kho.jpg", width = "50px"), rx.link("Xóa")),
                    rx.text("Thùng nước"),
                    rx.vstack(
                        rx.text("79.000đ"),
                        rx.hstack(
                            rx.button("-", color="#0069D1",bg= "#E4E9F2", on_click=State.decrement),
                            rx.text(State.count),
                            rx.button("+", color="#0069D1",bg= "#E4E9F2", on_click=State.increment),
                            border = "0.5px solid #E4E9F2",
                            border_radius = "4px"
                        ),
                    ),
                    justify="between",
                    align_items="center",
                    width="100%",
                    padding = "4px"
                ),
                width="100%",
                bg = "white",
                border_radius = "4px",
            ),
            rx.vstack(
                rx.text("Thông tin thanh toán", size="2", font_weight="bold"),
                rx.vstack(
                    rx.hstack(
                        rx.text("Tiền hàng"),
                        rx.text("79.000đ"),
                        width="100%",
                        justify="between",
                    ),
                    rx.hstack(
                        rx.text("Phí giao dịch, phụ phí"),
                        rx.text("15.000đ"),
                        width="100%",
                        justify="between",
                    ),
                    rx.hstack(
                        rx.text("Tổng đơn hàng"),
                        rx.text("94.000đ"),
                        width="100%",
                        justify="between",
                    ),
                    width="100%",
                    padding = "4px"
                ),
                width="100%",
                bg = "white",
                border_radius = "4px",
            ),
            rx.vstack(
                rx.vstack(
                    rx.heading("Thanh toán(tiền mặt, thẻ, chuyển khoản, ví...)", size="3"),
                ),
                rx.hstack(
                    rx.hstack(
                        rx.icon(tag="wallet"),
                        rx.text("Tiền mặt khi nhận hàng"),
                    ),
                    rx.link("Đổi >"),
                    border="1px solid #eee",
                    border_radius="4px",
                    padding="1%",
                    bg="#F5FFF3",
                    justify="between",
                    align_items="center",
                    width="100%",
                ),
                width = "100%",
                bg = "white",
                border_radius = "4px",
                padding = "4px"
            ),
            rx.vstack(rx.button(rx.icon(tag="trash"), rx.text("Xóa hết sản phẩm"), bg = "#F2F5F9", color = "black"), padding = "2%"),
            rx.hstack(
                rx.button(
                    rx.icon(tag="store"), rx.text("Đặt hàng"), rx.text("94.000đ"),
                    width = "100%",
                    padding = "8px",
                    bg = "green"
                ),
                width = "100%",
            ),
            bg="#F2F5F9",
            padding_x="1%",
            align_items="center",
            width = "50%"
        ),
        color="black",
        align_items="center",
        width="100%",
        margin_top ="0.5%"
    )


def index() -> rx.Component:
    """Hàm dựng giao diện chính của trang chủ."""
    return rx.vstack(
        header(),
        cart_product(),
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="100vh",
    )

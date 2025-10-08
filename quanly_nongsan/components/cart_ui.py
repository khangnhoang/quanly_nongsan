import reflex as rx
from ..states.cart_backend import CartState
from ..states.login_backend import State as LoginState


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


def cart_no_item() -> rx.Component:
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


def cart_item() -> rx.Component:
    def row_view(it: dict):
        return rx.hstack(
            rx.vstack(
                rx.image(src=it["image_url"], width="50px"),
                rx.link("Xóa"),  # gắn handler xóa nếu bạn muốn
            ),
            rx.text(it["name"]),
            rx.vstack(
                rx.text(f"{it['price']:,} đ".replace(",", ".")),
                rx.hstack(
                    rx.button(
                        "-",
                        on_click=lambda: CartState.decrement_item(it["cart_item_id"]),
                        color="#0069D1",
                        bg="#E4E9F2",
                    ),
                    rx.text(it["quantity"]),
                    rx.button(
                        "+",
                        on_click=lambda: CartState.increment_item(it["cart_item_id"]),
                        color="#0069D1",
                        bg="#E4E9F2",
                    ),
                    border="0.5px solid #E4E9F2",
                    border_radius="4px",
                    padding_x="6px",
                ),
            ),
            rx.text(f"{it['line_total']:,} đ".replace(",", ".")),
            justify="between",
            align_items="center",
            width="100%",
            padding="4px",
        )

    return rx.center(
        rx.vstack(
            rx.vstack(
                rx.heading("Giỏ hàng", size="3"),
                width="100%",
                align_items="center",
                bg="white",
                padding="4px",
            ),
            rx.vstack(
                rx.text("Đơn hàng có sẵn, giao ngay", size="2", font_weight="bold"),
                rx.foreach(CartState.items, row_view),
                width="100%",
                bg="white",
                border_radius="4px",
                border="1px solid #eee",
                padding="4px",
            ),
            rx.vstack(
                rx.text("Thông tin thanh toán", size="2", font_weight="bold"),
                rx.vstack(
                    rx.hstack(
                        rx.text("Tiền hàng"),
                        rx.text(f"{CartState.total:,} đ".replace(",", ".")),
                        width="100%",
                        justify="between",
                    ),
                    width="100%",
                    padding="4px",
                ),
                width="100%",
                bg="white",
                border_radius="4px",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="wallet"),
                    rx.text("Tiền mặt khi nhận hàng"),
                    justify="between",
                    align_items="center",
                    width="100%",
                ),
                width="100%",
                bg="white",
                border_radius="4px",
                padding="8px",
            ),
            rx.hstack(
                rx.button(
                    rx.icon(tag="store"),
                    rx.text("Đặt hàng"),
                    rx.text(f"{CartState.total:,} đ".replace(",", ".")),
                    width="100%",
                    padding="8px",
                    bg="green",
                    color="white",
                ),
                width="100%",
            ),
            bg="#F2F5F9",
            padding_x="1%",
            align_items="center",
            width="50%",
        ),
        color="black",
        align_items="center",
        width="100%",
        margin_top="0.5%",
    )


def index() -> rx.Component:
    """Hàm dựng giao diện chính của trang chủ."""
    return rx.vstack(
        header(),
        rx.cond(
            CartState.has_items,
            cart_item(),
            cart_no_item(),
        ),
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="100vh",
        on_mount=CartState.load_cart,
    )

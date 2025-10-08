# cart_ui.py
import reflex as rx
from .main_page_and_cart_header import header
from ..states.cart_backend import CartState
from ..states.login_backend import State as LoginState

def cart_no_item() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Giỏ hàng của Bạn", size="3"),
            rx.vstack(rx.image(src="/cart.jpg", width="300px")),
            rx.link(rx.button("Tiếp tục mua hàng", color="white", bg="green", size="3"), href="/"),
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
                rx.link(
                    "Xóa",
                    on_click=CartState.delete_item(it["cart_item_id"]),  # NEW
                    style={"cursor": "pointer", "textDecoration": "underline"},
                ),
            ),
            rx.text(it["name"]),
            rx.vstack(
                rx.text(f"{it['price']:,} đ".replace(",", ".")),
                rx.hstack(
                    rx.button(
                        "-",
                        on_click=CartState.decrement_item(it["cart_item_id"]),  # đổi: bỏ lambda
                        color="#0069D1",
                        bg="#E4E9F2",
                    ),
                    rx.text(it["quantity"]),
                    rx.button(
                        "+",
                        on_click=CartState.increment_item(it["cart_item_id"]),  # đổi: bỏ lambda
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
            # NEW: Hàng nút hành động
            rx.hstack(
                rx.button(
                    "Xóa hết giỏ hàng",
                    on_click=CartState.clear_cart(),      # gọi hàm clear
                    variant="surface",
                    color_scheme="red",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon(tag="store"),
                    rx.text("Đặt hàng"),
                    rx.text(f"{CartState.total:,} đ".replace(",", ".")),
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
    return rx.vstack(
        header(),
        rx.cond(CartState.has_items, cart_item(), cart_no_item()),
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="100vh",
        on_mount=CartState.load_cart,
    )

import reflex as rx
from .main_page_and_cart_header import header
from ..states.order_history_backend import (
    OrderHistoryState,
    Order,
)  # <-- import Order trực tiếp
from ..states.login_backend import State as LoginState

def _status_badge(text: str, color: str) -> rx.Component:
    return rx.box(
        rx.text(text, color=color, font_weight="bold", size="2"),
        border=f"1px solid {color}",
        border_radius="9999px",
        padding_x="8px",
        padding_y="2px",
        bg="white",
    )


def _order_card(
    order: Order,
) -> rx.Component:  # <-- dùng Order (class độc lập), không phải OrderHistoryState.Order
    # Hàng card đơn
    return rx.vstack(
        # Header: mã đơn + link + trạng thái (màu)
        rx.hstack(
            rx.text(f"Đơn hàng #{order.id}", font_weight="bold"),
            rx.link("Xem chi tiết >", href=f"/product_detail?order_id={order.id}", color="black"),
            justify="between",
            align="center",
            width="100%",
            color="black",
        ),
        rx.hstack(
            _status_badge(order.status_text, order.status_color),
            justify="end",
            width="100%",
        ),
        # Ảnh sản phẩm (tối đa 4)
        rx.hstack(
            rx.foreach(
                order.product_images,
                lambda src: rx.image(src=src, width="96px", height="96px"),
            ),
            width="100%",
            wrap="wrap",
            gap="8px",
        ),
        # Tổng tiền
        rx.hstack(
            rx.text(f"Tổng đơn hàng: {order.total_price_formatted}"),
            justify="end",
            width="100%",
        ),
        # Nút mua lại: Dùng rx.link để chuyển hướng đến trang chi tiết
        rx.link(
            rx.button(
                "Mua lại",
                # on_click được loại bỏ vì đã sử dụng rx.link để chuyển hướng
                width="100%",
                bg="white",
                border="1px solid #eee",
                cursor="pointer",
                color = "black"
            ),
            href=f"/product_detail?order_id={order.id}",
            width="100%", # Quan trọng để link bao bọc hết chiều rộng của button
        ),
        
        border="1px solid #eee",
        width="100%",
        border_radius="8px",
        bg="white",
        padding="8px",
        gap="8px",
    )


def order_history_empty() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Đơn hàng từng mua", size="3", padding="4px"),
                justify="center",
                border="1px solid #eee",
                width="100%",
                height="30px",
                border_radius="8px",
                bg="white",
            ),
            rx.vstack(
                rx.icon(tag="shopping-bag"),
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

def order_history_list() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Đơn hàng từng mua", size="3", padding="4px"),
                justify="center",
                border="1px solid #eee",
                width="100%",
                height="30px",
                border_radius="8px",
                bg="white",
            ),
            # Danh sách card có thanh cuộn dọc
            rx.box(
                rx.vstack(
                    rx.foreach(OrderHistoryState.orders, _order_card),
                    gap="12px",
                    width="100%",
                ),
                max_height="60vh",
                overflow_y="auto",
                width="100%",
                padding="4px",
                bg="white",
                border_radius="8px",
                border="1px solid #eee",
            ),
            align_items="center",
            color="black",
            width="60%",
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
            rx.cond(
                OrderHistoryState.is_loading,
                # loading skeleton
                rx.center(rx.spinner(size="3"), height="100%"),
                rx.cond(
                    OrderHistoryState.has_orders,
                    order_history_list(),
                    order_history_empty(),
                ),
            ),
            height="calc(100vh - 100px)",  # trừ chiều cao header
            overflow_y="auto",
            width="100%",
        ),
        # Gọi auto-login + bootstrap đợi xong mới load
        on_mount=[
            LoginState.try_auto_login,
            OrderHistoryState.load_orders,
        ],
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="100vh",
    )
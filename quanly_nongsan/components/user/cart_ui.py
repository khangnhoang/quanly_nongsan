import reflex as rx
from .main_page_and_cart_header import header
from ...states.state import State


def cart_no_item() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(
                "Giỏ hàng của bạn đang trống",
                size="5",
                color_scheme="gray",
                color="black",
            ),
            rx.image(src="/cart.jpg", width="300px", margin_y="20px"),
            rx.link(
                rx.button("Tiếp tục mua hàng", color_scheme="grass", size="3"),
                href="/",
            ),
            align_items="center",
            color="black",
            width="100%",
        ),
        width="100%",
        height="calc(100vh - 80px)",
    )


def delivery_time_selector() -> rx.Component:
    def radio_item_view(option: dict):
        """Tạo view cho mỗi radio button để dễ quản lý style."""
        is_disabled = option["is_disabled"]
        return rx.flex(
            rx.radio_group.item(
                value=option["value"],
                disabled=is_disabled,
            ),
            rx.text(
                option["label"],
                color=rx.cond(is_disabled, "#AEAEAE", "black"),
            ),
            spacing="2",
            cursor=rx.cond(is_disabled, "not-allowed", "pointer"),
            align_items="center",
        )

    return rx.vstack(
        rx.text("Chọn thời gian giao hàng", weight="bold", color="black"),
        rx.segmented_control.root(
            rx.segmented_control.item(
                "Hôm nay", value="Hôm nay", bg="#0090FF", cursor="pointer"
            ),
            rx.segmented_control.item(
                "Ngày mai", value="Ngày mai", bg="#0090FF", cursor="pointer"
            ),
            value=rx.cond(
                State.CartState.selected_delivery_day == "hom_nay",
                "Hôm nay",
                "Ngày mai",
            ),
            on_change=lambda day: State.CartState.set_delivery_day(
                rx.cond(day == "Hôm nay", "hom_nay", "ngay_mai")
            ),
            name="delivery_day",
            color_scheme="grass",
        ),
        rx.radio_group.root(
            rx.foreach(
                State.CartState.valid_delivery_options,
                radio_item_view,
            ),
            value=State.CartState.selected_delivery_slot,
            on_change=State.CartState.set_delivery_slot,
            spacing="3",
            margin_top="10px",
            width="100%",
            cursor="pointer",
        ),
        align_items="start",
        width="100%",
        spacing="2",
    )


def cart_with_items() -> rx.Component:
    def row_view(it: dict):
        return rx.hstack(
            rx.image(
                src=it["image_url"],
                width="60px",
                height="60px",
                object_fit="cover",
                border_radius="md",
            ),
            rx.vstack(
                rx.text(it["name"], weight="bold", color="black"),
                rx.link(
                    "Xóa",
                    on_click=lambda: State.CartState.delete_item(
                        it["cart_item_id"]
                    ),  # SỬA LỖI
                    size="1",
                    color_scheme="red",
                    cursor="pointer",
                ),
                align_items="start",
                width="40%",
            ),
            rx.text(f"{it['price']:,} đ".replace(",", "."), color="black"),
            rx.hstack(
                rx.button(
                    "-",
                    on_click=lambda: State.CartState.decrement_item(
                        it["cart_item_id"]
                    ),  # SỬA LỖI
                    size="1",
                    cursor="pointer",
                ),
                rx.text(it["quantity"], margin_x="10px", weight="bold", color="black"),
                rx.button(
                    "+",
                    on_click=lambda: State.CartState.increment_item(
                        it["cart_item_id"]
                    ),  # SỬA LỖI
                    size="1",
                    cursor="pointer",
                ),
                align_items="center",
            ),
            rx.text(
                f"{it['line_total']:,} đ".replace(",", "."),
                weight="bold",
                color_scheme="ruby",
            ),
            justify="between",
            align_items="center",
            width="100%",
            padding_y="10px",
            border_bottom="1px solid #eee",
        )

    return rx.center(
        rx.hstack(
            rx.vstack(
                rx.heading("Đơn hàng của bạn", size="5", color="black"),
                rx.divider(),
                rx.foreach(State.CartState.items, row_view),
                width="60%",
                padding="20px",
                border="1px solid #eee",
                border_radius="md",
                spacing="4",
                max_height="65vh",
                overflow_y="auto",
                bg="white",
            ),
            rx.vstack(
                rx.heading("Thông tin giao hàng", size="5", color="black"),
                rx.divider(),
                rx.vstack(
                    rx.hstack(
                        rx.text("Người nhận:", width="80px", color="black"),
                        rx.text(
                            State.CartState.user_full_name, weight="bold", color="black"
                        ),
                    ),
                    rx.hstack(
                        rx.text("Điện thoại:", width="80px", color="black"),
                        rx.text(
                            State.CartState.user_phone, weight="bold", color="black"
                        ),
                    ),
                    rx.hstack(
                        rx.text("Địa chỉ:", width="80px", color="black"),
                        rx.text(
                            State.CartState.user_address, weight="bold", color="black"
                        ),
                    ),
                    align_items="start",
                    spacing="2",
                    width="100%",
                ),
                rx.divider(margin_y="10px"),
                delivery_time_selector(),
                rx.spacer(),
                rx.divider(),
                rx.hstack(
                    rx.text("Tổng tiền:", size="4", weight="bold", color="black"),
                    rx.text(
                        f"{State.CartState.total:,} đ".replace(",", "."),
                        size="6",
                        weight="bold",
                        color_scheme="ruby",
                    ),
                    justify="between",
                    width="100%",
                    align_items="center",
                ),
                rx.button(
                    "Đặt hàng ngay",
                    on_click=State.CartState.place_order,
                    is_loading=State.CartState.is_loading,
                    width="100%",
                    size="3",
                    color_scheme="grass",
                    cursor="pointer",
                ),
                rx.button(
                    "Xóa hết giỏ hàng",
                    on_click=State.CartState.clear_cart,
                    variant="soft",
                    color_scheme="red",
                    width="100%",
                    cursor="pointer",
                ),
                width="35%",
                height="100%",
                padding="20px",
                border="1px solid #eee",
                border_radius="md",
                spacing="4",
                bg="white",
            ),
            spacing="6",
            width="100%",
            max_width="1200px",
            align_items="start",
            padding_y="20px",
        ),
        width="100%",
    )


def index() -> rx.Component:
    return rx.vstack(
        header(),
        rx.box(
            rx.cond(State.CartState.has_items, cart_with_items(), cart_no_item()),
            flex_grow=1,
            width="100%",
            overflow_y="auto",
            background="#F9FAFB",
        ),
        gap="0",
        spacing="0",
        width="100%",
        height="100vh",
        align_items="stretch",
        on_mount=[State.LoginState.try_auto_login, State.CartState.load_cart],
    )
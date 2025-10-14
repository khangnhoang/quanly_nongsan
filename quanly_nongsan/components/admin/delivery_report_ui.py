import reflex as rx
from ...states.state import State
from .sidebar_ui import sidebar
from ...states.admin.delivery_report_backend import DeliveryState


def stat_card(title: str, value: rx.Var, color: str) -> rx.Component:
    return rx.vstack(
        rx.heading(value, size="7", color_scheme=color),
        rx.text(title, size="3", color="black"),
        padding="20px",
        border="1px solid #eee",
        border_radius="md",
        bg="white",
        align_items="center",
        width="100%",
    )


def main_content():
    is_selected = lambda order: DeliveryState.selected_order_ids.contains(order["id"])
    HEADERS = [
        "Mã ĐH",
        "Tên Người Nhận",
        "SĐT",
        "Địa chỉ",
        "Ngày Giao",
        "Trạng Thái",
        "Ghi Chú",
    ]

    return rx.vstack(
        rx.center(
            rx.hstack(
                rx.button("Khách hàng đã đặt", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/report_order")),
                rx.button("Quản lý giao hàng", bg="red", color="white", padding="12px", cursor="pointer", on_click=rx.redirect("/delivery_report")),
                spacing="0",
            ),
            width="100%", marginBottom="2%",
        ),
        
        rx.heading("Quản lý Giao hàng", size="7"),
        rx.divider(border_color="red"),
        rx.hstack(
            stat_card("Tổng Đơn Hàng", DeliveryState.total_orders, "blue"),
            stat_card("Giao Hôm Nay", DeliveryState.delivered_today_count, "green"),
            stat_card("Đơn Quá Hạn", DeliveryState.overdue_count, "red"),
            spacing="6",
            width="100%",
            margin_y="20px",
        ),
        rx.input(
            value=DeliveryState.search_query,
            on_change=DeliveryState.set_search_query,
            on_key_down=DeliveryState.search_on_enter,
            placeholder="Tìm kiếm đơn hàng và nhấn Enter...",
            width="100%",
            margin_bottom="10px",
            bg="whitesmoke",
            color="black",
            style={"input::placeholder": {"color": "#ccc"}},
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.text("Chọn"),
                        color="black",
                    ),
                    *[rx.table.column_header_cell(h, color="black") for h in HEADERS],
                )
            ),
            rx.table.body(
                rx.foreach(
                    DeliveryState.orders,
                    lambda order: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                checked=is_selected(order),
                                on_change=lambda checked: DeliveryState.select_order(
                                    order, checked
                                ),
                            ),
                            # Dòng này sẽ chặn sự kiện click lan ra ngoài hàng
                            on_click=rx.stop_propagation,
                        ),
                        rx.table.cell(order["id"], color="black"),
                        rx.table.cell(order["recipient_name"], color="black"),
                        rx.table.cell(order["recipient_phone"], color="black"),
                        rx.table.cell(
                            order["shipping_address"],
                            max_width="250px",
                            text_overflow="ellipsis",
                            overflow="hidden",
                            white_space="nowrap",
                            color="black",
                        ),
                        rx.table.cell(order["delivery_date_formatted"], color="black"),
                        rx.table.cell(
                            rx.badge(
                                order["status_text"], color_scheme=order["status_color"]
                            )
                        ),
                        rx.table.cell(
                            order["notes"],
                            max_width="200px",
                            text_overflow="ellipsis",
                            overflow="hidden",
                            white_space="nowrap",
                            color="black",
                        ),
                        on_click=lambda: DeliveryState.select_single_order_for_edit(
                            order
                        ),
                        cursor="pointer",
                        _hover={"background_color": "#f8f9fa"},
                        bg=rx.cond(is_selected(order), "#f0f8ff", "transparent"),
                    ),
                )
            ),
            variant="surface",
            width="100%",
        ),
        rx.cond(
            DeliveryState.is_only_one_selected,
            rx.vstack(
                rx.heading(
                    f"Chỉnh sửa đơn hàng #{DeliveryState.order_to_edit.get('id', '')}",
                    size="5",
                ),
                rx.cond(
                    DeliveryState.is_editing_disabled,
                    rx.callout(
                        "Đã quá hạn giao, không thể chỉnh sửa.",
                        icon="triangle-alert",
                        color_scheme="red",
                        variant="soft",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.select.root(
                        rx.select.trigger(placeholder="Chọn Trạng Thái"),
                        rx.select.content(
                            rx.foreach(
                                DeliveryState.status_options,
                                lambda option: rx.select.item(
                                    option[0], value=option[1]
                                ),
                            )
                        ),
                        value=DeliveryState.edited_status,
                        on_change=DeliveryState.set_edited_status,
                        disabled=DeliveryState.is_editing_disabled,
                    ),
                    rx.input(
                        value=DeliveryState.edited_delivery_date,
                        on_change=DeliveryState.set_edited_delivery_date,
                        type="date",
                        disabled=DeliveryState.is_editing_disabled,
                    ),
                    rx.input(
                        value=DeliveryState.edited_notes,
                        on_change=DeliveryState.set_edited_notes,
                        placeholder="Thêm ghi chú...",
                        disabled=DeliveryState.is_editing_disabled,
                        style={"input::placeholder": {"color": "white"}},
                    ),
                    rx.button(
                        "Cập nhật",
                        on_click=DeliveryState.update_order,
                        disabled=DeliveryState.is_editing_disabled,
                    ),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                padding="15px",
                border="1px solid #ddd",
                border_radius="8px",
                marginTop="20px",
                bg="#fafafa",
            ),
        ),
        width="100%",
        bg="white",
        padding="20px",
        height="100%",
        overflow_y="auto",
        color="black",
    )


def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        on_mount=[State.LoginState.try_auto_login, DeliveryState.on_load],
        gap="0",
        width="100%",
        height="100vh",
    )

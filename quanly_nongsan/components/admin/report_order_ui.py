import reflex as rx
from ...states.state import State
from .sidebar_ui import sidebar as sidebar

# Định nghĩa các tiêu đề cột
HEADERS = [
    "ID",
    "Tên khách hàng",
    "Tổng số đơn",
    "Số điện thoại",
    "Địa chỉ",
]


def customer_list_rows():
    """Tạo bảng hiển thị danh sách khách hàng."""
    CELL_STYLE = {
        "border": "0.5px solid #C1C1C1",
        "color": "black",
        "padding": "8px",
    }

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                *[rx.table.column_header_cell(h, style=CELL_STYLE) for h in HEADERS],
            ),
        ),
        rx.table.body(
            rx.foreach(
                State.ReportOrderState.customers,
                lambda customer: rx.table.row(
                    rx.table.cell(customer["id"], style=CELL_STYLE),
                    rx.table.cell(customer["full_name"], style=CELL_STYLE),
                    rx.table.cell(customer["total_orders"], style=CELL_STYLE),
                    rx.table.cell(customer["phone_number"], style=CELL_STYLE),
                    rx.table.cell(customer["address"], style=CELL_STYLE),
                ),
            )
        ),
        width="100%",
        style={"border_collapse": "collapse", "border": "1px solid #C1C1C1"},
    )


def main_content():
    return rx.vstack(
        rx.center(
            rx.hstack(
                rx.button("Khách hàng đã đặt", bg="red", color="white", padding="12px", cursor="pointer", on_click=rx.redirect("/report_order")),
                rx.button("Quản lý giao hàng", bg="whitesmoke", color="black", padding="12px", cursor="pointer", on_click=rx.redirect("/delivery_report")),
                spacing="0",
            ),
            width="100%", marginBottom="2%",
        ),
        
        rx.heading("Danh sách khách hàng đã đặt hàng", size="7"),
        rx.box(
            height="2px",
            bg="red",
            width="100%",
            marginTop="",
        ),
        # Khối tìm kiếm
        rx.vstack(
            rx.text("Tìm kiếm khách hàng theo Tên hoặc SĐT (nhấn Enter)", size="2"),
            rx.input(
                value=State.ReportOrderState.search_query,
                on_change=State.ReportOrderState.set_search_query,
                on_key_down=State.ReportOrderState.search_on_enter,
                width="100%",
                bg="#f1f4f9",
                color="black",
            ),
            width="100%",
            margin_y="15px",
        ),
        rx.heading("Kết quả danh sách khách hàng", size="3"),
        # Bảng danh sách khách hàng
        rx.box(
            customer_list_rows(),
            width="100%",
            overflow_x="auto",
            margin_top="10px",
        ),
        width="100%",
        height="100vh",
        bg="white",
        color="black",
        padding="20px",
    )


def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        main_content(),
        # Tải danh sách khách hàng khi component được mount
        on_mount=State.ReportOrderState.load_customers,
        gap="0",
        max_width="100%",
        height="100vh",
    )
import reflex as rx

# --- IMPORT LOGIC VÀ CẤU TRÚC DỮ LIỆU ---
from ...states.user.history_order_backend import OrderHistoryState, Order
# Import header từ file có sẵn của bạn
from .main_page_and_cart_header import header 


# --- Component con: Hiển thị danh sách sản phẩm (hình ảnh) trong 1 hóa đơn ---
def order_item_images(items: rx.Var[list]) -> rx.Component:
    """Hiển thị các hình ảnh sản phẩm trong một đơn hàng."""
    return rx.hstack(
        rx.text("Sản phẩm: ", font_weight="bold"),
        rx.foreach(
            items,
            # 'item' ở đây là một OrderItem (rx.Base)
            lambda item: rx.image(
                src=item.image_url,
                alt=item.product_name,
                width="50px",
                height="50px",
                object_fit="cover",
                border_radius="5px",
                margin_right="5px",
                # Hiển thị thông tin khi di chuột vào ảnh
                tooltip=rx.tooltip(f"{item.product_name} x {item.quantity} - {item.price * item.quantity:,} VND"),
            )
        ),
        spacing="3",
        wrap="wrap",
        padding_top="10px"
    )

# --- Component chính: Hiển thị chi tiết 1 hóa đơn ---
def order_card(order: rx.Var[Order]) -> rx.Component:
    """Hiển thị chi tiết của một đơn hàng."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                # Sửa lỗi: size="md" -> size="5"
                rx.heading(f"Đơn hàng #{order.order_id}", size="5"),
                rx.spacer(),
                # Hiển thị trạng thái
                rx.badge(
                    order.status, 
                    color_scheme="blue" if order.status in ["Đã đặt", "Đang giao"] else "green" if order.status == "Đã nhận" else "red",
                    padding_x="10px",
                    padding_y="5px",
                    border_radius="full",
                ),
            ),
            rx.divider(margin_y="5px"),
            rx.hstack(
                # Sửa lỗi: size="sm" -> size="2"
                rx.text(f"Ngày đặt: {order.order_date}", size="2", color="gray.600"),
                rx.spacer(),
                # Sửa lỗi: size="md" -> size="3"
                rx.text(f"Tổng tiền:", font_weight="bold", size="3"),
                # Sửa lỗi: size="md" -> size="3"
                rx.text(f"{order.total_amount:,} VND", color="red.600", font_weight="bold", size="3"),
            ),
            # Hiển thị hình ảnh sản phẩm
            order_item_images(order.items),
        ),
        width="100%",
        box_shadow="lg",
        bg="white",
        border_radius="10px",
        padding="20px"
    )

# --- Trang Lịch sử Đơn hàng ---
@rx.page(on_load=OrderHistoryState.load_order_history)
def order_history_page() -> rx.Component:
    """Render trang lịch sử đơn hàng."""
    return rx.vstack(
        header(), # Sử dụng header đã có
        rx.center(
            rx.vstack(
                # Sửa lỗi: size="xl" -> size="8" (Kích thước lớn cho tiêu đề)
                rx.heading("Lịch sử Đơn hàng", size="8", margin_bottom="30px", color="#0069D1"),
                
                # Hiển thị trạng thái tải
                rx.cond(
                    OrderHistoryState.is_loading,
                    # Sửa lỗi: size="xl" -> size="8"
                    rx.spinner(size="8", margin_top="50px"),
                    
                    # Hiển thị danh sách đơn hàng hoặc thông báo không có
                    rx.cond(
                        OrderHistoryState.orders,
                        rx.vstack(
                            rx.foreach(OrderHistoryState.orders, order_card),
                            spacing="5",
                            width="100%",
                        ),
                        rx.vstack(
                            # Sửa lỗi: size="8" -> size="7" (Kích thước lớn cho icon)
                            rx.icon(tag="file-text", size="7", color="gray.400"), 
                            # Sửa lỗi: size="lg" -> size="5"
                            rx.text("Bạn chưa có đơn hàng nào.", size="5", margin_y="10px"),
                            rx.link(rx.button("Tiếp tục mua sắm", color_scheme="green"), href="/"),
                            margin_top="50px",
                        )
                    )
                ),
                
                width="95%",
                max_width="1000px",
                padding="20px",
                bg="white",
                border_radius="10px",
                box_shadow="xl",
            ),
            width="100%",
            min_height="80vh",
            padding_top="50px",
            padding_bottom="50px",
            bg="#f0f2f5",
        ),
    )

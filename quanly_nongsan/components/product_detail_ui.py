# C:\quanly_nongsan\quanly_nongsan\pages\product_detail_ui.py
import reflex as rx
from .main_page_and_cart_header import header
from ..states.product_detail_backend import ProductDetailState, OrderItem

def _order_item_row(item: OrderItem) -> rx.Component:
    """Tạo một hàng giao diện cho từng sản phẩm trong đơn hàng."""
    return rx.hstack(
        rx.image(src=item.image_url, width="96px", height="96px", border_radius="4px"),
        rx.vstack(
            rx.text(item.product_name, font_weight="bold"),
            rx.text(f"Số lượng: {item.quantity}"),
            align_items="start",
            width="100%",
        ),
        rx.text(item.unit_price_formatted, font_weight="medium", white_space="nowrap"),
        width="100%",
        gap="12px",
        align="center",
        border_bottom="1px solid #eee",
        padding_y="8px",
    )

def product_detail_view() -> rx.Component:
    """Giao diện chính hiển thị chi tiết đơn hàng."""
    return rx.center(
        rx.vstack(
            # Header (40px)
            rx.hstack(
                rx.link(rx.icon(tag="chevron-left"), href="/order_history", padding="4px"),
                rx.heading(f"Đơn hàng #{ProductDetailState.order_id}", size="5"),
                width="100%",
                justify="center",
                padding="4px",
                bg="white",
                height="40px",
                border_bottom="1px solid #eee",
                position="relative"
            ),
            
            # Vùng nội dung có thể cuộn
            # FIX: Xoá height cố định để rx.box chỉ chiếm đủ không gian cần thiết
            rx.box(
                rx.vstack(
                    # Danh sách các sản phẩm
                    rx.vstack(
                        rx.foreach(
                            ProductDetailState.order_items,
                            _order_item_row
                        ),
                        bg="white",
                        width="100%",
                        padding="8px",
                    ),
                    # Tổng tiền
                    rx.hstack(
                        rx.text("Tổng tiền:", font_weight="bold"),
                        rx.text(ProductDetailState.grand_total, font_weight="bold"),
                        width="100%",
                        justify="end",
                        padding="8px",
                        bg="white",
                    ),
                    width="100%",
                    gap="0",
                ),
                # Đặt chiều cao max-content cho vùng cuộn để nó hiển thị toàn bộ nội dung
                # Nếu nội dung quá dài, trang tổng thể sẽ cuộn
                height="auto", 
                overflow_y="visible", # Bỏ cuộn riêng cho box này
                width="100%",
            ),

            # Footer với nút Mua lại (Nằm sát ngay dưới Tổng tiền)
            rx.hstack(
                rx.button(
                    "Mua lại", 
                    on_click=ProductDetailState.reorder_from_detail,
                    cursor="pointer",
                    bg="green", 
                    color="white", 
                    width="100%"
                ),
                width="100%",
                padding="8px",
                bg="white",
                border_top="1px solid #eee",
            ),
            
            # Container ngoài cùng (Vstack chính)
            width=["100%", "80%", "60%", "50%"], # Responsive width
            max_width="720px",
            bg="#F2F5F9",
            color="black",
            # FIX: Chiều cao tối thiểu, cho phép nội dung dài hơn màn hình
            min_height="calc(100vh - 50px)", 
            height="auto",
            gap="0",
        ),
        width="100%",
    )

def index() -> rx.Component:
    """Trang chi tiết đơn hàng hoàn chỉnh."""
    return rx.vstack(
        header(),
        rx.box(
            rx.cond(
                ProductDetailState.is_loading,
                rx.center(rx.spinner(size="3"), height="100%"),
                product_detail_view(),
            ),
            on_mount=ProductDetailState.load_order_details,
            # FIX: Cho phép index cuộn toàn bộ nếu nội dung (product_detail_view) dài
            height="auto", 
            min_height="calc(100vh - 50px)",
            overflow_y="visible",
            width="100%",
        ),
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="auto", # FIX: Chiều cao tự động
    )
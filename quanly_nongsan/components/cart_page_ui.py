import reflex as rx

# Import CartState từ backend
from ..states.cart_backend import CartState 

# Component cho từng dòng sản phẩm trong giỏ hàng
def cart_item_row(item: rx.Var[dict], index: rx.Var[int]) -> rx.Component:
    """Hiển thị một sản phẩm duy nhất trong giỏ hàng."""
    
    return rx.hstack(
        # Ảnh sản phẩm
        rx.image(
            src=item["image_url"],
            width="60px",
            height="60px",
            object_fit="cover",
            border_radius="5px",
        ),
        
        # Tên sản phẩm
        rx.text(item["name"], font_weight="bold", width="40%", min_width="200px"),
        
        # Giá đơn vị
        rx.text(item["price"], width="15%", color="red"),
        
        # Số lượng (hiển thị đơn giản)
        rx.center(
            rx.text(item["quantity"], width="100%"),
            width="10%",
        ),
        
        # Nút xóa
        rx.button(
            rx.icon(tag="trash-2"),
            on_click=CartState.remove_item(index), # Gọi hàm xóa dựa trên chỉ mục (index)
            size="sm",
            color_scheme="red",
            variant="ghost",
        ),
        
        width="100%",
        padding="10px",
        border_bottom="1px solid #eee",
        align_items="center",
        justify="start",
        gap="10px",
    )


def cart_page() -> rx.Component:
    """Hàm dựng giao diện trang giỏ hàng."""
    return rx.center(
        rx.vstack(
            rx.heading("🛒 Giỏ hàng của bạn", size="xl", margin_bottom="20px"),
            
            # --- Tiêu đề cột ---
            rx.cond(
                CartState.cart_items,
                rx.hstack(
                    rx.text("Sản phẩm", font_weight="bold", width="40%", min_width="260px"),
                    rx.text("Giá", font_weight="bold", width="15%"),
                    rx.text("Số lượng", font_weight="bold", width="10%"),
                    rx.spacer(),
                    rx.button("Xóa tất cả", on_click=CartState.clear_cart, size="sm", variant="link", color_scheme="red"),
                    width="100%",
                    padding="10px",
                    border_bottom="2px solid #0069D1",
                    align_items="center",
                    justify="start",
                ),
            ),
            
            # --- Danh sách sản phẩm ---
            rx.cond(
                # Nếu giỏ hàng có sản phẩm
                CartState.cart_items,
                rx.vstack(
                    rx.foreach(
                        CartState.cart_items, 
                        # Hàm lambda để lấy cả item và index
                        lambda item, index: cart_item_row(item, index)
                    ),
                    width="100%",
                    spacing="0",
                ),
                # Nếu giỏ hàng trống
                rx.center(
                    rx.vstack(
                        rx.icon(tag="shopping-bag", size="9"),
                        rx.text("Giỏ hàng của bạn đang trống."),
                        rx.link(rx.button("Quay về trang chủ"), href="/"),
                    ),
                    height="300px",
                ),
            ),
            
            # --- Tổng tiền & Thanh toán ---
            rx.cond(
                CartState.cart_items,
                rx.vstack(
                    rx.hstack(
                        rx.text("Tổng tiền:", font_weight="bold", size="md"),
                        rx.spacer(),
                        rx.text(CartState.calculate_total(), color="red", font_weight="bold", size="xl"),
                        width="100%",
                        padding_top="20px",
                        justify="between",
                    ),
                    rx.button(
                        "Tiến hành Thanh toán",
                        width="100%",
                        size="lg",
                        color_scheme="green",
                        margin_top="15px",
                    ),
                    width="100%",
                    border_top="2px solid #eee",
                    padding_top="10px",
                ),
            ),

            width="90%",
            max_width="1000px",
            padding="20px",
            bg="white",
            border_radius="10px",
            box_shadow="lg",
        ),
        width="100%",
        min_height="80vh",
        padding_top="50px",
        padding_bottom="50px",
        bg="#F5F5F5",
    )
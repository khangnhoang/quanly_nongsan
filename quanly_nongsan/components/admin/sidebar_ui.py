import reflex as rx
from ...states.state import State

def sidebar_link(text: str, icon: str, hrefs: str | list[str]) -> rx.Component:
    """
    Một component link cho sidebar có thể thay đổi style khi được chọn.
    hrefs có thể là một chuỗi đơn hoặc một danh sách các chuỗi.
    """
    # Xác định URL chính để điều hướng (luôn là phần tử đầu tiên nếu là list)
    primary_href = hrefs[0] if isinstance(hrefs, list) else hrefs
    
    # Xây dựng điều kiện để xác định trạng thái active
    is_active = rx.Var.create(False) # Tạo một biến điều kiện ban đầu
    
    routes_to_check = hrefs if isinstance(hrefs, list) else [hrefs]
    for route in routes_to_check:
        is_active |= (State.router.page.path == route)

    return rx.link(
        rx.box(
            rx.hstack(
                rx.icon(icon, color="orange"),
                rx.text(
                    text,
                    color=rx.cond(is_active, "white", "black"),
                    font_weight=rx.cond(is_active, "bold", "normal"),
                ),
                width="100%",
                bg=rx.cond(is_active, "red", "transparent"),
                padding="4px",
                border_radius="4px",
            ),
            width="100%",
        ),
        href=primary_href, # Điều hướng đến URL chính
        width="100%",
    )


def sidebar() -> rx.Component:
    """A reusable sidebar component for the application."""
    return rx.vstack(
        rx.hstack(
            rx.spacer(), rx.icon("x", cursor="pointer"), width="100%", align="center"
        ),
        rx.image(
            src="/logo.png",
            max_width="40%",
            height="auto",
            border="2px solid none",
            boxShadow="0 0 10px rgba(255, 0, 0, 0.75)",
            marginTop="10%",
        ),
        rx.box(height="1px", bg="black", width="100%", margin_y="5%"),
        rx.vstack(
            rx.heading(
                rx.hstack(
                    rx.icon("house"),
                    rx.text("Tồn kho và bán hàng"),
                    spacing="2",
                    align="center",
                ),
                size="4",
            ),
            rx.box(height="1px", bg="black", width="100%", marginTop="2px"),
            
            # --- ÁP DỤNG LOGIC MỚI TẠI ĐÂY ---
            
            # Link "Khai báo" sẽ active với 1 trong 4 routes
            sidebar_link(
                "Khai báo", 
                "user-round-check", 
                ["/product_types", "/product_category", "/image_page", "/customer"]
            ),
            
            # Link "Báo Cáo" sẽ active với 1 trong 2 routes
            sidebar_link(
                "Báo Cáo", 
                "bar-chart", 
                ["/report_order", "/delivery_report"]
            ),
            
            # Link "Tài khoản" vẫn như cũ (chỉ có 1 route)
            sidebar_link("Tài khoản", "key-round", "/change_password"),

            width="95%",
            spacing="2",
            border="3px solid #cac8c6",
            bg="#cac8c6",
            border_radius="4px",
            padding="8px",
            text_align="left",
        ),
        rx.spacer(),
        rx.vstack(
            rx.heading(
                "Xin chào: ",
                State.LoginState.current_user["fullname"],
                size="5",
                text_align="left",
            ),
            rx.button(
                "Đăng xuất",
                bg="lightgray",
                color="black",
                border="1px solid",
                cursor="pointer",
                on_click=State.LoginState.handle_logout,
            ),
            marginTop="auto",
        ),
        width="25%",
        height="100vh",
        padding="10px",
        bg="#f0f4f8",
        color="black",
        align="center",
        position="sticky",
        top="0",
    )
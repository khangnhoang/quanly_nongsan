import reflex as rx
from ..states.state import State 


def sidebar() -> rx.Component:
    """A reusable sidebar component for the application."""
    return rx.vstack(
        rx.hstack(
            rx.spacer(), rx.icon("x", cursor="pointer"), width="100%", align="center"
        ),
        rx.image(
            src="/logo.png",
            max_width="40%",
            height="auto",  # Sử dụng auto để giữ tỷ lệ ảnh
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
                size="4",  # Chỉnh size cho phù hợp
            ),
            rx.box(height="1px", bg="black", width="100%", marginTop="2px"),
            rx.link(
                rx.box(
                rx.hstack(
                    rx.icon("user-round-check", color="orange"),
                    rx.text("Khai báo", color="white", font_weight="bold"),
                    width="100%",
                    bg="red",
                    padding="4px",
                    border_radius="4px",
                ),
                width="100%",
            ),
                href="/product_types",
                color = "black",
                width = "100%",
            ),
            rx.box(
                rx.hstack(
                    rx.icon("package", color="orange"),
                    rx.text("Quản lí kho"),
                    width="100%",
                    bg="none",
                    padding="4px",
                    border_radius="4px",
                ),
            ),
            rx.box(
                rx.hstack(
                    rx.icon("dollar-sign", color="orange"),
                    rx.text("Bán hàng"),
                    width="100%",
                    bg="none",
                    padding="4px",
                    border_radius="4px",
                )
            ),
            rx.box(
                rx.hstack(
                    rx.icon("bar-chart", color="orange"),
                    rx.text("Báo Cáo"),
                    width="100%",
                    bg="none",
                    padding="4px",
                    border_radius="4px",
                )
            ),
            rx.link(
                rx.box(
                rx.hstack(
                    rx.icon("users", color="orange"),
                    rx.text("Tài khoản"),
                    width="100%",
                    bg="none",
                    padding="4px",
                    border_radius="4px",
                ),
            ),
                href="/change_password",
                color = "black",
                width = "100%",
            ),
            width="95%",
            spacing="2",
            border="3px solid #cac8c6",
            bg="#cac8c6",
            border_radius="4px",
            padding="8px",
            text_align="left",
        ),
        rx.spacer(),  # Đẩy nội dung xuống dưới cùng
        rx.vstack(
            rx.heading("Xin chào: ", State.LoginState.current_user["fullname"], size="5", text_align="left"),
            rx.button(
                "Đăng xuất",
                bg="lightgray",
                color="black",
                border="1px solid",
                cursor="pointer",
                on_click=State.LoginState.handle_logout,
                
            ),
            marginTop="auto",  # Đẩy lên trên cùng của vstack này
        ),
        width="25%",
        height="100vh",
        padding="10px",
        bg="#f0f4f8",
        color="black",
        align="center",
        position="sticky",  # Giữ sidebar cố định khi cuộn
        top="0",
    )
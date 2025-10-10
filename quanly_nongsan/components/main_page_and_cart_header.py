import reflex as rx
from ..states.main_page_backend import MainPageState

def header() -> rx.Component:
    """Component cho phần header đầu trang."""
    return rx.hstack(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/logonongsan.png", width="90px", height="90px"),
                    rx.center(
                        rx.text("MyWorldtoFarm.com"),
                    ),
                    align_items="center",
                ),
                width="30%",
                href="/",  # Link về trang chủ
            ),
            rx.hstack(
                rx.center(
                    rx.input(placeholder="Tìm kiếm", width="100%", height="40px"),
                    rx.button(rx.icon(tag="search"), height="40px"),
                    width="60%",
                    align_items="center",
                ),
                width="100%",
                align_items="center",
            ),
            rx.hstack(
                rx.link(
                    rx.vstack(
                        rx.icon(tag="shopping-bag"),
                        rx.text("Cart"),
                        width="100%",
                        color="white",
                    ),
                    href="/cart",  # Link tới giỏ hàng
                ),
                rx.cond(
                MainPageState.LoginState.current_user,
                # Nếu ĐÃ đăng nhập (current_user không rỗng)
                rx.hstack(
                     rx.link(
                        rx.vstack(
                            rx.icon(tag="user"),
                            rx.text(MainPageState.LoginState.current_user.get("fullname", "User")),
                            width="100%",
                            color="white",
                        ),
                        href="/customer" # Chuyển đến trang thông tin khách hàng
                    ),
                    rx.link(
                        rx.vstack(
                           rx.icon(tag="log-out"),
                           rx.text("Logout"),
                           width="100%",
                           color="white",
                        ),
                       on_click=MainPageState.LoginState.handle_logout
                    )
                ),
                # Nếu CHƯA đăng nhập (current_user rỗng)
                rx.link(
                    rx.vstack(
                        rx.icon(tag="user"),
                        rx.text("Login"),
                        width="100%",
                        color="white",
                    ),
                    href="/login_page",
                ),
            )
        ),
            align_items="center",
            width="100%",
        ),
        height="100px",
        width="100%",
        bg="#0069D1",
        padding_x="2%",  # Dùng padding_x cho gọn
        align_items="center",
        justify="between",
    )
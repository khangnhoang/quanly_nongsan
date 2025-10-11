import reflex as rx
from ..states.main_page_backend import MainPageState

def header() -> rx.Component:
    """Component cho phần header đầu trang."""
    return rx.hstack(
        rx.link(
            rx.hstack(
                rx.image(src="/logonongsan.png", width="90px", height="auto"),
                rx.center(
                    rx.text("MyWorldtoFarm.com", color="white", weight="bold"),
                ),
                align_items="center",
            ),
            href="/",
            _hover={"opacity": 0.8},
            transition="opacity 0.2s ease",
        ),
        rx.center(
            rx.input(placeholder="Tìm kiếm sản phẩm bạn mong muốn...", width="400px", height="40px"),
            rx.button(rx.icon(tag="search"), height="40px", cursor="pointer"),
            spacing="0",
        ),
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.icon(tag="shopping-bag"),
                    rx.text("Cart"),
                    spacing="2",
                    align_items="center",
                ),
                href="/cart",
                color="white",
                _hover={"opacity": 0.8},
                transition="opacity 0.2s ease",
            ),
            rx.link(
                rx.hstack(
                    rx.icon(tag="history"),
                    rx.text("Lịch sử"),
                    spacing="2",
                    align_items="center",
                ),
                href="/order_history",
                color="white",
                _hover={"opacity": 0.8},
                transition="opacity 0.2s ease",
            ),
            rx.cond(
                MainPageState.LoginState.current_user,
                # Nếu ĐÃ đăng nhập
                rx.hstack(
                    rx.link(
                        rx.hstack(
                            rx.icon(tag="user"),
                            rx.text(MainPageState.LoginState.current_user.get("fullname", "User")),
                            spacing="2",
                            align_items="center",
                        ),
                        href="/customer",
                        color="white",
                        _hover={"opacity": 0.8},
                        transition="opacity 0.2s ease",
                    ),
                    rx.link(
                        rx.hstack(
                           rx.icon(tag="log-out"),
                           rx.text("Logout"),
                           spacing="2",
                           align_items="center",
                        ),
                        on_click=MainPageState.LoginState.handle_logout,
                        color="white",
                        cursor="pointer",
                        _hover={"opacity": 0.8},
                        transition="opacity 0.2s ease",
                    ),
                    spacing="4",
                ),
                # Nếu CHƯA đăng nhập
                rx.link(
                    rx.hstack(
                        rx.icon(tag="user"),
                        rx.text("Login"),
                        spacing="2",
                        align_items="center",
                    ),
                    href="/login_page",
                    color="white",
                    _hover={"opacity": 0.8},
                    transition="opacity 0.2s ease",
                ),
            ),
            spacing="4", # Khoảng cách giữa các mục
        ),
        height="100px",
        width="100%",
        bg="#0069D1",
        padding_x="2%",
        align_items="center",
        justify="between",
    )
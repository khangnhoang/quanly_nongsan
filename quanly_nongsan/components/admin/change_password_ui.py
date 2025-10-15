import reflex as rx
from ...states.state import State
from .sidebar_ui import sidebar


def main_content() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.center(
                # Bọc các nút trên cùng trong hstack để xếp ngang
                rx.hstack(
                    rx.button("Password", bg="red", color="white", cursor="pointer"),

                    # --- THÊM NÚT "QUAY LẠI" CÓ ĐIỀU KIỆN TẠI ĐÂY ---
                    rx.cond(
                        State.LoginState.current_user["role"] == "user",
                        rx.button(
                            "Quay lại",
                            on_click=rx.redirect("/main_page"),
                            bg="gray",
                            color="white",
                            cursor="pointer",
                        ),
                    ),
                    spacing="0",
                ),
                width="100%",
                justify_content="center", # Căn giữa các nút
                padding_bottom="10px",
            ),
            rx.vstack(
                rx.heading(
                    "Password",
                ),
                rx.text("Mật khẩu cũ", size="1"),
                rx.input(
                    value=State.LoginState.old_password,
                    on_change=State.LoginState.set_old_password,
                    width="100%",
                    bg="#F0F4F8",
                    color="black",
                    type="password",
                    style={"input::placeholder": {"color": "#ccc"}},
                ),
                rx.text("Mật khẩu mới", size="1"),
                rx.input(
                    value=State.LoginState.new_password,
                    on_change=State.LoginState.set_new_password,
                    width="100%",
                    bg="#F0F4F8",
                    color="black",
                    type="password",
                    style={"input::placeholder": {"color": "#ccc"}},
                ),
                rx.text("Xác nhận mật khẩu mới", size="1"),
                rx.input(
                    value=State.LoginState.confirm_new_password,
                    on_change=State.LoginState.set_confirm_new_password,
                    width="100%",
                    bg="#F0F4F8",
                    color="black",
                    type="password",
                    style={"input::placeholder": {"color": "#ccc"}},
                ),
                rx.button(
                    "Đổi mật khẩu",
                    on_click=State.LoginState.change_password,
                    bg="red",
                    color="white",
                    cursor="pointer",
                ),
                width="100%",
            ),
            width="100%",
            padding="18px",
        ),
        width="100%",
        bg="white",
        color="black",
        height="100vh",
    )


def index() -> rx.Component:
    return rx.hstack(
        # Logic ẩn sidebar cho user vẫn được giữ nguyên
        rx.cond(
            State.LoginState.current_user["role"] != "user",
            sidebar(),
            rx.fragment(),
        ),
        main_content(),
        gap="0",
        on_mount=State.LoginState.try_auto_login
    )
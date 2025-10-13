import reflex as rx
from .sidebar_ui import sidebar

def index () -> rx.Component:
    return rx.hstack(
        sidebar
    )
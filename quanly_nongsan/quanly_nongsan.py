"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from .components.report_order_ui import index as report_order_page

class State(rx.State):
    """The app state."""




app = rx.App()
app.add_page(report_order_page, route="/report_order")

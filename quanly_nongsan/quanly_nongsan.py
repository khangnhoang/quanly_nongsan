import reflex as rx
from .main_page_ui import index as main_page

app = rx.App()
app.add_page(main_page, route = "/main_page")

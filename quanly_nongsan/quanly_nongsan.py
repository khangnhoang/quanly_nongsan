import reflex as rx
from quanly_nongsan.components.main_page_ui import index as main_page
from .components.login_ui import index as login_page
from .components.cart import index as cart_page

app = rx.App()
app.add_page(main_page, route="/")
app.add_page(main_page, route="/main_page")
app.add_page(login_page, route="/login_page")
app.add_page(cart_page, route="/cart")

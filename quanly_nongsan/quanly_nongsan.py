import reflex as rx
from .components.product_category_ui import index as product_category_page
from .components.product_types_ui import index as product_types_page
from .components.customer_ui import index as customer
from .components.images_ui import image_page as image_page
from .components.login_ui import index as login_page
from .components.change_password_ui import index as change_password_page
from quanly_nongsan.components.main_page_ui import index as main_page
from .components.login_ui import index as login_page
from .components.cart_ui import index as cart_page

app = rx.App()
app.add_page(login_page, route="/")
app.add_page(login_page, route="/login_page")
app.add_page(product_types_page, route="/product_types")
app.add_page(customer, route="/customer")
app.add_page(product_category_page, route="/product_category")
app.add_page(image_page, route="/image_page")
app.add_page(change_password_page, route="/change_password")
app.add_page(main_page, route="/")
app.add_page(main_page, route="/main_page")
app.add_page(login_page, route="/login_page")
app.add_page(cart_page, route="/cart")

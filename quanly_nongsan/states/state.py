import reflex as rx
from .user.cart_backend import CartState
from .admin.login_backend import State as LoginState
from .user.main_page_backend import MainPageState
from .admin.product_types_backend import State as productState
from .admin.product_category_backend import State as productState2
from .admin.customer_backend import UserState as UserState
from .admin.images_backend import ImageState as ImageState


class State(rx.State):
    CartState = CartState
    LoginState = LoginState
    MainPageState = MainPageState
    productState = productState
    productState2 = productState2
    UserState = UserState
    ImageState = ImageState
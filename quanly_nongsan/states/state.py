import reflex as rx
from .cart_backend import CartState
from .login_backend import State as LoginState
from .main_page_backend import MainPageState
from .product_types_backend import State as productState
from .product_category_backend import State as productState2
from .customer_backend import UserState as UserState
from .images_backend import ImageState as ImageState


class State(rx.State):
    CartState = CartState
    LoginState = LoginState
    MainPageState = MainPageState
    productState = productState
    productState2 = productState2
    UserState = UserState
    ImageState = ImageState
import reflex as rx
from .cart_backend import CartState
from .login_backend import State as LoginState
from .main_page_backend import MainPageState 


class State(rx.State):
    CartState = CartState
    LoginState = LoginState
    MainPageState = MainPageState
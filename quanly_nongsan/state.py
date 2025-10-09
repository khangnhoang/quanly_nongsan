import reflex as rx
from .states.cart_backend import CartState
from .states.login_backend import State as LoginState
from .states.main_page_backend import MainPageState 


class State(rx.State):
    CartState = CartState
    LoginState = LoginState
    MainPageState = MainPageState
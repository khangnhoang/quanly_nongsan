from .report_order_backend import ReportOrderState as reportOrderState

import reflex as rx

class State(rx.State):
    ReportOrderState = reportOrderState

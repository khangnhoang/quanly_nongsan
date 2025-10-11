import reflex as rx
from .main_page_and_cart_header import header


class ProductDetailState(rx.State):
    order_id: str = ""

    def on_mount(self):
        self.order_id = self.router.page.params.get("order_id", "Không rõ mã")


def product_detail_form(order_id: str) -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.link(rx.icon(tag="chevron-left", href="/order_history")),
                rx.heading("Đơn hàng #{order_id}", size="5"),
                width="100%",
                justify="center",
                padding="4px",
                bg="white",
                height="40px",
                border="1px solid #eee",
            ),
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.image(src="/banana.jpg", width="96px", height="96px"),
                        rx.text(
                        "Quả chuối diệu kì, bổ sung vitamin chuối và một số loại vitamin khác"),
                        rx.vstack(
                            rx.text("15.000đ", font_weight="bold"),
                            rx.text("SL: 1"),
                        )
                    ),
                    rx.hstack(
                        rx.image(src="/banana.jpg", width="96px", height="96px"),
                        rx.text(
                        "Quả chuối diệu kì, bổ sung vitamin chuối và một số loại vitamin khác"),
                        rx.vstack(
                            rx.text("15.000đ", font_weight="bold"),
                            rx.text("SL: 1"),
                        )
                    ),
                    rx.hstack(
                        rx.image(src="/banana.jpg", width="96px", height="96px"),
                        rx.text(
                        "Quả chuối diệu kì, bổ sung vitamin chuối và một số loại vitamin khác"),
                        rx.vstack(
                            rx.text("15.000đ", font_weight="bold"),
                            rx.text("SL: 1"),
                        )
                    ),
                ),
                rx.hstack(
                    rx.text("Tổng tiền: 15.000đ", font_weight="bold"),
                    width="100%",
                    justify="end",
                ),
                bg="white",
                width="100%",
                padding="8px",
            ),
            rx.hstack(
                rx.button("Mua lại", bg="green", color="white", width="100%"),
                width="100%",
                padding="4px",
                bg="white",
                border="1px solid #eee",
            ),
            width="50%",
            bg="#F2F5F9",
            color="black",
        ),
        width="100%",
    )


def index() -> rx.Component:
    return rx.vstack(
        header(),
        rx.box(
            rx.cond(
                ProductDetailState.order_id != "",
                product_detail_form(ProductDetailState.order_id),
                rx.text("Đang tải chi tiết đơn hàng..."),
            ),
            on_mount=[ProductDetailState.on_mount],
            height="calc(100vh - 100px)",  # trừ chiều cao header
            overflow_y="auto",  # vùng cuộn dọc
            width="100%",
        ),
        bg="#F5F5F5",
        gap="0",
        width="100%",
        height="100vh",
    )

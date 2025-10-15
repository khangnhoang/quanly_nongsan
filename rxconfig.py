import reflex as rx

config = rx.Config(
    app_name="quanly_nongsan",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
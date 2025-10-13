import reflex as rx
from typing import List, Optional
from sqlmodel import Field, Relationship, select
from sqlalchemy import Column, String, Integer, ForeignKey, DECIMAL, DateTime, Date
from datetime import datetime, date


# =====================================================
# I. REFLEX ORM MODELS (Ánh xạ tới Database)
# =====================================================

class ProductType(rx.Model, table=True):
    __tablename__ = "ProductTypes"

    id: Optional[int] = Field(default=None, sa_column=Column("ID", Integer, primary_key=True))
    code: str = Field(sa_column=Column("Code", String))
    name: str = Field(sa_column=Column("Name", String))
    created_at: Optional[datetime] = Field(sa_column=Column("CreatedAt", DateTime))

    # Một ProductType có nhiều Product
    products: List["Product"] = Relationship(back_populates="product_type_ref")


class Image(rx.Model, table=True):
    __tablename__ = "Images"

    id: Optional[int] = Field(default=None, sa_column=Column("STT", Integer, primary_key=True))
    image_url: str = Field(sa_column=Column("ImageURL", String))
    alt_text: Optional[str] = Field(sa_column=Column("AltText", String))
    created_at: Optional[datetime] = Field(sa_column=Column("CreatedAt", DateTime))


class Product(rx.Model, table=True):
    __tablename__ = "Products"

    id: Optional[int] = Field(default=None, sa_column=Column("ID", Integer, primary_key=True))
    name: str = Field(sa_column=Column("Name", String))
    product_code: Optional[str] = Field(sa_column=Column("ProductCode", String))
    expiry_date: Optional[date] = Field(sa_column=Column("ExpiryDate", Date))
    notes: Optional[str] = Field(sa_column=Column("Notes", String))
    product_type_id: Optional[int] = Field(sa_column=Column("ProductTypeID", Integer, ForeignKey("ProductTypes.ID")))
    primary_image_id: Optional[int] = Field(sa_column=Column("PrimaryImageID", Integer, ForeignKey("Images.STT")))
    price: float = Field(sa_column=Column("Price", DECIMAL(18, 2)))
    product_type: str = Field(sa_column=Column("ProductType", String))

    # Quan hệ
    order_items: List["OrderItemDB"] = Relationship(back_populates="product")
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    product_type_ref: Optional["ProductType"] = Relationship(back_populates="products")


class User(rx.Model, table=True):
    __tablename__ = "Users"

    id: Optional[int] = Field(default=None, sa_column=Column("ID", Integer, primary_key=True))
    username: str = Field(sa_column=Column("Username", String))
    password_hash: Optional[str] = Field(sa_column=Column("PasswordHash", String))
    fullname: Optional[str] = Field(sa_column=Column("FullName", String))
    role: Optional[str] = Field(sa_column=Column("Role", String))
    phone_number: Optional[str] = Field(sa_column=Column("PhoneNumber", String))
    address: Optional[str] = Field(sa_column=Column("Address", String))

    # Quan hệ
    orders: List["Order"] = Relationship(back_populates="user")
    carts: List["Cart"] = Relationship(back_populates="user")


class Order(rx.Model, table=True):
    __tablename__ = "Orders"

    id: Optional[int] = Field(default=None, sa_column=Column("ID", Integer, primary_key=True))
    user_id: int = Field(sa_column=Column("UserID", Integer, ForeignKey("Users.ID")))
    order_date: datetime = Field(sa_column=Column("OrderDate", DateTime))
    receiving_date: Optional[date] = Field(sa_column=Column("ReceivingDate", Date, nullable=True))
    status: str = Field(sa_column=Column("Status", String))
    notes: Optional[str] = Field(sa_column=Column("Notes", String, nullable=True))
    recipient_name: str = Field(sa_column=Column("RecipientName", String))
    recipient_phone: str = Field(sa_column=Column("RecipientPhone", String))
    shipping_address: str = Field(sa_column=Column("ShippingAddress", String))

    user: "User" = Relationship(back_populates="orders")
    items: List["OrderItemDB"] = Relationship(back_populates="order")


class OrderItemDB(rx.Model, table=True):
    __tablename__ = "OrderItems"

    id: Optional[int] = Field(default=None, sa_column=Column("ID", Integer, primary_key=True))
    order_id: int = Field(sa_column=Column("OrderID", Integer, ForeignKey("Orders.ID")))
    product_id: int = Field(sa_column=Column("ProductID", Integer, ForeignKey("Products.ID")))
    quantity: int = Field(sa_column=Column("Quantity", Integer))

    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")


class Cart(rx.Model, table=True):
    __tablename__ = "Carts"

    id: Optional[int] = Field(default=None, sa_column=Column("CartID", Integer, primary_key=True))
    user_id: int = Field(sa_column=Column("UserID", Integer, ForeignKey("Users.ID")))
    created_at: datetime = Field(sa_column=Column("CreatedAt", DateTime))

    user: "User" = Relationship(back_populates="carts")
    items: List["CartItem"] = Relationship(back_populates="cart")


class CartItem(rx.Model, table=True):
    __tablename__ = "CartItems"

    id: Optional[int] = Field(default=None, sa_column=Column("CartItemID", Integer, primary_key=True))
    cart_id: int = Field(sa_column=Column("CartID", Integer, ForeignKey("Carts.CartID")))
    product_id: int = Field(sa_column=Column("ProductID", Integer, ForeignKey("Products.ID")))
    quantity: int = Field(sa_column=Column("Quantity", Integer))

    cart: "Cart" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="cart_items")


# =====================================================
# II. PYDANTIC DATA CLASSES (Dùng cho Reflex State)
# =====================================================

class OrderProduct(rx.Base):
    product_id: int
    name: str
    image_url: str
    quantity: int
    price: float


class OrderItem(rx.Base):
    order_id: int
    status: str
    total_amount: float
    products: List[OrderProduct]


class FormattedOrderData(rx.Base):
    order_id: int
    order_code: str
    status: str
    total_amount: str
    image_urls: List[str]


# =====================================================
# III. STATE LOGIC (Quản lý Lịch sử Đơn hàng)
# =====================================================

class OrderHistoryState(rx.State):
    current_user_id: int = 1
    orders: List[OrderItem] = []
    is_loading: bool = True

    @rx.var
    def has_orders(self) -> bool:
        return len(self.orders) > 0

    @rx.var
    def formatted_orders(self) -> List[FormattedOrderData]:
        formatted_list = []
        for order in self.orders:
            formatted_amount = f"{int(order.total_amount):,}".replace(",", ".") + "đ"
            status_vn = "Giao thành công" if order.status == "Delivered" else "Đang xử lý"
            image_urls = [p.image_url for p in order.products[:2]]

            formatted_list.append(
                FormattedOrderData(
                    order_id=order.order_id,
                    order_code=f"DH{order.order_id}",
                    status=status_vn,
                    total_amount=formatted_amount,
                    image_urls=image_urls,
                )
            )
        return formatted_list

    def load_order_history(self):
        self.is_loading = True
        self._fetch_orders_from_db()
        self.is_loading = False

    def _fetch_orders_from_db(self):
        """Truy vấn danh sách đơn hàng và sản phẩm liên quan từ database"""
        if not self.current_user_id:
            self.orders = []
            return

        try:
            with rx.session() as session:
                orders_db = session.exec(
                    select(Order)
                    .where(Order.user_id == self.current_user_id)
                    .order_by(Order.order_date.desc())
                ).all()

                final_orders: List[OrderItem] = []

                for order in orders_db:
                    items_query = (
                        select(OrderItemDB, Product, Image.image_url)
                        .join(Product, OrderItemDB.product_id == Product.id)
                        .outerjoin(Image, Product.primary_image_id == Image.id)
                        .where(OrderItemDB.order_id == order.id)
                    )

                    items_results = session.exec(items_query).all()

                    order_products: List[OrderProduct] = []
                    total_amount = 0.0

                    for item_db, product_db, image_url in items_results:
                        product_price = float(product_db.price)
                        product_quantity = item_db.quantity

                        order_products.append(
                            OrderProduct(
                                product_id=product_db.id,
                                name=product_db.name,
                                image_url=image_url if image_url else "/placeholder.jpg",
                                quantity=product_quantity,
                                price=product_price,
                            )
                        )
                        total_amount += product_price * product_quantity

                    final_orders.append(
                        OrderItem(
                            order_id=order.id,
                            status=order.status,
                            total_amount=total_amount,
                            products=order_products,
                        )
                    )

                self.orders = final_orders

        except Exception as e:
            print(f"LỖI KHI TRUY VẤN LỊCH SỬ ĐƠN HÀNG: {e}")
            self.orders = []

    def repurchase_order(self, order_id: int):
        print(f"Kích hoạt mua lại đơn hàng ID: {order_id}")

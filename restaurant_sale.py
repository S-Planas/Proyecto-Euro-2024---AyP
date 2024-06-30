class Restaurant_Sale:
    def __init__(self, client_id, client_age, shopping_cart, discount, subtotal, total):
        self.client_id = client_id
        self.client_age = client_age
        self.shopping_cart = shopping_cart
        self.discount = discount
        self.subtotal = subtotal
        self.total = total

    def show_attr(self):
        str_shooping_cart = ""

        for i_product in self.shopping_cart:
            str_shooping_cart += i_product.show_product_restaurant()

        return f"ID del cliente: {self.client_id}\nEdad del cliente: {self.client_age}\nCarrito de compras: {str_shooping_cart}\nDescuento: {self.discount}\nSubtotal: {self.subtotal}\nTotal: {self.total}"
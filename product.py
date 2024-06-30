class Product:
    def __init__(self, name, quantity, price, stock, adicional):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.stock = stock
        self.adicional = adicional

    def show_product_restaurant(self):
        return f"Nombre: {self.name}\nCantidad: {self.quantity}\nPrecio (IVA incluido|16%): ${round(self.price, 2)}\nAlmacen: {self.stock}\nAdicional: {self.adicional}"

    def show_product_client(self):
        return f"Nombre: {self.name}\nPrecio (IVA incluido|16%): ${self.price}\nAlmacen: {self.stock}\nAdicional: {self.adicional}"
    
    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "stock": self.stock,
            "adicional": self.adicional
            }
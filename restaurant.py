class Restaurant:
    def __init__(self, name):
        self.name = name
        self.products = []

    def show_restaurant(self):
        str_products = ""

        for i_product in self.products:
            str_products += i_product.show_product()

        return f"Nombre: {self.name}\nProductos: {str_products}"
    
    def to_dict(self):
        list_products = []

        for i_product in self.products:
            list_products.append(i_product.to_dict())

        return {
            "name": self.name,
            "products": list_products,
            }
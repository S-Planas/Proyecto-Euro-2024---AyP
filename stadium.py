class Stadium:
    def __init__(self, id, name, city, capacity, restaurants, seats):
        self.id = id
        self.name = name
        self.city = city
        self.capacity = capacity
        self.restaurants = restaurants
        self.seats = seats

    def show_stadium(self):

        str_restaurants = ""

        for i_restaurant in self.restaurants:
            str_restaurants += i_restaurant.show_restaurant()

        return f"ID: {self.id}\nNombre: {self.name}\Ciudad: {self.city}\nCapacidad: {self.capacity}\nRestaurantes: {str_restaurants}"
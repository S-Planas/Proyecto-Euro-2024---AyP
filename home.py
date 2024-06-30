# Importamos las librerías y las clases.
import json
import uuid
import requests
import itertools as it
import operator
from match import Match
from team import Team
from stadium import Stadium
from ticket_sale import Ticket_Sale
from restaurant import Restaurant
from restaurant_sale import Restaurant_Sale
from product import Product

# Métodos para número vampiro.
def getFangs(num_str):

    num_iter = it.permutations(num_str, len(num_str))

    for num_tuple in num_iter:

        x, y = num_tuple[:int(len(num_tuple)/2)
                        ], num_tuple[int(len(num_tuple)/2):]

        x_str, y_str = ''.join(x), ''.join(y)

        if x_str[-1] == '0' and y_str[-1] == '0':
            continue

        if int(x_str) * int(y_str) == int(num_str):
            return x_str, y_str

    return None

def isVampire(m_int):

    n_str = str(m_int)

    if len(n_str) % 2 == 1:
        return False
    fangs = getFangs(n_str)
    if not fangs:
        return False
    return True

# Métodos para número perfecto.
def perfectNumber(i_num):
    sum = 0

    for i in range(1, i_num):
        if(i_num % i == 0):
            sum = sum + i
    if (sum == i_num):
        return True
    else:
        return False

# Creamos la clase principal del programa.
class Home:

    def __init__(self):
        self.teams = []
        self.stadiums = []
        self.matches = []
        self.ticket_sales = []
        self.restaurant_sales = []

    # Métodos 'get' para las 'API' y la base de datos local.
    def get_teams(self, teams):

        # Iteramos los equipos del 'json', creamos los objetos 'team' y los guardamos en la base de datos.
        for i_team in teams:
            team = Team(i_team["id"], i_team["code"], i_team["name"], i_team["group"])
            self.teams.append(team)

    def get_stadiums(self, stadiums):

        # Iteramos los estadios del 'json' y creamos los objetos 'restaurant' y 'product'.
        for i_stadium in stadiums:
            restaurants = []
            for i_restaurant in i_stadium["restaurants"]:
                restaurant = Restaurant(i_restaurant["name"])
                restaurants.append(restaurant)
                for i_product in i_restaurant["products"]:
                    total_price = float(i_product["price"]) + (float(i_product["price"]) * 16 / 100)
                    product = Product(i_product["name"], i_product["quantity"], total_price, i_product["stock"], i_product["adicional"])
                    restaurant.products.append(product)

            # Probamos si ya se solicitaron las 'API' previamente.
            try:
                seats = []
                vip_seats = []
                general_seats = []

                for i_seat in i_stadium["seats"][0]:
                    vip_seats.append(i_seat)
                
                for i_seat in i_stadium["seats"][1]:
                    general_seats.append(i_seat)

                seats.append(vip_seats)
                seats.append(general_seats)

                stadium = Stadium(i_stadium["id"], i_stadium["name"], i_stadium["city"], i_stadium["capacity"], restaurants, seats)

            # En caso de que sea la primera vez que llamamos a las 'API'.
            except:
                stadium = Stadium(i_stadium["id"], i_stadium["name"], i_stadium["city"], i_stadium["capacity"], restaurants, [])

                vip_seats = []
                for num in range(1, stadium.capacity[0] + 1):
                    vip_seat = {"number": num,
                                "available": True}
                    vip_seats.append(vip_seat)

                stadium.seats.append(vip_seats)

                general_seats = []
                for num in range(1, stadium.capacity[1] + 1):
                    general_seat = {"number": num,
                                    "available": True}
                    general_seats.append(general_seat)
                
                stadium.seats.append(general_seats)

            self.stadiums.append(stadium)
            self.save_changes()

    def get_matches(self, matches):

        # Iteramos los partidos del 'json' y creamos los objetos 'match'.
        for i_match in matches:
            # Guardamos los equipos locales y visitantes como objetos 'team' dentro de 'match'.
            for i_team in self.teams:
                if i_team.id == i_match["home"]["id"]:
                    home = i_team
                elif i_team.id == i_match["away"]["id"]:
                    away = i_team

            # Creamos los objetos 'match' y los guardamos en la base de datos.
            match = Match(i_match["id"], i_match["number"], home, away, i_match["date"], i_match["group"], i_match["stadium_id"])
            self.matches.append(match)

    def get_ticket_sales(self, ticket_sales):

        # Iteramos los ventas de tickets del 'json' y creamos los objetos 'team', 'match' y 'ticket_sale'.
        for i_ticket_sale in ticket_sales:

            home = Team(i_ticket_sale["match"]["home"]["id"], i_ticket_sale["match"]["home"]["code"], i_ticket_sale["match"]["home"]["name"], i_ticket_sale["match"]["home"]["group"])
            away = Team(i_ticket_sale["match"]["away"]["id"], i_ticket_sale["match"]["away"]["code"], i_ticket_sale["match"]["away"]["name"], i_ticket_sale["match"]["away"]["group"])
            match = Match(i_ticket_sale["match"]["id"], i_ticket_sale["match"]["number"], home, away, i_ticket_sale["match"]["date"], i_ticket_sale["match"]["group"], i_ticket_sale["match"]["stadium_id"])
            
            ticket_sale = Ticket_Sale(i_ticket_sale["ticket_id"], i_ticket_sale["client_name"], i_ticket_sale["client_id"], i_ticket_sale["client_age"], match, i_ticket_sale["ticket"])

            try:
                ticket_sale.redeemed = i_ticket_sale["redeemed"]
            except:
                pass

            self.ticket_sales.append(ticket_sale)

    def get_restaurant_sales(self, restaurant_sales):

        # Iteramos los ventas de tickets del 'json' y creamos los objetos 'ticket_sale'.
        for i_restaurant_sale in restaurant_sales:
            shopping_cart = []

            for i_product in i_restaurant_sale["shopping_cart"]:
                product = Product(i_product["name"], i_product["quantity"], i_product["price"], i_product["stock"], i_product["adicional"])
                shopping_cart.append(product)

            restaurant_sale = Restaurant_Sale(i_restaurant_sale["client_id"], i_restaurant_sale["client_age"], shopping_cart, i_restaurant_sale["discount"], i_restaurant_sale["subtotal"], i_restaurant_sale["total"])
            self.restaurant_sales.append(restaurant_sale)

    # Módulo de gestión de partidos y estadios.
    def search_match(self):
    
        filter = input("""
ELIJA UN FILTRO DE BÚSQUEDA:
            
1. País.
2. Estadio específico.
3. Fecha determinada.

[PRESIONE '0' PARA SALIR]

>> """)
        
        # Validamos el input del filtro.
        while not filter.isnumeric() or int(filter) not in range(0,4):
            filter = input("""
ERROR! ELIJA UN FILTRO DE BÚSQUEDA:

1. País.
2. Estadio específico.
3. Fecha determinada.

[PRESIONE '0' PARA SALIR]

>> """)
        
        if filter == "1":
            aux = True

            while aux:

                exact_match = 0
                total_matches = 0
                matches = []

                search = input("\n============================\n\nIngrese el nombre de un país...\n\n[PRESIONE '0' PARA SALIR]\n\n>> ")

                if len(search) == 0:
                    print("\nNO EXISTE REGISTRO DE ESTE PAÍS!")

                elif search == "0":
                    aux = False

                else:
                    for match in self.matches:
                        if match.home.country.lower() == search.lower() or match.away.country.lower() == search.lower():
                            print(F"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")
                            print(f"\n== PARTIDO #{exact_match + 1} ==\n\n{match.show_match(self.stadiums)}")
                            exact_match += 1
                        else:
                            x = slice(0, len(search))
                            if search.lower() == match.home.country[x].lower() or search.lower() == match.away.country[x].lower():
                                matches.append(match)
                                total_matches += 1
                    
                    if total_matches > 0:
                        print(f"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")

                        for idx, match in enumerate(matches):
                            print(f"\n== PARTIDO #{idx + 1} ==\n\n{match.show_match(self.stadiums)}")

                    if exact_match == 0 and total_matches == 0: 
                        print("\nNO SE ENCONTRÓ RESULTADOS!")

        elif filter == "2":
            aux = True
            
            while aux:

                exact_match = 0
                total_matches = 0
                matches = []

                search = input("\n=======================\n\nIngrese el nombre de un estadio específico...\n\n[PRESIONE '0' PARA SALIR]\n\n>> ")

                if len(search) == 0:
                    print("\nNO EXISTE REGISTRO DE ESTE ESTADIO!")

                elif search == "0":
                    aux = False

                else:
                    for match in self.matches:
                        for stadium in self.stadiums:
                            if stadium.name.lower() == search.lower():
                                if match.stadium_id == stadium.id:
                                    print(F"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")
                                    print(f"\n== PARTIDO #{exact_match + 1} ==\n\n{match.show_match(self.stadiums)}")
                                    exact_match += 1
                            else:
                                x = slice(0, len(search))
                                if search.lower() == stadium.name[x].lower():
                                    if match.stadium_id == stadium.id:
                                        matches.append(match)
                                        total_matches += 1
                        
                    if total_matches > 0:
                        print(F"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")

                        for idx, match in enumerate(matches):
                            print(f"\n== PARTIDO #{idx + 1} ==\n\n{match.show_match(self.stadiums)}")

                    if exact_match == 0 and total_matches == 0: 
                        print("\nNO SE ENCONTRÓ RESULTADOS!")

        elif filter == "3":
            aux = True
            
            while aux:

                exact_match = 0
                total_matches = 0
                matches = []

                search = input("\n=======================\n\nIngrese una fecha determinada 'yyyy-dd-mm'...\n\n[PRESIONE '0' PARA SALIR]\n\n>> ")

                if len(search) == 0:
                    print("\nNO EXISTE REGISTRO DE ESTA FECHA!")

                elif search == "0":
                    aux = False

                else:
                    for match in self.matches:
                        if match.date == search:
                            print(F"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")
                            print(f"\n== PARTIDO #{exact_match + 1} ==\n\n{match.show_match(self.stadiums)}")
                            exact_match += 1
                        else:
                            x = slice(0, len(search))
                            if search.lower() == match.date[x]:
                                matches.append(match)
                                total_matches += 1
                    
                    if total_matches > 0:
                        print(f"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")

                        for idx, match in enumerate(matches):
                            print(f"\n== PARTIDO #{idx + 1} ==\n\n{match.show_match(self.stadiums)}")

                    if exact_match == 0 and total_matches == 0: 
                        print("\nNO SE ENCONTRÓ RESULTADOS!")

        elif filter == "0":
            return "FINALIZADO"

        self.save_changes()

    # Módulo de gestión de venta de entradas.
    def register_ticket_sale(self):
        print("\nINGRESE LOS DATOS DEL CLIENTE...\n")

        # Solicitamos la información del cliente y la validamos.
        firstname = input("Nombre: ").lower().capitalize()

        while not firstname.isalpha() or " " in firstname:
            firstname = input("Error! Ingrese un nombre válido: ").lower().capitalize()

        lastname = input("Apellido: ").lower().capitalize()

        while not lastname.isalpha() or " " in lastname:
            lastname = input("Error! Ingrese un apellido válido: ").lower().capitalize()

        client_name = f"{firstname} {lastname}"

        client_id = input("Cédula: ")

        while not client_id.isnumeric():
            client_id = input("Error! Ingrese un cédula válida: ")

        client_age = input("Edad: ")

        while not client_age.isnumeric() or int(client_age) < 0 or int(client_age) > 120:
            client_age = input("Error! Ingrese una edad válida: ")
        
        # Listamos todos los partidos.
        for match_i in self.matches:
            print(f"\n== PARTIDO NÚMERO #{match_i.number} ==\n\n{match_i.show_match(self.stadiums)}")

        # Buscamos el partido al que se desea asistir y lo guardamos como un objeto 'match'.
        found = False

        while found == False:
            match_ticket = input("\nIngrese el número del partido al que desea comprar ticket: ")

            while not match_ticket.isnumeric():
                match_ticket = input("\nError! Ingrese un número de partido válido: ")

            for match_i in self.matches:
                if match_i.number == int(match_ticket):
                    match = match_i
                    found = True
                    break

            if found == False:
                print(f"\nPARTIDO NÚMERO #{match_ticket} NO ENCONTRADO!")

        type = input("""Tipo de entrada:
                     
1. VIP.
2. General.
                     
>> """)
        
        while not type.isnumeric() or int(type) not in range(1,3) or len(type) > 1:
            type = input("""Error! Seleccione un tipo de entrada válido:
                     
1. VIP.
2. General.
                     
>> """)

        # Le asignamos sus valores a las variables del diccionario 'ticket' en base a la validación.
        if type == "1":
            ticket_type = "VIP"
            price = 75
        
        elif type == "2":
            ticket_type = "General"
            price = 35
        
        # Ahora imprimimos un mapa de los asientos 'VIP' o 'Generales'.
        print(f"""
== ASIENTO {ticket_type.upper()} ==

Los asientos marcados con una 'X' no se encuentran disponibles!
""")

        # Iteramos los estadios para buscar el que corresponde al partido seleccionado por el cliente.
        for i_stadium in self.stadiums:
            if i_stadium.id == match.stadium_id:
                stadium = i_stadium
                seats = ""
                cont_v = 0
                # Iteramos los asientos para el estadio encontrado.
                for i_seat in i_stadium.seats[int(type) - 1]:
                    cont_v += 1
                    if i_seat["available"]:
                        seats += f"[{i_seat['number']}]"
                    else:
                        seats += f"[X]"
                    if cont_v >= 10:
                        cont_v = 0
                        seats += "\n"
                print(seats)
        
        # Recibimos el número del asiento que el cliente desea selccionar.
        seat = input("""
Ingrese el asiento que desea...
                     
[PRESIONE "0" PARA SALIR]

>> """)

        # Creamos una variable para determinar si el asiento ha sido asignado exitosamente.
        seat_assigned = False

        # Validamos el número de asiento selccionado.
        while not seat.isnumeric() or int(seat) not in range(0, stadium.capacity[int(type) - 1] + 1):
            seat = input("""
===========================================

Ups! Ingrese un número de asiento válido...

[PRESIONE "0" PARA SALIR]

>> """)

        # Creamos un 'while loop' el cual se repetira mientras no se desee
        # 'salir' y no se haya encontrado un asiento disponible.
        while int(seat) != 0 and seat_assigned == False:
            for i_seat in stadium.seats[int(type) - 1]:
                if int(seat) == i_seat["number"]:
                    if i_seat["available"]:
                        seleceted_seat = i_seat
                        seat_assigned = True
                        print("""
Asiento seleccionado exitosamente!
                              
==================================""")
                        break
                    else:
                        seat = input("""
===========================================

Ups! Ingrese un número de asiento válido...

[PRESIONE "0" PARA SALIR]

>> """)
                        break
        
        # Si no se decidio salir y un asiento fue asignado con exito,
        # procedemos a crear el ticket.
        if int(seat) != 0 and seat_assigned:
            ticket = {"type": ticket_type,
                      "price": price,
                      "seat": seat}

            # Determinamos si la cédula es un número vampiro y calculamos el 50% de descuento.
            if isVampire(client_id):
                discount = 50
                subtotal = ticket["price"]
                discount_subtotal = ticket["price"] * discount / 100
                iva = 16 * discount_subtotal / 100
                total = discount_subtotal + iva
                print(f"\nUSTED HA RECIBIDO UN 50% DE DESCUENTO DEBIO A QUE SU NÚMERO DE CÉDULA ES VAMPIRO!\n\nCOSTO FINAL DE LA ENTRADA: ${round(total, 2)}\n\n")
            else:
                discount = 0
                subtotal = ticket["price"]
                iva = 16 * subtotal / 100
                total = subtotal + iva

            # Le generamos un 'ID' unico al boleto.
            ticket_id = uuid.uuid4()

            # Validamos que el 'ID' sea unico.
            for sale in self.ticket_sales:
                while sale.ticket_id == id:
                    ticket_id = uuid.uuid4()

            # Confirmamos si se desea llevar a cabo el pago.
            confirm_payment = input(f"\nINFO DE ENTRADA:\n\nCódigo: #{ticket_id}\nAsiento: #{ticket['seat']}\n\nCosto:\n- Subtotal: ${round(subtotal, 2)}\n- Descuento: {discount}%\n- IVA (16%): {round(iva, 2)}\n- Total: ${round(total, 2)}\n\n==================================\n\nDesea proceder con el pago?\n\n1. Si.\n2. No.\n\n>> ")
            
            # Validamos la opción del cliente.
            while not confirm_payment.isnumeric() or int(confirm_payment) not in range(1,3) or len(confirm_payment) > 1:
                confirm_payment = input(f"\nERROR! INFO DE ENTRADA:\n\nCódigo: #{ticket_id}\nAsiento: #{ticket['seat']}\n\nCosto:\n- Subtotal: ${round(subtotal, 2)}\n- Descuento: {discount}%\n- IVA (16%): {round(iva, 2)}\n- Total: ${round(total, 2)}\n\nDesea proceder con el pago?\n\n1. Si.\n2. No.\n\n>> ")

            # Determinamos si creamos un objeto 'sale' y lo guardamos en la BDD en base a la validación.
            if confirm_payment == "1":
                seleceted_seat["available"] = False
                sale = Ticket_Sale(str(ticket_id), client_name, client_id, client_age, match, ticket)
                self.ticket_sales.append(sale)
                print("\nPAGO EXITOSO!")
                self.save_changes()
            else:
                print("\nPAGO CANCELADO!")
   
    # Módulo de gestión de asistencia a partidos.
    def match_assistance(self):

        # Recibimos el código del boleto.
        ticket = input("\n== VALIDACIÓN DE BOLETOS ==\n\nIngrese el código del boleto: ")

        # Creamos una variable para determinar el estado de la búsqueda.
        found = False

        # Buscamos el boleto dentro de la lista de ventas y determinamos su autenticidad.
        for sale_i in self.ticket_sales:
            # En caso de que el código coincida y no se haya canjeado el boleto.
            if sale_i.ticket_id == ticket and sale_i.redeemed == False:
                sale_i.redeemed = True
                found = True
                print("\nBOLETO AUTÉNTICO! CANJEADO CON EXITO...")
                self.save_changes()
                break
            # En caso de que el código coincida y se haya canjeado el boleto.
            elif sale_i.ticket_id == ticket and sale_i.redeemed:
                found = True
                verification = input("""
BOLETO YA CANJEADO!

Para modificar la asistencia del partido verifique su identidada ingresando su número de cédula: """)
                
                # Validamos que la cédula sea un número.
                while not verification.isnumeric():
                    verification = input("\nError! Ingrese un número de cédula válido: ")

                # En caso de que la cédula coincida.
                if sale_i.client_id == verification:
                    sale_i.redeemed = False
                    print("\nVerificación exitosa, se cambió su asistencia exitosamente!\nIntente canjear su boleto nuevamente.")
                    self.save_changes()
                # En caso de que la cédula no coincida.
                else:
                    print("\nVerificación fallida!")
                break
        # En caso de que no se encuentre ningún boleto con el código ingresado.
        if found == False:
            print("\nBOLETO FALSO...")

    # Módulo de gestión de restaurantes.
    def search_product(self):
        
        # Recibimos la opción del filtro que se desea utilizar para la búsqueda.
        filter = input("""
ELIJA UN FILTRO DE BÚSQUEDA:
            
1. Nombre.
2. Tipo.
3. Rango de precio.

[PRESIONE '0' PARA SALIR]

>> """)
        
        # Validamos la opción del filtro.
        while not filter.isnumeric() or int(filter) not in range(0,4):
            filter = input("""
ERROR! ELIJA UN FILTRO DE BÚSQUEDA:

1. Nombre.
2. Tipo.
3. Rango de precio.

[PRESIONE '0' PARA SALIR]

>> """)   

        if filter == "1":
            aux = True

            while aux:

                exact_product = 0
                total_products = 0
                products = []

                # Recibimos el nombre completo o una parte de este del produto que se desea buscar.
                search = input("\n================================\n\nIngrese el nombre de un producto...\n\n[PRESIONE '0' PARA SALIR]\n\n>> ")

                # Validamos que la entrada no este vacía.
                if len(search) == 0:
                    print("\nNO EXISTE REGISTRO DE ESTE PRODUCTO!")
                
                # Validamos que no se desee cancelar la búsqueda.
                elif search == "0":
                    aux = False

                # En caso de que se reciba un input válido.
                else:
                    for i_stadium in self.stadiums:
                        for i_restaurant in i_stadium.restaurants:
                            for i_product in i_restaurant.products:
                                # En caso de que la entrada para la busqueda coincida por completo con algún producto.
                                if i_product.name.lower() == search.lower():
                                    print(F"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")
                                    print(f"\n== PRODUCTO #{exact_product + 1} ==\n\nEstadio: {i_stadium.name}\nRestaurante: {i_restaurant.name}\n\n{i_product.show_product()}")
                                    exact_product += 1
                                # En caso de que la entrada para la busqueda coincida parcialmente con algún producto.
                                else:
                                    x = slice(0, len(search))
                                    if search.lower() == i_product.name[x].lower():
                                        products.append({"stadium": i_stadium, "restaurant": i_restaurant, "product": i_product})
                                        total_products += 1
                    
                    # En caso de que haya más de un resultado de búsqueda.
                    if total_products > 0:
                        print(f"\nRESULTADOS DE BÚSQUEDA PARA '{search}'...")

                        for idx, dict in enumerate(products):
                            print(f"\n== PRODUCTO #{idx + 1} ==\n\nEstadio: {dict['stadium'].name}\nRestaurante: {dict['restaurant'].name}\n\n{dict['product'].show_product()}")

                    # En caso de que no haya ningún resultado de búsqueda.
                    if exact_product == 0 and total_products == 0: 
                        print("\nNO SE ENCONTRÓ RESULTADOS!")

        elif filter == "2":
            aux = True
            
            while aux:
                
                total_products = 0

                # Determinamos si el producto es alimento o bebida.
                product_type = input("\n===============================\n\nSELECCIONE UN TIPO DE PRODUCTO:\n\n1. Alimento.\n2. Bebida.\n\n[PRESIONE '0' PARA SALIR]\n\n>> ")

                # Validamos la entrada.
                while not product_type.isnumeric() or int(product_type) not in range(0,3):
                    product_type = input("\n===============================\n\nERROR! SELECCIONE UN TIPO DE PRODUCTO:\n\n1. Alimento.\n2. Bebida.\n\n[PRESIONE '0' PARA SALIR]\n\n>> ")
                
                # En caso de que el producto sea un alimento.
                if product_type == "1":

                    # Determinamos el tipo de alimento.
                    food_type = input("\n===============================\n\nSELECCIONE UN TIPO DE ALIMENTO:\n\n1. Plato.\n2. Paquete.\n\n>> ")

                    # Validamos la entrada.
                    while not food_type.isnumeric() or int(food_type) not in range(1,3):
                        food_type = input("\n===============================\n\nERROR! SELECCIONE UN TIPO DE ALIMENTO:\n\n1. Plato.\n2. Paquete.\n\n>> ")

                    # En caso de que el producto sea un alimento en plato.
                    if food_type == "1":
                        for i_stadium in self.stadiums:
                            for i_restaurant in i_stadium.restaurants:
                                for i_product in i_restaurant.products:
                                    if i_product.adicional == "plate":
                                        print(F"\nRESULTADOS DE BÚSQUEDA...")
                                        print(f"\n== PRODUCTO #{total_products + 1} ==\n\nEstadio: {i_stadium.name}\nRestaurante: {i_restaurant.name}\n\n{i_product.show_product()}")
                                        total_products += 1

                        if total_products == 0: 
                            print("\nNO SE ENCONTRÓ RESULTADOS!")

                    # En caso de que el producto sea un alimento empaquetado.
                    if food_type == "2":
                        for i_stadium in self.stadiums:
                            for i_restaurant in i_stadium.restaurants:
                                for i_product in i_restaurant.products:
                                    if i_product.adicional == "package":
                                        print(F"\nRESULTADOS DE BÚSQUEDA...")
                                        print(f"\n== PRODUCTO #{total_products + 1} ==\n\nEstadio: {i_stadium.name}\nRestaurante: {i_restaurant.name}\n\n{i_product.show_product()}")
                                        total_products += 1

                # En caso de que el producto sea una bebida.
                if product_type == "2":
                    drink_type = input("\n===============================\n\nSELECCIONE UN TIPO DE BEBIDA:\n\n1. Alcoholica.\n2. No alcoholica.\n\n>> ")
                    
                    # Validamos la entrada.
                    while not drink_type.isnumeric() or int(drink_type) not in range(1,3):
                        drink_type = input("\n===============================\n\nERROR! SELECCIONE UN TIPO DE BEBIDA:\n\n1. Alcoholica.\n2. No alcoholica.\n\n>> ")

                    # En caso de que la bebida sea alcoholica.
                    if drink_type == "1":
                        for i_stadium in self.stadiums:
                            for i_restaurant in i_stadium.restaurants:
                                for i_product in i_restaurant.products:
                                    if i_product.adicional == "alcoholic":
                                        print(F"\nRESULTADOS DE BÚSQUEDA...")
                                        print(f"\n== PRODUCTO #{total_products + 1} ==\n\nEstadio: {i_stadium.name}\nRestaurante: {i_restaurant.name}\n\n{i_product.show_product()}")
                                        total_products += 1

                        if total_products == 0: 
                            print("\nNO SE ENCONTRÓ RESULTADOS!")

                    # En caso de que la bebida sea no alcoholica.
                    if drink_type == "2":
                        for i_stadium in self.stadiums:
                            for i_restaurant in i_stadium.restaurants:
                                for i_product in i_restaurant.products:
                                    if i_product.adicional == "non-alcoholic":
                                        print(F"\nRESULTADOS DE BÚSQUEDA...")
                                        print(f"\n== PRODUCTO #{total_products + 1} ==\n\nEstadio: {i_stadium.name}\nRestaurante: {i_restaurant.name}\n\n{i_product.show_product()}")
                                        total_products += 1

                # En caso de que no se consigan resultado de ningún producto.
                if total_products == 0: 
                    print("\nNO SE ENCONTRÓ RESULTADOS!")

                # En caso de que se desee cancelar la búsqueda.
                if product_type == "0":
                    aux = False

        elif filter == "3":

            total_products = 0
            products = []

            print("\n===========================\n\nINGRESE UN RANGO DE PRECIO:\n")

            # Recibimos el rango menor.
            lower_range = input("Rango menor: ")
            
            # Validamos el rango menor.
            while not lower_range.isnumeric():
                lower_range = input("Error! Rango menor: ")

            # Recibimos el rango mayor.
            higher_range = input("Rango mayor: ")

            # Validamos el rango mayor.
            while not higher_range.isnumeric():
                higher_range = input("Error! Rango mayor: ")
            
            # Efectuamos la búsqueda con el rango establecido.
            for i_stadium in self.stadiums:
                for i_restaurant in i_stadium.restaurants:
                    for i_product in i_restaurant.products:
                        if float(i_product.price) >= float(lower_range) and float(i_product.price) <= float(higher_range):
                            print(F"\nRESULTADOS DE BÚSQUEDA...")
                            print(f"\n== PRODUCTO #{total_products + 1} ==\n\nEstadio: {i_stadium.name}\nRestaurante: {i_restaurant.name}\n\n{i_product.show_product()}")
                            total_products += 1

            # En caso de que no hayan resultados para la búsqueda.
            if total_products == 0: 
                print("\nNO SE ENCONTRÓ RESULTADOS!")

        # En caso de que se desee volver al menú.
        elif filter == "0":
            return "FINALIZADO"

    def register_restaurant_sale(self):

        # Recibimos la cédula del cliente.
        client_id = input("\nIngrese la cédula del cliente: ")
        client_age = 0

        # Validamos la cédula del cliente.
        while not client_id.isnumeric():
            client_id = input("\nError! Ingrese la cédula del cliente: ")

        # Declaramos una variable para determinar el estado de búsqueda.
        found = False

        # Buscamos la compra del cliente en la base de datos.
        for i_ticket_sale in self.ticket_sales:
            if int(i_ticket_sale.client_id) == int(client_id) and i_ticket_sale.ticket["type"] == "VIP":
                client_age = i_ticket_sale.client_age
                available_products = []
                shopping_cart = []
                found = True

                print("\nEL CLIENTE COMPRÓ UN BOLETO 'VIP'!...\n\n== SELECCIONE LOS PRODUCTOS QUE DESEA COMPRAR ==")

                # Creamos una lista auxiliar en donde guardaremos todo los productos disponibles
                # para el estadio correspondiente a la entrada del cliente.
                for i_stadium in self.stadiums:
                    if i_stadium.id == i_ticket_sale.match.stadium_id:
                        for i_restaurant in i_stadium.restaurants:
                            for i_product in i_restaurant.products:
                                available_products.append(i_product)

                # Declaramos una variable para determinar si ya no se desean agregar más productos.
                finished = False
                
                # Creamos un loop para comprar entre los productos disponibles.
                while finished == False:
                    for idx, i_product in enumerate(available_products):
                        print(f"\nPRODUCTO #{idx + 1}:\n\n{i_product.show_product_restaurant()}")

                    # Recibimos el número del producto a comprar.
                    purchase = input(f"""\nAgrege un producto a su carro de compras {len(shopping_cart)}:
                                    
[PRESIONE "0" PARA FINALIZAR]

>> """)             # Validamos el número del producto que se desea comprar.
                    while not purchase.isnumeric() or int(purchase) not in range(0, len(available_products) + 1):
                        purchase = input(f"""Error! Agrege un producto a su carro de compras {len(shopping_cart)}:
                                    
[PRESIONE "0" PARA FINALIZAR]

>> """)         
                    
                    # Validamos si se desea finalizar la compra.
                    if purchase == "0":
                        finished = True
                        subtotal = 0
                        total_cost = 0
                        discount = 0
                        print("\n== RESUMEN DE COMPRA ==\n")
                        for i_product in shopping_cart:
                            print(f"PRODUCTOS:\n\n{i_product.show_product_client()}")
                            subtotal += i_product.price

                        # Determinamos si hay un descuento disponible en caso
                        # de que la cédula del cliente sea un número perfecto.
                        if perfectNumber(int(client_id)):
                            discount = subtotal * 15 / 100
                            total_cost = subtotal - discount
                            print(f"\nDESCUENTO: 15%\nMONTO TOTAL: ${round(total_cost, 2)}")
                        else:
                            total_cost = subtotal
                            print(f"\nDESCUENTO: 0%\nMONTO TOTAL: ${round(total_cost, 2)}")

                        # Confirmamos el pago.
                        confirm_payment = input("""
DESEA PROCEDER CON LA COMPRA?
                                                
1. Si.
2. No.
                                                
>> """)                 
                        # Validamos la confirmación del pago.
                        while not confirm_payment.isnumeric or int(confirm_payment) not in range(1,3):
                            confirm_payment = input("""
ERROR! DESEA PROCEDER CON LA COMPRA?
                                                
1. Si.
2. No.
                                                
>> """)
                        # Determinamos la salida en base a la opción elejida por el cliente.
                        if confirm_payment == "1":
                            self.restaurant_sales.append(Restaurant_Sale(client_id, client_age, shopping_cart, discount, subtotal, total_cost))
                            print(f"PAGO EXITOSO!\nSUBTOTAL: ${round(subtotal, 2)}\nDESCUENTO: {discount}%\nTOTAL: ${round(total_cost, 2)}")
                            self.save_changes()
                        elif confirm_payment == "2":
                            print("PAGO CANCELADO!")

                    # En caso de que no se desee finalizar la compra seguimos mostrando
                    # los productos disponibles para que el cliente siga comprando.
                    else:
                        for idx, i_product in enumerate(available_products):
                            if idx + 1 == int(purchase):
                                if i_product.adicional == "alcoholic" and int(client_age) < 18:
                                    print("\nUPS! LO SENTIMOS, PERO ERES MENOR DE EDAD...")
                                else:
                                    if i_product.quantity - 1 >= 0:
                                        i_product.quantity -= 1
                                        shopping_cart.append(i_product)
                                    else:
                                        print("UPS! LO SENTIMOS, YA NO QUEDA MÁS DE ESTE PRODUCTO...")
                break
            # En caso de que la búsqueda haya coincidio con un resultado pero la entrada es de tipo 'General'.
            elif int(i_ticket_sale.client_id) == int(client_id) and i_ticket_sale.ticket["type"] == "General":
                found = True
                print("\nEL CLIENTE COMPRÓ UN BOLETO 'GENERAL'!...")
                break
        
        # En caso de que la búsqueda no haya coincidio con ningún resultado.
        if found == False:
            print("\nEL CLIENTE NO COMPRÓ UN BOLETO...")

    # Módulo de estadística.
    def vip_spending_average(self):
        vip_spending = {}
        sum_spending = 0

        for i_restaurant_sale in self.restaurant_sales:
            if str(i_restaurant_sale.client_id) in vip_spending:
                vip_spending[str(i_restaurant_sale.client_id)] += i_restaurant_sale.total
            else:
                vip_spending[str(i_restaurant_sale.client_id)] = i_restaurant_sale.total

        for i_ticket_sale in self.ticket_sales:
            if i_ticket_sale.ticket["type"] == "VIP":
                if str(i_ticket_sale.client_id) in vip_spending:
                    vip_spending[str(i_ticket_sale.client_id)] += i_ticket_sale.ticket["price"]
                else:
                    vip_spending[str(i_ticket_sale.client_id)] = i_ticket_sale.ticket["price"]
        
        for client in vip_spending:
            sum_spending += vip_spending[client]

        if sum_spending > 0:
            result = sum_spending/len(vip_spending)

            print(f"\nPromedio de gasto de un cliente VIP en un partido: ${round(result, 2)}")

        else:
            print("\nNO HAY CLIENTES VIP!")

    def attendance_table(self):
        match_attendance = {}
        match_ticket_sales = {}
        matches = []

        for i_ticket_sale in self.ticket_sales:
            if i_ticket_sale.redeemed == True:
                match_id = str(i_ticket_sale.match.id)
                if match_id in match_attendance:
                    match_attendance[match_id] += 1
                else:
                    match_attendance[match_id] = 1

        sorted_match_attendance = sorted(match_attendance.items(), key=lambda item: item[1], reverse=True)

        for i_ticket_sale in self.ticket_sales:
            match_id = str(i_ticket_sale.match.id)
            if match_id in match_ticket_sales:
                match_ticket_sales[match_id] += 1
            else:
                match_ticket_sales[match_id] = 1
                matches.append(i_ticket_sale.match)
        
        if len(matches) > 0:

            print("\n== TABLA DECRECIENTE DE ASISTENCIA DE PARTIDOS ==\n")
            cont = 0

            for i_match in matches:
                for i_attended_match in sorted_match_attendance:
                    if i_attended_match[0] == str(i_match.id):
                        cont += 1
                        print(f"PARTIDO #{cont}\n\n{i_match.show_match(self.stadiums)}\nBoletos vendidos: {match_ticket_sales[i_attended_match[0]]}\nNúmero de asistencias: {i_attended_match[1]}\nRelación asistencia venta: {round((match_attendance[i_attended_match[0]]*100)/match_ticket_sales[i_attended_match[0]], 2)}%\n")
        else:
            print("\nNO HAY PARTIDOS CON ASISTENCIA!")

    def most_attended_match(self):
        
        match_attendance = {}
        matches = []

        for i_ticket_sale in self.ticket_sales:
            if i_ticket_sale.redeemed == True:
                if str(i_ticket_sale.match.id) in match_attendance:
                    match_attendance[str(i_ticket_sale.match.id)] += 1
                else:
                    match_attendance[str(i_ticket_sale.match.id)] = 1
                    matches.append(i_ticket_sale.match)

        sorted_match_attendance = sorted(match_attendance.items(), key=operator.itemgetter(1), reverse=True)

        if len(matches) > 0:
            print("\n== PARTIDO CON MAYOR ASISTENCIA ==\n")
            for i_match in matches:
                if str(i_match.id) == sorted_match_attendance[0][0]:
                    print(f"{i_match.show_match(self.stadiums)}\nNúmero de asistencias: {sorted_match_attendance[0][1]}")
        else:
            print("\nNO HAY PARTIDOS CON ASISTENCIA!")

    def most_sold_match(self):

        matches_sales = {}
        matches = []

        for i_ticket_sale in self.ticket_sales:
            if str(i_ticket_sale.match.id) in matches_sales:
                matches_sales[str(i_ticket_sale.match.id)] += 1
            else:
                matches_sales[str(i_ticket_sale.match.id)] = 1
                matches.append(i_ticket_sale.match)

        sorted_matches_sales = sorted(matches_sales.items(), key=operator.itemgetter(1), reverse=True)

        if len(matches) > 0:
            print("\n== PARTIDO CON MAYOR BOLETOS VENDIDOS ==\n")
            for i_match in matches:
                if str(i_match.id) == sorted_matches_sales[0][0]:
                    print(f"{i_match.show_match(self.stadiums)}\nBoletos vendidos: {sorted_matches_sales[0][1]}")
        else:
            print("\nNO HAY PARTIDOS CON BOLETOS VENDIDOS!")

    def top3_most_sold_products(self):
        
        products_bought = {}
        cont = 0

        for i_restaurant_sale in self.restaurant_sales:
            for i_product in i_restaurant_sale.shopping_cart:
                if i_product.name in products_bought:
                    products_bought[i_product.name] += 1
                else:
                    products_bought[i_product.name] = 1

        sorted_products_bought = sorted(products_bought.items(), key=operator.itemgetter(1), reverse=True)
        

        if cont > 0:
            print("\n== TOP 3 PRODUCTOS MÁS VENDIDOS ==\n")
            while cont < 3:
                cont += 1
                print(f"#{cont}. {sorted_products_bought[cont - 1][0]} | Unidades: {sorted_products_bought[cont - 1][1]}")
        else:
            print("\nNO HAY PRODUCTOS VENDIDOS!")

    def top3_clients(self):
        
        tickets_bought = {}
        cont = 0

        for i_ticket_sale in self.ticket_sales:
            if str(i_ticket_sale.client_id) in tickets_bought:
                tickets_bought[str(i_ticket_sale.client_id)] += 1
            else:
                tickets_bought[str(i_ticket_sale.client_id)] = 1

        sorted_tickets_bought = sorted(tickets_bought.items(), key=operator.itemgetter(1), reverse=True)
        

        if cont > 0:

            print("\n== TOP 3 CLIENTES ==\n")
            while cont < 3:
                cont += 1
                print(f"#{cont}. {sorted_tickets_bought[cont - 1][0]} | Tickets: {sorted_tickets_bought[cont - 1][1]}")
        else:
            print("\nNO HAY CLIENTES!")

    # Método para salvar cambios en los txt.
    def save_changes(self):

        saved_teams = []
        saved_stadiums = []
        saved_matches = []
        saved_ticket_sales = []
        saved_restaurant_sales = []

        # Guardamos los cambios en el 'TXT' de los equipos.
        for team in self.teams:
            save_team = {
"id": team.id,
"code": team.fifa_code,
"name": team.country,
"group": team.group
}

            saved_teams.append(save_team)

        with open("Euro2024_teams.json", "w") as file:
            json.dump(saved_teams, file, indent = 4)
            file.close()

        # Guardamos los cambios en el 'TXT' de los partidos.
        for match in self.matches:
            save_match = {
"id": match.id,
"number": match.number,
"home": match.home.to_dict(),
"away": match.away.to_dict(),
"date": match.date,
"group": match.group,
"stadium_id": match.stadium_id,
}

            saved_matches.append(save_match)

        with open("Euro2024_matches.json", "w") as file:
            json.dump(saved_matches, file, indent = 4)
            file.close()

        # Guardamos los cambios en el 'TXT' de las ventas de tickets.
        for ticket_sale in self.ticket_sales:
            save_ticket_sale = {
"ticket_id": ticket_sale.ticket_id,
"client_name": ticket_sale.client_name,
"client_id": ticket_sale.client_id,
"client_age": ticket_sale.client_age,
"match": ticket_sale.match.to_dict(),
"ticket": ticket_sale.ticket,
"redeemed": ticket_sale.redeemed,
}

            saved_ticket_sales.append(save_ticket_sale)

        with open("Euro2024_ticket_sales.json", "w") as file:
            json.dump(saved_ticket_sales, file, indent = 4)
            file.close()

        # Guardamos los cambios en el 'TXT' de las ventas de restaurantes.
        for restaurant_sale in self.restaurant_sales:
            shopping_cart = []

            for i_product in restaurant_sale.shopping_cart:
                shopping_cart.append(i_product.to_dict())

            save_restaurant_sale = {
"client_id": restaurant_sale.client_id,
"client_age": restaurant_sale.client_age,
"shopping_cart": shopping_cart,
"discount": restaurant_sale.discount,
"subtotal": restaurant_sale.subtotal,
"total": restaurant_sale.total,
}

            saved_restaurant_sales.append(save_restaurant_sale)

        with open("Euro2024_restaurant_sales.json", "w") as file:
            json.dump(saved_restaurant_sales, file, indent = 4)
            file.close()

        # Guardamos los cambios en el 'TXT' de los estadios.
        for stadium in self.stadiums:
            list_restaurants = []

            for i_restaurant in stadium.restaurants:
                list_restaurants.append(i_restaurant.to_dict())

            save_stadium = {
"id": stadium.id,
"name": stadium.name,
"city": stadium.city,
"capacity": stadium.capacity,
"restaurants": list_restaurants,
"seats": stadium.seats
}

            saved_stadiums.append(save_stadium)

        with open("Euro2024_stadiums.json", "w") as file:
            json.dump(saved_stadiums, file, indent = 4)
            file.close()

# MÉTODO PARA INICIAR EL PROGRAMA

    def start(self):
        
        # Links de las 'API'.
        url_teams = 'https://raw.githubusercontent.com/Algoritmos-y-Programacion/api-proyecto/main/teams.json'
        url_stadiums = "https://raw.githubusercontent.com/Algoritmos-y-Programacion/api-proyecto/main/stadiums.json"
        url_matches = "https://raw.githubusercontent.com/Algoritmos-y-Programacion/api-proyecto/main/matches.json"

        # Variable contador para determinar si los archivos TXT estan vacios.
        cont = 0

        while True:
            
            # Abrimos y leemos el archivo.
            with open("Euro2024_teams.json", "r") as file_1:
                if file_1.read() != '':
                    x = "1"
                else:
                    x = "2"

            # Si los archivos no están vacios, los abrimos y leemos.
            if x == "1":
                with open("Euro2024_teams.json", "r") as file:
                    teams = json.load(file)
                with open("Euro2024_matches.json", "r") as file:
                    matches = json.load(file)
                with open("Euro2024_stadiums.json", "r") as file:
                    stadiums = json.load(file)
                with open("Euro2024_ticket_sales.json", "r") as file:
                    ticket_sales = json.load(file)
                    self.get_ticket_sales(ticket_sales)
                with open("Euro2024_restaurant_sales.json", "r") as file:
                    restaurant_sales = json.load(file)
                    self.get_restaurant_sales(restaurant_sales)

                self.get_teams(teams)
                self.get_matches(matches)
                self.get_stadiums(stadiums)
                #self.get_restaurant_sales(ticket_sales)

                cont += 1
                break
            
            # Si el archivo está vacio, tenemos que solicitar las 'API'.
            if x == "2":
                url_teams = requests.get(url_teams)
                url_stadiums = requests.get(url_stadiums)
                url_matches = requests.get(url_matches)

                if url_teams.status_code == 200 and url_stadiums.status_code == 200 and url_matches.status_code == 200:
                    teams = url_teams.json() 
                    stadiums = url_stadiums.json()
                    matches = url_matches.json()
                    break
        
        # Si los archivos están vacios tenemos que escribir en ellos utilizando los 'json' obtenidos al solicitar las 'API'.
        if cont == 0:
            # Solicitamos a las 'API' y creamos los objetos.
            self.get_teams(teams)
            self.get_matches(matches)
            self.get_stadiums(stadiums)

            saved_teams = []
            saved_stadiums = []
            saved_matches = []

            for team in self.teams:
                save_team = {
"id": team.id,
"code": team.fifa_code,
"name": team.country,
"group": team.group
}
                saved_teams.append(save_team)

            with open("Euro2024_teams.json", "w") as file:
                json.dump(saved_teams, file, indent = 4)
                file.close()

            for match in self.matches:
                save_match = {
"id": match.id,
"number": match.number,
"home": match.home.to_dict(),
"away": match.away.to_dict(),
"date": match.date,
"group": match.group,
"stadium_id": match.stadium_id,
}
                saved_matches.append(save_match)

            with open("Euro2024_matches.json", "w") as file:
                json.dump(saved_matches, file, indent = 4)
                file.close()

            for stadium in self.stadiums:
                list_restaurants = []

                for i_restaurant in stadium.restaurants:
                    list_restaurants.append(i_restaurant.to_dict())

                save_stadium = {
    "id": stadium.id,
    "name": stadium.name,
    "city": stadium.city,
    "capacity": stadium.capacity,
    "restaurants": list_restaurants
    }
                saved_stadiums.append(save_stadium)

            with open("Euro2024_stadiums.json", "w") as file:
                json.dump(saved_stadiums, file, indent = 4)
                file.close()

        # Declaramos la variable del 'while loop'.
        loop = True

        # Creamos un 'while loop' para que al final de cada operación se retorne al menú de inicio.
        while loop:

            start = input("""
EUROCOPA ALEMANIA 2024
========================
1. Partidos y estadios.
2. Venta de entradas.
3. Asistencia a partidos.
4. Restaurantes.
5. Estadisticas.

[PRESIONE "0" PARA SALIR]

>> """)

            #VALIDAMOS EL INPUT DE LA VARIABLE 'START'
            while not start.isnumeric() or int(start) not in range(0,8) or len(start) != 1:
                start = input("""
UPS, ESA OPCIÓN NO ES VÁLIDA...

EUROCOPA ALEMANIA 2024
========================
1. Partidos y estadios.
2. Venta de entradas.
3. Asistencia a partidos.
4. Restaurantes.
5. Estadisticas.

[PRESIONE "0" PARA SALIR]

>> """)

            if start == "1":
                self.search_match()

            elif start == "2":
                self.register_ticket_sale()

            elif start == "3":
                self.match_assistance()

            elif start == "4":

                option = input("""
1. Buscar producto.
2. Venta de restaurantes.

[PRESIONE "0" PARA SALIR]

>> """)
                
                while not option.isnumeric() or int(option) not in range(0,3) or len(option) != 1:
                    option = input("""
ERROR! SELECCIONE UNA OPCIÓN VÁLIDA...

1. Buscar producto.
2. Venta de restaurantes.

[PRESIONE "0" PARA SALIR]

>> """)         

                if option == "1":
                    self.search_product()

                elif option == "2":
                    self.register_restaurant_sale()

            elif start == "5":
                option = input("""
== ESTADÍSTICAS ==

1. Promedio de gasto de un cliente VIP en un partido.
2. Ver tabla de asistencia a los partidos.
3. Partido con mayor asistencia.
4. Partido con mayor boletos vendidos.
5. Top 3 productos más vendidos en el restaurante.
6. Top 3 de clientes que más compraron boletos.
                               
[PRESIONE "0" PARA SALIR]
                               
>> """)
                
                while not option.isnumeric() and int(option) not in range(0, 7):
                    option = input("""
== ESTADÍSTICAS ==             

1. Promedio de gasto de un cliente VIP en un partido.
2. Ver tabla de asistencia a los partidos.
3. Partido con mayor asistencia.
4. Partido con mayor boletos vendidos.
5. Top 3 productos más vendidos en el restaurante.
6. Top 3 de clientes que más compraron boletos.
                               
[PRESIONE "0" PARA SALIR]
                               
>> """)
                
                if option == "1":
                   self.vip_spending_average()

                elif option == "2":
                    self.attendance_table()

                elif option == "3":
                    self.most_attended_match()

                elif option == "4":
                    self.most_sold_match()

                elif option == "5":
                    self.top3_most_sold_products()

                elif option == "6":
                    self.top3_clients()

            elif start == "0":
                exit()
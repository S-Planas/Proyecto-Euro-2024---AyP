class Ticket_Sale:
    def __init__(self, ticket_id, client_name, client_id, client_age, match, ticket) -> None:
        self.ticket_id = ticket_id
        self.client_name = client_name
        self.client_id = client_id
        self.client_age = client_age
        self.match = match
        self.ticket = ticket
        self.redeemed = False

    def show_sale(self, stadiums):
        return f"Código: {self.ticket_id}\nNombre: {self.client_name}\nID: {self.client_id}\nEdad: {self.client_age}\nPartido: {self.match.show_match(stadiums)}\nTicket: {self.ticket['type']}"
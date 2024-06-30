class Team:
    def __init__(self, id, fifa_code, country, group):
        self.id = id
        self.fifa_code = fifa_code
        self.country = country
        self.group = group

    def show_team(self):
        return f"ID: {self.id}\nPaís: {self.country}\nCódigo FIFA: {self.fifa_code}\nGrupo: {self.group}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.fifa_code,
            "name": self.country,
            "group": self.group
            }
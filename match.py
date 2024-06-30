class Match:
    def __init__(self, id, number, home, away, date, group, stadium_id):
        self.id = id
        self.number = number
        self.home = home
        self.away = away
        self.date = date
        self.group = group
        self.stadium_id = stadium_id

    def show_match(self, stadiums):
        for stadium_i in stadiums:
            if stadium_i.id == self.stadium_id:
                stadium = stadium_i

        return f"Equipo local: {self.home.country}\nEquipo visitante: {self.away.country}\nFecha: {self.date}\nGrupo: {self.group}\nEstadio: {stadium.name}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "home": self.home.to_dict(),
            "away": self.away.to_dict(),
            "date": self.date,
            "group": self.group,
            "stadium_id": self.stadium_id
            }
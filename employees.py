from utils.controller import get_coordinates

class Employee:
    def __init__(self, name: str, surname: str, farm_id: int, location: str, map_widget):
        self.name = name
        self.surname = surname
        self.farm_id = farm_id
        self.location = location
        self.coords = get_coordinates(location)
        self.marker = map_widget.set_marker(self.coords[0], self.coords[1],
                                            text=f"{name} {surname}")

    def update_marker(self, map_widget):
        self.marker.delete()
        self.marker = map_widget.set_marker(self.coords[0], self.coords[1],
                                            text=f"{self.name} {self.surname}")

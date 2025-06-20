class Farm:
    def __init__(self, name: str, location: str, map_widget):
        self.name = name
        self.location = location
        self.coords = get_coordinates(location)
        self.marker = map_widget.set_marker(self.coords[0], self.coords[1], text=name)

    def update_marker(self, map_widget):
        self.marker.delete()
        self.marker = map_widget.set_marker(self.coords[0], self.coords[1], text=self.name)
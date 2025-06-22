farms: list[Farm] = []

def list_farms() -> list[Farm]:
    return farms.copy()

def add_farm(name: str, location: str, map_widget):
    farm = Farm(name, location, map_widget)
    farms.append(farm)

def remove_farm(index: int):
    farm = farms.pop(index)
    farm.marker.delete()

def update_farm(index: int, name: str = None, location: str = None, map_widget=None):
    farm = farms[index]
    if name:
        farm.name = name
    if location:
        farm.location = location
        farm.coords = get_coordinates(location)
    if map_widget:
        farm.update_marker(map_widget)

from farms import farms
from employees import employees
from clients import clients

def show_map_all_farms(map_widget):
    map_widget.delete_all_marker()
    coords = [f.coords for f in farms]
    # ustalenie środka i zoomu...
    for f in farms:
        map_widget.set_marker(f.coords[0], f.coords[1], text=f.name)

def show_map_all_employees(map_widget):
    # analogicznie dla employees

def show_map_clients_for_farm(map_widget, farm_id):
    # filtracja po farm_id

def show_map_employees_for_farm(map_widget, farm_id):
    # filtracja po farm_id

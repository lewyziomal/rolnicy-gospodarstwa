# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from tkintermapview import TkinterMapView

# Listy danych dla gospodarstw, pracowników i klientów
farms = []
employees = []
clients = []
next_farm_id = 1
next_employee_id = 1
next_client_id = 1


def get_coordinates_for_city(city_name):
    """
    Pobiera współrzędne GPS (szerokość i długość geograficzną) dla podanej nazwy miasta z Wikipedii.
    Zwraca krotkę (lat, lon) lub None, jeśli nie znaleziono.
    W razie problemów z połączeniem rzuca wyjątek z komunikatem 'network_error'.
    """
    if not city_name:
        return None
    # Parametry zapytania do API Wikipedii
    params = {
        'action': 'query',
        'prop': 'coordinates',
        'titles': city_name,
        'format': 'json',
        'formatversion': '2',
        'redirects': '1'
    }
    urls = ["https://en.wikipedia.org/w/api.php", "https://pl.wikipedia.org/w/api.php"]
    network_issue = True
    for url in urls:
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
        except Exception:
            # Jeśli błąd (np. brak połączenia), spróbuj następny URL
            continue
        network_issue = False  # połączenie udane
        data = response.json()
        if data.get("query") and data["query"].get("pages"):
            pages = data["query"]["pages"]
            if pages:
                page = pages[0]
                coords = page.get("coordinates")
                if coords:
                    lat = coords[0].get("lat")
                    lon = coords[0].get("lon")
                    if lat is not None and lon is not None:
                        return (lat, lon)
    if network_issue:
        # Żadne z zapytań nie powiodło się z powodu braku połączenia
        raise Exception("network_error")
    # Brak współrzędnych dla podanej nazwy
    return None


# Funkcje dla gospodarstw rolnych
def add_farm():
    """Dodaje nowe gospodarstwo rolne na podstawie pól formularza."""
    global farms, next_farm_id
    name = entry_farm_name.get().strip()
    city = entry_farm_city.get().strip()
    if not name or not city:
        messagebox.showerror("Błąd", "Proszę podać nazwę i miasto gospodarstwa.")
        return
    # Sprawdź unikalność nazwy gospodarstwa
    for f in farms:
        if f["name"].lower() == name.lower():
            messagebox.showerror("Błąd", f"Gospodarstwo o nazwie '{name}' już istnieje.")
            return
    # Pobierz współrzędne z Wikipedii
    try:
        coords = get_coordinates_for_city(city)
    except Exception as e:
        if str(e) == "network_error":
            messagebox.showerror("Błąd", "Błąd podczas pobierania współrzędnych. Sprawdź połączenie internetowe.")
        else:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania współrzędnych: {e}")
        return
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla lokalizacji '{city}'.")
        return
    lat, lon = coords
    # Dodaj gospodarstwo do listy
    farm = {"id": next_farm_id, "name": name, "city": city, "coords": (lat, lon)}
    farms.append(farm)
    next_farm_id += 1
    # Dodaj do tabeli (Treeview)
    tree_farms.insert("", "end", iid=str(farm["id"]), values=(farm["name"], farm["city"]))
    # Wyczyść pola formularza
    entry_farm_name.delete(0, tk.END)
    entry_farm_city.delete(0, tk.END)
    # Odśwież listy gospodarstw w comboboxach innych zakładek
    refresh_farm_options()
    # Jeśli aktualnie na mapie są wyświetlane wszystkie gospodarstwa – zaktualizuj mapę
    if map_mode.get() == "Wszystkie gospodarstwa":
        update_map()


def update_farm():
    """Aktualizuje zaznaczone gospodarstwo danymi z formularza."""
    global farms
    selected = tree_farms.selection()
    if not selected:
        messagebox.showerror("Błąd", "Nie wybrano gospodarstwa do edycji.")
        return
    item_id = selected[0]  # ID (iid) wybranego elementu w Treeview
    farm = next((f for f in farms if str(f["id"]) == item_id), None)
    if not farm:
        messagebox.showerror("Błąd", "Wybrane gospodarstwo nie zostało znalezione.")
        return
    new_name = entry_farm_name.get().strip()
    new_city = entry_farm_city.get().strip()
    if not new_name or not new_city:
        messagebox.showerror("Błąd", "Proszę podać nazwę i miasto gospodarstwa.")
        return
    # Sprawdź duplikat nazwy (jeśli nazwa zmieniona)
    if new_name.lower() != farm["name"].lower():
        for f in farms:
            if f["id"] != farm["id"] and f["name"].lower() == new_name.lower():
                messagebox.showerror("Błąd", f"Gospodarstwo o nazwie '{new_name}' już istnieje.")
                return
    # Sprawdź zmianę lokalizacji – pobierz nowe współrzędne, jeśli zmieniono miasto
    if new_city.strip().lower() != farm["city"].lower():
        try:
            coords = get_coordinates_for_city(new_city)
        except Exception as e:
            if str(e) == "network_error":
                messagebox.showerror("Błąd", "Błąd podczas pobierania współrzędnych. Sprawdź połączenie internetowe.")
            else:
                messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania współrzędnych: {e}")
            return
        if coords is None:
            messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla lokalizacji '{new_city}'.")
            return
        farm["coords"] = coords
    # Zapisz zmiany w danych
    farm["name"] = new_name
    farm["city"] = new_city
    # Zaktualizuj dane w tabeli
    tree_farms.item(item_id, values=(new_name, new_city))
    # Odśwież listy gospodarstw w comboboxach (np. jeśli nazwa się zmieniła)
    refresh_farm_options()
    # Zaktualizuj nazwę gospodarstwa w listach pracowników/klientów (kolumna "Gospodarstwo")
    for emp in employees:
        if emp["farm_id"] == farm["id"]:
            if tree_employees.exists(str(emp["id"])):
                tree_employees.item(str(emp["id"]), values=(emp["name"], emp["city"], new_name))
    for cli in clients:
        if cli["farm_id"] == farm["id"]:
            if tree_clients.exists(str(cli["id"])):
                tree_clients.item(str(cli["id"]), values=(cli["name"], cli["city"], new_name))
    # Jeśli mapa pokazuje gospodarstwa lub dane tego gospodarstwa – odśwież mapę
    if map_mode.get() in ["Wszystkie gospodarstwa", "Pracownicy wybranego gospodarstwa",
                          "Klienci wybranego gospodarstwa"]:
        update_map()


def delete_farm():
    """Usuwa zaznaczone gospodarstwo i powiązanych z nim pracowników/klientów."""
    global farms, employees, clients
    selected = tree_farms.selection()
    if not selected:
        messagebox.showerror("Błąd", "Nie wybrano gospodarstwa do usunięcia.")
        return
    item_id = selected[0]
    farm = next((f for f in farms if str(f["id"]) == item_id), None)
    if not farm:
        messagebox.showerror("Błąd", "Wybrane gospodarstwo nie zostało znalezione.")
        return
    # Usuń gospodarstwo z listy danych
    farms = [f for f in farms if f["id"] != farm["id"]]
    # Usuń z wyświetlanej tabeli
    tree_farms.delete(item_id)
    # Usuń powiązanych pracowników i klientów (aby nie było odwołań do nieistniejącego gospodarstwa)
    removed_emp_ids = [emp["id"] for emp in employees if emp["farm_id"] == farm["id"]]
    employees = [emp for emp in employees if emp["farm_id"] != farm["id"]]
    for emp_id in removed_emp_ids:
        if tree_employees.exists(str(emp_id)):
            tree_employees.delete(str(emp_id))
    removed_cli_ids = [cli["id"] for cli in clients if cli["farm_id"] == farm["id"]]
    clients = [cli for cli in clients if cli["farm_id"] != farm["id"]]
    for cli_id in removed_cli_ids:
        if tree_clients.exists(str(cli_id)):
            tree_clients.delete(str(cli_id))
    # Wyczyść pola formularza (jeśli było wypełnione danymi usuniętego gospodarstwa)
    entry_farm_name.delete(0, tk.END)
    entry_farm_city.delete(0, tk.END)
    # Odśwież listy gospodarstw w comboboxach
    refresh_farm_options()
    # Odśwież mapę, jeśli obecnie wyświetlała dane związane z usuniętym gospodarstwem
    if map_mode.get() in ["Wszystkie gospodarstwa", "Pracownicy wybranego gospodarstwa",
                          "Klienci wybranego gospodarstwa"]:
        update_map()


# Funkcje dla pracowników
def add_employee():
    """Dodaje nowego pracownika na podstawie pól formularza."""
    global employees, next_employee_id
    name = entry_emp_name.get().strip()
    city = entry_emp_city.get().strip()
    farm_name = combo_emp_farm.get().strip()
    if not name or not city or not farm_name:
        messagebox.showerror("Błąd", "Proszę podać imię i miasto pracownika oraz wybrać gospodarstwo.")
        return
    farm = next((f for f in farms if f["name"] == farm_name), None)
    if farm is None:
        messagebox.showerror("Błąd", "Wybrane gospodarstwo nie istnieje.")
        return
    try:
        coords = get_coordinates_for_city(city)
    except Exception as e:
        if str(e) == "network_error":
            messagebox.showerror("Błąd", "Błąd podczas pobierania współrzędnych. Sprawdź połączenie internetowe.")
        else:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania współrzędnych: {e}")
        return
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla lokalizacji '{city}'.")
        return
    lat, lon = coords
    # Dodaj pracownika do listy
    employee = {"id": next_employee_id, "name": name, "city": city, "coords": (lat, lon), "farm_id": farm["id"]}
    employees.append(employee)
    next_employee_id += 1
    # Dodaj do tabeli w zakładce "Pracownicy"
    tree_employees.insert("", "end", iid=str(employee["id"]), values=(employee["name"], employee["city"], farm["name"]))
    # Wyczyść pola formularza
    entry_emp_name.delete(0, tk.END)
    entry_emp_city.delete(0, tk.END)
    combo_emp_farm.set('')
    # Odśwież mapę, jeśli pokazuje wszystkich lub pracowników danego gospodarstwa
    if map_mode.get() in ["Wszyscy pracownicy", "Pracownicy wybranego gospodarstwa"]:
        update_map()


def update_employee():
    """Aktualizuje dane wybranego pracownika."""
    global employees
    selected = tree_employees.selection()
    if not selected:
        messagebox.showerror("Błąd", "Nie wybrano pracownika do edycji.")
        return
    item_id = selected[0]
    employee = next((emp for emp in employees if str(emp["id"]) == item_id), None)
    if not employee:
        messagebox.showerror("Błąd", "Wybrany pracownik nie został znaleziony.")
        return
    new_name = entry_emp_name.get().strip()
    new_city = entry_emp_city.get().strip()
    farm_name = combo_emp_farm.get().strip()
    if not new_name or not new_city or not farm_name:
        messagebox.showerror("Błąd", "Proszę podać imię i miasto pracownika oraz wybrać gospodarstwo.")
        return
    farm = next((f for f in farms if f["name"] == farm_name), None)
    if farm is None:
        messagebox.showerror("Błąd", "Wybrane gospodarstwo nie istnieje.")
        return
    # Jeśli zmieniono miasto – pobierz nowe współrzędne
    if new_city.strip().lower() != employee["city"].lower():
        try:
            coords = get_coordinates_for_city(new_city)
        except Exception as e:
            if str(e) == "network_error":
                messagebox.showerror("Błąd", "Błąd podczas pobierania współrzędnych. Sprawdź połączenie internetowe.")
            else:
                messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania współrzędnych: {e}")
            return
        if coords is None:
            messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla lokalizacji '{new_city}'.")
            return
        employee["coords"] = coords
    # Zapisz zmiany danych pracownika
    employee["name"] = new_name
    employee["city"] = new_city
    employee["farm_id"] = farm["id"]
    # Zaktualizuj w tabeli (łącznie z ewentualną zmianą przypisanego gospodarstwa)
    tree_employees.item(item_id, values=(new_name, new_city, farm_name))
    # Odśwież mapę, jeśli dotyczy to aktualnie wyświetlanych danych
    if map_mode.get() in ["Wszyscy pracownicy", "Pracownicy wybranego gospodarstwa", "Klienci wybranego gospodarstwa"]:
        update_map()


def delete_employee():
    """Usuwa zaznaczonego pracownika."""
    global employees
    selected = tree_employees.selection()
    if not selected:
        messagebox.showerror("Błąd", "Nie wybrano pracownika do usunięcia.")
        return
    item_id = selected[0]
    employee = next((emp for emp in employees if str(emp["id"]) == item_id), None)
    if not employee:
        messagebox.showerror("Błąd", "Wybrany pracownik nie został znaleziony.")
        return
    # Usuń pracownika z listy i z tabeli
    employees = [emp for emp in employees if emp["id"] != employee["id"]]
    tree_employees.delete(item_id)
    # Wyczyść pola formularza
    entry_emp_name.delete(0, tk.END)
    entry_emp_city.delete(0, tk.END)
    combo_emp_farm.set('')
    # Odśwież mapę, jeśli aktualnie pokazuje pracowników
    if map_mode.get() in ["Wszyscy pracownicy", "Pracownicy wybranego gospodarstwa"]:
        update_map()


# Funkcje dla klientów
def add_client():
    """Dodaje nowego klienta."""
    global clients, next_client_id
    name = entry_cli_name.get().strip()
    city = entry_cli_city.get().strip()
    farm_name = combo_cli_farm.get().strip()
    if not name or not city or not farm_name:
        messagebox.showerror("Błąd", "Proszę podać nazwę i miasto klienta oraz wybrać gospodarstwo.")
        return
    farm = next((f for f in farms if f["name"] == farm_name), None)
    if farm is None:
        messagebox.showerror("Błąd", "Wybrane gospodarstwo nie istnieje.")
        return
    try:
        coords = get_coordinates_for_city(city)
    except Exception as e:
        if str(e) == "network_error":
            messagebox.showerror("Błąd", "Błąd podczas pobierania współrzędnych. Sprawdź połączenie internetowe.")
        else:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania współrzędnych: {e}")
        return
    if coords is None:
        messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla lokalizacji '{city}'.")
        return
    lat, lon = coords
    # Dodaj klienta do listy
    client = {"id": next_client_id, "name": name, "city": city, "coords": (lat, lon), "farm_id": farm["id"]}
    clients.append(client)
    next_client_id += 1
    # Dodaj do tabeli wyświetlającej klientów
    tree_clients.insert("", "end", iid=str(client["id"]), values=(client["name"], client["city"], farm["name"]))
    # Wyczyść pola formularza
    entry_cli_name.delete(0, tk.END)
    entry_cli_city.delete(0, tk.END)
    combo_cli_farm.set('')
    # Odśwież mapę, jeśli aktualnie pokazuje wszystkich lub klientów wybranego gospodarstwa
    if map_mode.get() in ["Wszyscy klienci", "Klienci wybranego gospodarstwa"]:
        update_map()


def update_client():
    """Aktualizuje dane wybranego klienta."""
    global clients
    selected = tree_clients.selection()
    if not selected:
        messagebox.showerror("Błąd", "Nie wybrano klienta do edycji.")
        return
    item_id = selected[0]
    client = next((cli for cli in clients if str(cli["id"]) == item_id), None)
    if not client:
        messagebox.showerror("Błąd", "Wybrany klient nie został znaleziony.")
        return
    new_name = entry_cli_name.get().strip()
    new_city = entry_cli_city.get().strip()
    farm_name = combo_cli_farm.get().strip()
    if not new_name or not new_city or not farm_name:
        messagebox.showerror("Błąd", "Proszę podać nazwę i miasto klienta oraz wybrać gospodarstwo.")
        return
    farm = next((f for f in farms if f["name"] == farm_name), None)
    if farm is None:
        messagebox.showerror("Błąd", "Wybrane gospodarstwo nie istnieje.")
        return
    # Jeśli zmieniono miasto – pobierz ewentualnie nowe współrzędne
    if new_city.strip().lower() != client["city"].lower():
        try:
            coords = get_coordinates_for_city(new_city)
        except Exception as e:
            if str(e) == "network_error":
                messagebox.showerror("Błąd", "Błąd podczas pobierania współrzędnych. Sprawdź połączenie internetowe.")
            else:
                messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania współrzędnych: {e}")
            return
        if coords is None:
            messagebox.showerror("Błąd", f"Nie znaleziono współrzędnych GPS dla lokalizacji '{new_city}'.")
            return
        client["coords"] = coords
    # Zapisz zmiany w danych klienta
    client["name"] = new_name
    client["city"] = new_city
    client["farm_id"] = farm["id"]
    # Zaktualizuj w tabeli (łącznie ze zmianą gospodarstwa, jeśli dotyczy)
    tree_clients.item(item_id, values=(new_name, new_city, farm_name))
    # Odśwież mapę, jeśli dotyczy to aktualnie wyświetlanych danych (np. klienci danego gospodarstwa)
    if map_mode.get() in ["Wszyscy klienci", "Klienci wybranego gospodarstwa", "Pracownicy wybranego gospodarstwa"]:
        update_map()


def delete_client():
    """Usuwa zaznaczonego klienta."""
    global clients
    selected = tree_clients.selection()
    if not selected:
        messagebox.showerror("Błąd", "Nie wybrano klienta do usunięcia.")
        return
    item_id = selected[0]
    client = next((cli for cli in clients if str(cli["id"]) == item_id), None)
    if not client:
        messagebox.showerror("Błąd", "Wybrany klient nie został znaleziony.")
        return
    # Usuń klienta z listy i z tabeli
    clients = [cli for cli in clients if cli["id"] != client["id"]]
    tree_clients.delete(item_id)
    # Wyczyść pola formularza
    entry_cli_name.delete(0, tk.END)
    entry_cli_city.delete(0, tk.END)
    combo_cli_farm.set('')
    # Odśwież mapę, jeśli aktualnie pokazuje klientów
    if map_mode.get() in ["Wszyscy klienci", "Klienci wybranego gospodarstwa"]:
        update_map()


# Funkcja odświeżająca listy gospodarstw w polach wyboru (combobox) na innych zakładkach
def refresh_farm_options():
    farm_names = [f["name"] for f in farms]
    combo_emp_farm['values'] = farm_names
    combo_cli_farm['values'] = farm_names
    combo_map_farm['values'] = farm_names
    # Jeśli wybrane gospodarstwo na mapie już nie istnieje (np. po usunięciu) – wyczyść wybór
    current_farm = combo_map_farm.get()
    if current_farm and current_farm not in farm_names:
        combo_map_farm.set('')


# Funkcje obsługi wyboru elementu z list (aby wypełnić formularze do edycji)
def on_farm_tree_select(event):
    selected = tree_farms.selection()
    if not selected:
        return
    item_id = selected[0]
    farm = next((f for f in farms if str(f["id"]) == item_id), None)
    if farm:
        entry_farm_name.delete(0, tk.END)
        entry_farm_name.insert(0, farm["name"])
        entry_farm_city.delete(0, tk.END)
        entry_farm_city.insert(0, farm["city"])


def on_employee_tree_select(event):
    selected = tree_employees.selection()
    if not selected:
        return
    item_id = selected[0]
    emp = next((e for e in employees if str(e["id"]) == item_id), None)
    if emp:
        entry_emp_name.delete(0, tk.END)
        entry_emp_name.insert(0, emp["name"])
        entry_emp_city.delete(0, tk.END)
        entry_emp_city.insert(0, emp["city"])
        farm = next((f for f in farms if f["id"] == emp["farm_id"]), None)
        combo_emp_farm.set(farm["name"] if farm else '')


def on_client_tree_select(event):
    selected = tree_clients.selection()
    if not selected:
        return
    item_id = selected[0]
    cli = next((c for c in clients if str(c["id"]) == item_id), None)
    if cli:
        entry_cli_name.delete(0, tk.END)
        entry_cli_name.insert(0, cli["name"])
        entry_cli_city.delete(0, tk.END)
        entry_cli_city.insert(0, cli["city"])
        farm = next((f for f in farms if f["id"] == cli["farm_id"]), None)
        combo_cli_farm.set(farm["name"] if farm else '')


# Funkcja aktualizująca widok mapy na podstawie wybranego trybu
def update_map(event=None):
    # Usuń istniejące markery
    map_widget.delete_all_marker()
    mode = map_mode.get()
    if mode == "Wszystkie gospodarstwa":
        # Pokaż markery dla wszystkich gospodarstw
        for f in farms:
            lat, lon = f["coords"]
            map_widget.set_marker(lat, lon, text=f["name"])
        # Dopasuj widok do wszystkich gospodarstw
        if farms:
            lats = [f["coords"][0] for f in farms]
            lons = [f["coords"][1] for f in farms]
            max_lat, min_lat = max(lats), min(lats)
            max_lon, min_lon = max(lons), min(lons)
            if max_lat == min_lat and max_lon == min_lon:
                # Tylko jeden punkt
                map_widget.set_position(max_lat, max_lon)
                map_widget.set_zoom(12)
            else:
                # Dopasuj przybliżenie do obszaru obejmującego wszystkie punkty
                map_widget.fit_bounding_box((max_lat, min_lon), (min_lat, max_lon))
    elif mode == "Wszyscy pracownicy":
        for emp in employees:
            lat, lon = emp["coords"]
            map_widget.set_marker(lat, lon, text=emp["name"])
        if employees:
            lats = [emp["coords"][0] for emp in employees]
            lons = [emp["coords"][1] for emp in employees]
            max_lat, min_lat = max(lats), min(lats)
            max_lon, min_lon = max(lons), min(lons)
            if max_lat == min_lat and max_lon == min_lon:
                map_widget.set_position(max_lat, max_lon)
                map_widget.set_zoom(12)
            else:
                map_widget.fit_bounding_box((max_lat, min_lon), (min_lat, max_lon))
    elif mode == "Wszyscy klienci":
        for cli in clients:
            lat, lon = cli["coords"]
            map_widget.set_marker(lat, lon, text=cli["name"])
        if clients:
            lats = [cli["coords"][0] for cli in clients]
            lons = [cli["coords"][1] for cli in clients]
            max_lat, min_lat = max(lats), min(lats)
            max_lon, min_lon = max(lons), min(lons)
            if max_lat == min_lat and max_lon == min_lon:
                map_widget.set_position(max_lat, max_lon)
                map_widget.set_zoom(12)
            else:
                map_widget.fit_bounding_box((max_lat, min_lon), (min_lat, max_lon))
    elif mode == "Pracownicy wybranego gospodarstwa":
        farm_name = combo_map_farm.get().strip()
        if not farm_name:
            return  # jeśli nie wybrano gospodarstwa, nic nie pokazuj
        farm = next((f for f in farms if f["name"] == farm_name), None)
        if not farm:
            return
        emps = [e for e in employees if e["farm_id"] == farm["id"]]
        for emp in emps:
            lat, lon = emp["coords"]
            map_widget.set_marker(lat, lon, text=emp["name"])
        if emps:
            lats = [e["coords"][0] for e in emps]
            lons = [e["coords"][1] for e in emps]
            max_lat, min_lat = max(lats), min(lats)
            max_lon, min_lon = max(lons), min(lons)
            if max_lat == min_lat and max_lon == min_lon:
                map_widget.set_position(max_lat, max_lon)
                map_widget.set_zoom(12)
            else:
                map_widget.fit_bounding_box((max_lat, min_lon), (min_lat, max_lon))
        elif farm:
            # Jeśli brak pracowników, ustaw widok na samo gospodarstwo
            lat, lon = farm["coords"]
            map_widget.set_position(lat, lon)
            map_widget.set_zoom(12)
    elif mode == "Klienci wybranego gospodarstwa":
        farm_name = combo_map_farm.get().strip()
        if not farm_name:
            return
        farm = next((f for f in farms if f["name"] == farm_name), None)
        if not farm:
            return
        clis = [c for c in clients if c["farm_id"] == farm["id"]]
        for cli in clis:
            lat, lon = cli["coords"]
            map_widget.set_marker(lat, lon, text=cli["name"])
        if clis:
            lats = [c["coords"][0] for c in clis]
            lons = [c["coords"][1] for c in clis]
            max_lat, min_lat = max(lats), min(lats)
            max_lon, min_lon = max(lons), min(lons)
            if max_lat == min_lat and max_lon == min_lon:
                map_widget.set_position(max_lat, max_lon)
                map_widget.set_zoom(12)
            else:
                map_widget.fit_bounding_box((max_lat, min_lon), (min_lat, max_lon))
        elif farm:
            lat, lon = farm["coords"]
            map_widget.set_position(lat, lon)
            map_widget.set_zoom(12)


def map_mode_changed(event=None):
    """Reakcja na zmianę trybu wyświetlania mapy – włącza/wyłącza wybór gospodarstwa."""
    mode = map_mode.get()
    if mode in ["Pracownicy wybranego gospodarstwa", "Klienci wybranego gospodarstwa"]:
        combo_map_farm['state'] = 'readonly'  # umożliw wybór gospodarstwa
    else:
        combo_map_farm.set('')  # wyczyść wybór gospodarstwa
        combo_map_farm['state'] = 'disabled'  # dezaktywuj pole wyboru gospodarstwa
    update_map()  # zaktualizuj widok mapy zgodnie z nowym trybem



root = tk.Tk()
root.title("Zarządzanie gospodarstwem")
root.geometry("1000x600")

# Zakładki (Notebook)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)
tab_farms = ttk.Frame(notebook)
tab_employees = ttk.Frame(notebook)
tab_clients = ttk.Frame(notebook)
tab_map = ttk.Frame(notebook)
notebook.add(tab_farms, text="Gospodarstwa")
notebook.add(tab_employees, text="Pracownicy")
notebook.add(tab_clients, text="Klienci")
notebook.add(tab_map, text="Mapa")

# Zakładka Gospodarstwa
frame_farm_list = tk.Frame(tab_farms)
frame_farm_list.pack(fill='both', expand=True)
tree_farms = ttk.Treeview(frame_farm_list, columns=("Nazwa", "Miasto"), show='headings')
tree_farms.heading("Nazwa", text="Nazwa")
tree_farms.heading("Miasto", text="Miasto")
tree_farms.column("Nazwa", width=150)
tree_farms.column("Miasto", width=150)
scroll_farms = ttk.Scrollbar(frame_farm_list, orient=tk.VERTICAL, command=tree_farms.yview)
tree_farms.configure(yscrollcommand=scroll_farms.set)
tree_farms.pack(side=tk.LEFT, fill='both', expand=True)
scroll_farms.pack(side=tk.RIGHT, fill='y')
tree_farms.bind("<<TreeviewSelect>>", on_farm_tree_select)

frame_farm_form = ttk.Frame(tab_farms, padding=10)
frame_farm_form.pack(fill='x')
tk.Label(frame_farm_form, text="Nazwa:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
entry_farm_name = tk.Entry(frame_farm_form)
entry_farm_name.grid(row=0, column=1, padx=5, pady=2, sticky='w')
tk.Label(frame_farm_form, text="Miasto:").grid(row=1, column=0, padx=5, pady=2, sticky='e')
entry_farm_city = tk.Entry(frame_farm_form)
entry_farm_city.grid(row=1, column=1, padx=5, pady=2, sticky='w')
btn_add_farm = ttk.Button(frame_farm_form, text="Dodaj", command=add_farm)
btn_add_farm.grid(row=2, column=0, padx=5, pady=5, sticky='w')
btn_update_farm = ttk.Button(frame_farm_form, text="Aktualizuj", command=update_farm)
btn_update_farm.grid(row=2, column=1, padx=5, pady=5, sticky='w')
btn_delete_farm = ttk.Button(frame_farm_form, text="Usuń", command=delete_farm)
btn_delete_farm.grid(row=2, column=2, padx=5, pady=5, sticky='w')

# Zakładka Pracownicy
frame_emp_list = tk.Frame(tab_employees)
frame_emp_list.pack(fill='both', expand=True)
tree_employees = ttk.Treeview(frame_emp_list, columns=("Imię", "Miasto", "Gospodarstwo"), show='headings')
tree_employees.heading("Imię", text="Imię i nazwisko")
tree_employees.heading("Miasto", text="Miasto")
tree_employees.heading("Gospodarstwo", text="Gospodarstwo")
tree_employees.column("Imię", width=150)
tree_employees.column("Miasto", width=150)
tree_employees.column("Gospodarstwo", width=150)
scroll_emp = ttk.Scrollbar(frame_emp_list, orient=tk.VERTICAL, command=tree_employees.yview)
tree_employees.configure(yscrollcommand=scroll_emp.set)
tree_employees.pack(side=tk.LEFT, fill='both', expand=True)
scroll_emp.pack(side=tk.RIGHT, fill='y')
tree_employees.bind("<<TreeviewSelect>>", on_employee_tree_select)

frame_emp_form = ttk.Frame(tab_employees, padding=10)
frame_emp_form.pack(fill='x')
tk.Label(frame_emp_form, text="Imię i nazwisko:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
entry_emp_name = tk.Entry(frame_emp_form)
entry_emp_name.grid(row=0, column=1, padx=5, pady=2, sticky='w')
tk.Label(frame_emp_form, text="Miasto:").grid(row=1, column=0, padx=5, pady=2, sticky='e')
entry_emp_city = tk.Entry(frame_emp_form)
entry_emp_city.grid(row=1, column=1, padx=5, pady=2, sticky='w')
tk.Label(frame_emp_form, text="Gospodarstwo:").grid(row=2, column=0, padx=5, pady=2, sticky='e')
combo_emp_farm = ttk.Combobox(frame_emp_form, state="readonly")
combo_emp_farm.grid(row=2, column=1, padx=5, pady=2, sticky='w')
btn_add_emp = ttk.Button(frame_emp_form, text="Dodaj", command=add_employee)
btn_add_emp.grid(row=3, column=0, padx=5, pady=5, sticky='w')
btn_update_emp = ttk.Button(frame_emp_form, text="Aktualizuj", command=update_employee)
btn_update_emp.grid(row=3, column=1, padx=5, pady=5, sticky='w')
btn_delete_emp = ttk.Button(frame_emp_form, text="Usuń", command=delete_employee)
btn_delete_emp.grid(row=3, column=2, padx=5, pady=5, sticky='w')

# Zakładka Klienci
frame_cli_list = tk.Frame(tab_clients)
frame_cli_list.pack(fill='both', expand=True)
tree_clients = ttk.Treeview(frame_cli_list, columns=("Nazwa", "Miasto", "Gospodarstwo"), show='headings')
tree_clients.heading("Nazwa", text="Nazwa klienta")
tree_clients.heading("Miasto", text="Miasto")
tree_clients.heading("Gospodarstwo", text="Gospodarstwo")
tree_clients.column("Nazwa", width=150)
tree_clients.column("Miasto", width=150)
tree_clients.column("Gospodarstwo", width=150)
scroll_cli = ttk.Scrollbar(frame_cli_list, orient=tk.VERTICAL, command=tree_clients.yview)
tree_clients.configure(yscrollcommand=scroll_cli.set)
tree_clients.pack(side=tk.LEFT, fill='both', expand=True)
scroll_cli.pack(side=tk.RIGHT, fill='y')
tree_clients.bind("<<TreeviewSelect>>", on_client_tree_select)

frame_cli_form = ttk.Frame(tab_clients, padding=10)
frame_cli_form.pack(fill='x')
tk.Label(frame_cli_form, text="Nazwa klienta:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
entry_cli_name = tk.Entry(frame_cli_form)
entry_cli_name.grid(row=0, column=1, padx=5, pady=2, sticky='w')
tk.Label(frame_cli_form, text="Miasto:").grid(row=1, column=0, padx=5, pady=2, sticky='e')
entry_cli_city = tk.Entry(frame_cli_form)
entry_cli_city.grid(row=1, column=1, padx=5, pady=2, sticky='w')
tk.Label(frame_cli_form, text="Gospodarstwo:").grid(row=2, column=0, padx=5, pady=2, sticky='e')
combo_cli_farm = ttk.Combobox(frame_cli_form, state="readonly")
combo_cli_farm.grid(row=2, column=1, padx=5, pady=2, sticky='w')
btn_add_cli = ttk.Button(frame_cli_form, text="Dodaj", command=add_client)
btn_add_cli.grid(row=3, column=0, padx=5, pady=5, sticky='w')
btn_update_cli = ttk.Button(frame_cli_form, text="Aktualizuj", command=update_client)
btn_update_cli.grid(row=3, column=1, padx=5, pady=5, sticky='w')
btn_delete_cli = ttk.Button(frame_cli_form, text="Usuń", command=delete_client)
btn_delete_cli.grid(row=3, column=2, padx=5, pady=5, sticky='w')

# Zakładka "Mapa"
frame_map_controls = ttk.Frame(tab_map, padding=5)
frame_map_controls.pack(fill='x')
tk.Label(frame_map_controls, text="Pokaż:").grid(row=0, column=0, padx=5, pady=2)
map_mode = tk.StringVar(value="Wszystkie gospodarstwa")
combo_map_mode = ttk.Combobox(frame_map_controls, textvariable=map_mode, state="readonly",
                              values=["Wszystkie gospodarstwa", "Wszyscy pracownicy", "Wszyscy klienci",
                                      "Pracownicy wybranego gospodarstwa", "Klienci wybranego gospodarstwa"])
combo_map_mode.grid(row=0, column=1, padx=5, pady=2)
combo_map_mode.bind("<<ComboboxSelected>>", map_mode_changed)
tk.Label(frame_map_controls, text="Gospodarstwo:").grid(row=0, column=2, padx=5, pady=2)
combo_map_farm = ttk.Combobox(frame_map_controls, state="readonly")
combo_map_farm.grid(row=0, column=3, padx=5, pady=2)
combo_map_farm.bind("<<ComboboxSelected>>", update_map)

map_widget = TkinterMapView(tab_map, width=800, height=500, corner_radius=0)
map_widget.pack(fill="both", expand=True)
map_widget.set_position(52.0, 19.0)
map_widget.set_zoom(6)

combo_map_farm['state'] = 'disabled'

root.mainloop()

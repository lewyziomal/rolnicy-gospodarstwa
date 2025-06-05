from tkinter import *
import tkintermapview
import requests
from bs4 import BeautifulSoup
import re

gospodarstwa: list = []


def dms_to_decimal(dms_str: str) -> float:

    match = re.match(r"(\d+)°(\d+)′(\d+)″([NSEW])", dms_str)
    if not match:
        raise ValueError(f"Niepoprawny format DMS: {dms_str}")
    deg, minutes, seconds, hemi = match.groups()
    deg = int(deg)
    minutes = int(minutes)
    seconds = int(seconds)
    dec = deg + minutes / 60 + seconds / 3600
    if hemi in ("S", "W"):
        dec = -dec
    return dec


class Gospodarstwo:
    def __init__(self, nazwa, miejscowosc, firma, szczegoly):
        self.nazwa = nazwa
        self.miejscowosc = miejscowosc
        self.firma = firma
        self.szczegoly = szczegoly
        self.coordinates = self.get_coordinates()
        self.marker = None

    def get_coordinates(self) -> list:
        url = f"https://pl.wikipedia.org/wiki/{self.miejscowosc.replace(' ', '_')}"
        response = requests.get(url)
        response_html = BeautifulSoup(response.text, "html.parser")
        lat_elems = response_html.select(".latitude")
        lon_elems = response_html.select(".longitude")
        if not lat_elems or not lon_elems:
            raise Exception("Brak współrzędnych na Wikipedii")
        lat_dms = lat_elems[0].text.strip()
        lon_dms = lon_elems[0].text.strip()
        latitude = dms_to_decimal(lat_dms)
        longitude = dms_to_decimal(lon_dms)
        return [latitude, longitude]

    def place_marker(self, map_widget):
        # Usuń poprzedni marker, jeśli istnieje
        if self.marker:
            self.marker.delete()
        # Tworzymy marker BEZ tekstu (brak napisu z firmą lub nazwą)
        self.marker = map_widget.set_marker(
            self.coordinates[0], self.coordinates[1]
        )


def dodaj_gospodarstwo():
    zm_nazwa = entry_nazwa.get().strip()
    zm_miejscowosc = entry_miejscowosc.get().strip()
    zm_firma = entry_firma.get().strip()
    zm_szczegoly = entry_szczegoly.get().strip()

    if not (zm_nazwa and zm_miejscowosc and zm_firma):
        return

    try:
        g = Gospodarstwo(zm_nazwa, zm_miejscowosc, zm_firma, zm_szczegoly)
    except Exception as e:
        print("Błąd pobierania współrzędnych:", e)
        return

    gospodarstwa.append(g)
    entry_nazwa.delete(0, END)
    entry_miejscowosc.delete(0, END)
    entry_firma.delete(0, END)
    entry_szczegoly.delete(0, END)
    entry_nazwa.focus()
    pokaz_gospodarstwa()


def pokaz_gospodarstwa():
    listbox_lista.delete(0, END)
    for idx, g in enumerate(gospodarstwa):
        listbox_lista.insert(idx, f"{idx + 1}. {g.nazwa} ({g.miejscowosc})")


def usun_gospodarstwo():
    try:
        i = listbox_lista.index(ACTIVE)
    except TclError:
        return
    g = gospodarstwa.pop(i)
    if g.marker:
        g.marker.delete()
    pokaz_gospodarstwa()
    czysc_szczegoly()


def pokaz_szczegoly_gospodarstwa():
    try:
        i = listbox_lista.index(ACTIVE)
    except TclError:
        return
    g = gospodarstwa[i]
    label_nazwa_wartosc.config(text=g.nazwa)
    label_miejscowosc_wartosc.config(text=g.miejscowosc)
    label_firma_wartosc.config(text=g.firma)
    label_szczegoly_wartosc.config(text=g.szczegoly)
    lat, lon = g.coordinates
    label_wspolrzedne_wartosc.config(text=f"{lat:.6f}, {lon:.6f}")

    map_widget.set_position(lat, lon)
    map_widget.set_zoom(10)
    g.place_marker(map_widget)


def edytuj_gospodarstwo():
    try:
        i = listbox_lista.index(ACTIVE)
    except TclError:
        return
    g = gospodarstwa[i]
    entry_nazwa.delete(0, END)
    entry_nazwa.insert(0, g.nazwa)
    entry_miejscowosc.delete(0, END)
    entry_miejscowosc.insert(0, g.miejscowosc)
    entry_firma.delete(0, END)
    entry_firma.insert(0, g.firma)
    entry_szczegoly.delete(0, END)
    entry_szczegoly.insert(0, g.szczegoly)

    button_dodaj.config(text="Zapisz gospodarstwo", command=lambda idx=i: update_gospodarstwo(idx))


def update_gospodarstwo(i):
    g = gospodarstwa[i]
    new_nazwa = entry_nazwa.get().strip()
    new_miejsc = entry_miejscowosc.get().strip()
    new_firma = entry_firma.get().strip()
    new_szczegoly = entry_szczegoly.get().strip()
    if not (new_nazwa and new_miejsc and new_firma):
        return

    g.nazwa = new_nazwa
    g.miejscowosc = new_miejsc
    g.firma = new_firma
    g.szczegoly = new_szczegoly

    try:
        g.coordinates = g.get_coordinates()
    except Exception as e:
        print("Błąd pobierania nowych współrzędnych:", e)
    if g.marker:
        g.marker.delete()
        g.marker = None

    button_dodaj.config(text="dodaj gospodarstwo", command=dodaj_gospodarstwo)
    entry_nazwa.delete(0, END)
    entry_miejscowosc.delete(0, END)
    entry_firma.delete(0, END)
    entry_szczegoly.delete(0, END)
    entry_nazwa.focus()
    pokaz_gospodarstwa()
    czysc_szczegoly()


def czysc_szczegoly():
    label_nazwa_wartosc.config(text="–")
    label_miejscowosc_wartosc.config(text="–")
    label_firma_wartosc.config(text="–")
    label_szczegoly_wartosc.config(text="–")
    label_wspolrzedne_wartosc.config(text="–")



root = Tk()
root.geometry("1200x760")
root.title("mapbook_ak")

ramka_lista = Frame(root)
ramka_form = Frame(root)
ramka_szczegoly = Frame(root)
ramka_mapa = Frame(root)

ramka_lista.grid(row=0, column=0, padx=5, pady=5)
ramka_form.grid(row=0, column=1, padx=5, pady=5)
ramka_szczegoly.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
ramka_mapa.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# ramka_lista
label_lista = Label(ramka_lista, text="LISTA GOSPODARSTW")
label_lista.grid(row=0, column=0, columnspan=3)
listbox_lista = Listbox(ramka_lista, width=60, height=15)
listbox_lista.grid(row=1, column=0, columnspan=3)
button_pokaz = Button(ramka_lista, text="pokaż szczegóły", command=pokaz_szczegoly_gospodarstwa)
button_pokaz.grid(row=2, column=0)
button_usun = Button(ramka_lista, text="usuń", command=usun_gospodarstwo)
button_usun.grid(row=2, column=1)
button_edytuj = Button(ramka_lista, text="edytuj", command=edytuj_gospodarstwo)
button_edytuj.grid(row=2, column=2)

# ramka_form
label_form = Label(ramka_form, text="FORMULARZ")
label_form.grid(row=0, column=0, columnspan=2)
Label(ramka_form, text="Nazwa").grid(row=1, column=0, sticky=W)
Label(ramka_form, text="Miejscowość").grid(row=2, column=0, sticky=W)
Label(ramka_form, text="Firma").grid(row=3, column=0, sticky=W)
Label(ramka_form, text="Szczegóły").grid(row=4, column=0, sticky=W)

entry_nazwa = Entry(ramka_form)
entry_nazwa.grid(row=1, column=1)
entry_miejscowosc = Entry(ramka_form)
entry_miejscowosc.grid(row=2, column=1)
entry_firma = Entry(ramka_form)
entry_firma.grid(row=3, column=1)
entry_szczegoly = Entry(ramka_form)
entry_szczegoly.grid(row=4, column=1)

button_dodaj = Button(ramka_form, text="dodaj gospodarstwo", command=dodaj_gospodarstwo)
button_dodaj.grid(row=5, column=0, columnspan=2)

# ramka_szczegoly
Label(ramka_szczegoly, text="szczegóły gospodarstwa:").grid(row=0, column=0)
Label(ramka_szczegoly, text="Nazwa:").grid(row=1, column=0)
label_nazwa_wartosc = Label(ramka_szczegoly, text="–")
label_nazwa_wartosc.grid(row=1, column=1)
Label(ramka_szczegoly, text="Miejscowość:").grid(row=1, column=2)
label_miejscowosc_wartosc = Label(ramka_szczegoly, text="–")
label_miejscowosc_wartosc.grid(row=1, column=3)
Label(ramka_szczegoly, text="Firma:").grid(row=1, column=4)
label_firma_wartosc = Label(ramka_szczegoly, text="–")
label_firma_wartosc.grid(row=1, column=5)
Label(ramka_szczegoly, text="Szczegóły:").grid(row=1, column=6)
label_szczegoly_wartosc = Label(ramka_szczegoly, text="–")
label_szczegoly_wartosc.grid(row=1, column=7)
Label(ramka_szczegoly, text="Współrzędne:").grid(row=1, column=8)
label_wspolrzedne_wartosc = Label(ramka_szczegoly, text="–")
label_wspolrzedne_wartosc.grid(row=1, column=9)

# ramka_mapa
map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=1200, height=600, corner_radius=5)
map_widget.set_position(52.23, 21.0)
map_widget.set_zoom(6)
map_widget.grid(row=0, column=0, columnspan=3)

root.mainloop()

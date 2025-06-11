from tkinter import *
import tkintermapview


users:list = []

class User:
    def __init__(self, nazwa_gospodarstwa, nazwa_firmy_gospodarstwa, location, posts):
        self.nazwa_gospodarstwa=nazwa_gospodarstwa
        self.nazwa_firmy_gospodarstwa=nazwa_firmy_gospodarstwa
        self.location=location
        self.posts=posts
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1])

    def get_coordinates(self)->list:
        import requests
        from bs4 import BeautifulSoup
        url=f"https://pl.wikipedia.org/wiki/{self.location}"
        response=requests.get(url)
        response_html=BeautifulSoup(response.text,"html.parser")
        latitude=float(response_html.select(".latitude")[1].text.replace(",","."))
        longitude=float(response_html.select(".longitude")[1].text.replace(",","."))
        return [latitude,longitude]


def add_user():
    zmienna_nazwa_gospodarstwa=entry_nazwa_gospodarstwa.get()
    zmienna_nazwisko=entry_nazwa_firmy_gospodarstwa.get()
    zmienna_miejscowosc=entry_location.get()
    zmienna_posty=entry_posts.get()

    users.append(User(nazwa_gospodarstwa = zmienna_nazwa_gospodarstwa, nazwa_firmy_gospodarstwa = zmienna_nazwisko, location = zmienna_miejscowosc, posts = zmienna_posty))
    print(users)
    entry_nazwa_gospodarstwa.delete(0, END)
    entry_nazwa_firmy_gospodarstwa.delete(0, END)
    entry_location.delete(0, END)
    entry_posts.delete(0, END)
    entry_nazwa_gospodarstwa.focus()
    show_users()

def show_users():
    listboox_lista_obiektow.delete(0, END)
    for idx, user in enumerate(users):
        listboox_lista_obiektow.insert(idx, f"{idx+1}. {user.nazwa_gospodarstwa} {user.nazwa_firmy_gospodarstwa}")

def remove_user():
    i=listboox_lista_obiektow.index(ACTIVE)
    users[i].marker.delete()
    users.pop(i)
    show_users()

def show_user_details():
    i=listboox_lista_obiektow.index(ACTIVE)
    user_nazwa_gospodarstwa=users[i].nazwa_gospodarstwa
    user_nazwa_firmy_gospodarstwa=users[i].nazwa_firmy_gospodarstwa
    user_location=users[i].location
    user_post=users[i].posts
    label_nazwa_gospodarstwa_szczegoly_obiektow_wartosc.config(text=user_nazwa_gospodarstwa)
    label_nazwa_firmy_gospodarstwa_szczegoly_obiektow_wartosc.config(text=user_nazwa_firmy_gospodarstwa)
    label_location_szczegoly_obiektow_wartosc.config(text=user_location)
    label_posts_szczegoly_obiektow_wartosc.config(text=user_post)
    map_widget.set_position(users[i].coordinates[0],users[i].coordinates[1])
    map_widget.set_zoom(12)

def edit_user():
    i=listboox_lista_obiektow.index(ACTIVE)
    user_nazwa_gospodarstwa=users[i].nazwa_gospodarstwa
    user_nazwa_firmy_gospodarstwa=users[i].nazwa_firmy_gospodarstwa
    user_location=users[i].location
    user_post=users[i].posts
    entry_nazwa_gospodarstwa.insert(0, user_nazwa_gospodarstwa)
    entry_nazwa_firmy_gospodarstwa.insert(0, user_nazwa_firmy_gospodarstwa)
    entry_location.insert(0, user_location)
    entry_posts.insert(0, user_post)

    button_dodaj_obiekt.config(text="zapisz", command=lambda: update_user(i))

def update_user(i):
    zmienna_nazwa_gospodarstwa = entry_nazwa_gospodarstwa.get()
    zmienna_nazwisko = entry_nazwa_firmy_gospodarstwa.get()
    zmienna_miejscowosc = entry_location.get()
    zmienna_posty = entry_posts.get()
    users[i].nazwa_gospodarstwa = zmienna_nazwa_gospodarstwa
    users[i].nazwa_firmy_gospodarstwa = zmienna_nazwisko
    users[i].location = zmienna_miejscowosc
    users[i].posts = zmienna_posty
    users[i].marker.delete()
    users[i].coordinates = users[i].get_coordinates()
    users[i].marker = map_widget.set_marker(users[i].coordinates[0],users[i].coordinates[1])
    print(users[i].coordinates)
    show_users()

    button_dodaj_obiekt.config(text="dodaj użytkownika", command=add_user)
    entry_nazwa_gospodarstwa.delete(0, END)
    entry_nazwa_firmy_gospodarstwa.delete(0, END)
    entry_location.delete(0, END)
    entry_posts.delete(0, END)
    entry_nazwa_gospodarstwa.focus()









root = Tk()
root.geometry("1200x760")
root.title("mapbook_ak")

ramka_lista_obiektow = Frame(root)
ramka_formularz = Frame(root)
ramka_szczegoly_obiektow = Frame(root)
ramka_mapa = Frame(root)

ramka_lista_obiektow.grid(row=0, column=0)
ramka_formularz.grid(row=0, column=1)
ramka_szczegoly_obiektow.grid(row=1, column=0, columnspan=2)
ramka_mapa.grid(row=2, column=0, columnspan=2)

# ramka_lista_obiektow
label_lista_obiektow = Label(ramka_lista_obiektow, text="LISTA GOSPODARSTW")
label_lista_obiektow.grid(row=0, column=0, columnspan=3)
listboox_lista_obiektow = Listbox(ramka_lista_obiektow, width=60, height=15)
listboox_lista_obiektow.grid(row=1, column=0, columnspan=3)
button_pokaz_szczegoly = Button(ramka_lista_obiektow, text="pokaż szczegóły farm", command=show_user_details)
button_pokaz_szczegoly.grid(row=2, column=0)
button_usun_obiekt = Button(ramka_lista_obiektow, text="usuń farmę", command=remove_user)
button_usun_obiekt.grid(row=2, column=1)
button_edytuj_obiekt = Button(ramka_lista_obiektow, text="edytuj informacje o farmie ", command=edit_user)
button_edytuj_obiekt.grid(row=2, column=2)

# ramka_formularz
label_ramka_formularz = Label(ramka_formularz, text="FORMULARZ")
label_ramka_formularz.grid(row=0, column=0, columnspan=2)
label_nazwa_gospodarstwa = Label(ramka_formularz, text="Nazwa Gospodarstwa")
label_nazwa_gospodarstwa.grid(row=1, column=0, sticky=W)
label_nazwa_firmy_gospodarstwa = Label(ramka_formularz, text="Rodzaj Gospodarstwa")
label_nazwa_firmy_gospodarstwa.grid(row=2, column=0, sticky=W)
label_location = Label(ramka_formularz, text="Miejscowość")
label_location.grid(row=3, column=0, sticky=W)
label_posts = Label(ramka_formularz, text="Ilość pracowników")
label_posts.grid(row=4, column=0, sticky=W)

entry_nazwa_gospodarstwa = Entry(ramka_formularz)
entry_nazwa_gospodarstwa.grid(row=1, column=1)
entry_nazwa_firmy_gospodarstwa = Entry(ramka_formularz)
entry_nazwa_firmy_gospodarstwa.grid(row=2, column=1)
entry_location = Entry(ramka_formularz)
entry_location.grid(row=3, column=1)
entry_posts = Entry(ramka_formularz)
entry_posts.grid(row=4, column=1)

button_dodaj_obiekt = Button(ramka_formularz, text="dodaj famrę", command=add_user)
button_dodaj_obiekt.grid(row=5, column=0, columnspan=2)

# ramka_szczegoly_obiektow
label_szczegoly_obiektow = Label(ramka_szczegoly_obiektow, text="szczegóły farmy: ")
label_szczegoly_obiektow.grid(row=0, column=0)
label_nazwa_gospodarstwa_szczegoly_obiektow = Label(ramka_szczegoly_obiektow, text="Nazwa Gospodarstwa: :")
label_nazwa_gospodarstwa_szczegoly_obiektow.grid(row=1, column=0)
label_nazwa_gospodarstwa_szczegoly_obiektow_wartosc = Label(ramka_szczegoly_obiektow, text="......")
label_nazwa_gospodarstwa_szczegoly_obiektow_wartosc.grid(row=1, column=1)
label_nazwa_firmy_gospodarstwa_szczegoly_obiektow = Label(ramka_szczegoly_obiektow, text="Rodzaj gospodarstwa:")
label_nazwa_firmy_gospodarstwa_szczegoly_obiektow.grid(row=1, column=2)
label_nazwa_firmy_gospodarstwa_szczegoly_obiektow_wartosc = Label(ramka_szczegoly_obiektow, text="......")
label_nazwa_firmy_gospodarstwa_szczegoly_obiektow_wartosc.grid(row=1, column=3)
label_location_szczegoly_obiektow = Label(ramka_szczegoly_obiektow, text="Miejscowość:")
label_location_szczegoly_obiektow.grid(row=1, column=4)
label_location_szczegoly_obiektow_wartosc = Label(ramka_szczegoly_obiektow, text="......")
label_location_szczegoly_obiektow_wartosc.grid(row=1, column=5)
label_posts_szczegoly_obiektow = Label(ramka_szczegoly_obiektow, text="Ilość pracowników:")
label_posts_szczegoly_obiektow.grid(row=1, column=6)
label_posts_szczegoly_obiektow_wartosc = Label(ramka_szczegoly_obiektow, text="......")
label_posts_szczegoly_obiektow_wartosc.grid(row=1, column=7)

# ramka_mapa
map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=1200, height=800, corner_radius=5)
map_widget.set_position(52.23, 21.0)
map_widget.set_zoom(6)
map_widget.grid(row=0, column=0, columnspan=3)

root.mainloop()


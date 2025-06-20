# main.py
import tkinter as tk
import tkintermapview
from utils.controller import get_coordinates


# Initialize main window
def main():
    root = tk.Tk()
    root.title("System Zarządzania Rolnikami")
    root.geometry("1200x700")

    # TODO: implement frames: list, form, details, map
    # Example:
    frame_list = tk.Frame(root)
    frame_form = tk.Frame(root)
    frame_details = tk.Frame(root)
    frame_map = tk.Frame(root)

    frame_list.grid(row=0, column=0, padx=10, pady=10)
    frame_form.grid(row=0, column=1, padx=10, pady=10)
    frame_details.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    frame_map.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Map widget
    map_widget = tkintermapview.TkinterMapView(frame_map, width=800, height=400)
    map_widget.pack()

    # TODO: Setup listboxes, entries, buttons,
    # bind CRUD functions, map views, details.

    root.mainloop()

if __name__ == '__main__':
    main()

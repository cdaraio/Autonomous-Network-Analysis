import tkinter as tk
from tkinter import Menu

class MainFrame(tk.Tk):
    def __init__(self, controllo_frame, title="Network Topology Mapper", window_width=1200, window_height=600):
        super().__init__()

        self.title(title)
        self.window_width = window_width
        self.window_height = window_height
        self.controllo_frame = controllo_frame  # Associazione al controllo
        self.larg_min = 730
        self.alt_min = 600
        self.minsize(self.larg_min, self.alt_min)
        self.center_window()

        self.attributes("-topmost", True)
        self.lift()
        self.after(100, lambda: self.attributes("-topmost", False))

        self.create_menu_bar()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        position_top = int(screen_height / 2 - self.window_height / 2)
        position_right = int(screen_width / 2 - self.window_width / 2)

        self.geometry(f'{self.window_width}x{self.window_height}+{position_right}+{position_top}')

    def create_menu_bar(self):
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Esci", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Guida", command=self.controllo_frame.mostra_guida)
        help_menu.add_command(label="Informazioni su...", command=self.controllo_frame.mostra_informazioni)
        menu_bar.add_cascade(label="Aiuto", menu=help_menu)

        self.config(menu=menu_bar)

    def set_view(self, view_instance):
        if hasattr(self, 'current_view'):
            self.current_view.destroy()
        self.current_view = view_instance
        self.current_view.pack(fill="both", expand=True)

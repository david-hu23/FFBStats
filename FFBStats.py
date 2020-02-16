from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os
import AllTimeStandings
from AllTimeStandings import figureOptions
from functools import partial

def start_application():
    """ Creates main window for the user to interact with.
    """
    application_window = generate_window()
    application_window.mainloop()

def generate_window():
    window = ApplicationWindow()
    window.geometry('1000x700')
    window.title('Fumbled From Birth')
    Grid.rowconfigure(window, 0, weight=1)
    Grid.columnconfigure(window, 0, weight=1)
    return window

class ApplicationWindow(Tk):

    def __init__(self):
        super().__init__()
        self.cached_JSON = list()
        self.generate_frame()
        self.set_icon()
        self.generate_commands()
        self.generate_buttons()
        self.generate_advanced_options()

    def generate_frame(self):
        self.layout_frame = Frame(self)
        self.layout_frame.grid(row=0, column=0, sticky=N+S+E+W)
        for x in range(2):
            Grid.rowconfigure(self.layout_frame, x, weight=1)
        for y in range(2):
            Grid.columnconfigure(self.layout_frame, y, weight=1)

    def set_icon(self):
        photo = self.get_icon()
        self.iconphoto(False, photo)

    def get_icon(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        return PhotoImage(file=os.path.join(current_directory, 'icon.gif'))
    
    def generate_commands(self):
        self.all_time_record_command = partial(on_click_all_time, self.cached_JSON, figureOptions.get("All Time Record"))
        self.all_time_record_adjusted_command = partial(on_click_all_time, self.cached_JSON, figureOptions.get("All Time Record - Adjusted (%)"))
        self.all_time_points_command = partial(on_click_all_time, self.cached_JSON, figureOptions.get("All Time Points"))
        self.all_time_points_adjusted_command = partial(on_click_all_time, self.cached_JSON, figureOptions.get("All Time Points - Adjusted (Per Game)"))

        self.clear_cache_command = partial(on_click_clear_cache_button, self.cached_JSON)

    def generate_buttons(self):
        self.all_time_record_button = Button(self.layout_frame, command=self.all_time_record_command, text="All Time Records")
        self.all_time_record_adjusted_button = Button(self.layout_frame, command=self.all_time_record_adjusted_command, text="All Time Record - Adjusted (%)")
        self.all_time_points_button = Button(self.layout_frame, command=self.all_time_points_command, text="All Time Points")
        self.all_time_points_adjusted_button = Button(self.layout_frame, command=self.all_time_points_adjusted_command, text="All Time Points - Adjusted (Per Game)")
    
        self.assign_buttons_to_grid()

    def assign_buttons_to_grid(self):
        self.all_time_record_button.grid(column=0, row=0, sticky=N+S+E+W)
        self.all_time_record_adjusted_button.grid(column=1, row=0, sticky=N+S+E+W)
        self.all_time_points_button.grid(column=0, row=1, sticky=N+S+E+W)
        self.all_time_points_adjusted_button.grid(column=1, row=1, sticky=N+S+E+W)

    def generate_advanced_options(self):
        self.advanced_options_menu = Menu(self)
        self.clear_cache_item = Menu(self.advanced_options_menu, tearoff=0)
        self.clear_cache_item.add_command(label='Clear cached data', command=self.clear_cache_command)
        self.advanced_options_menu.add_cascade(label='Advanced Options', menu=self.clear_cache_item)
        self.config(menu=self.advanced_options_menu)

def on_click_all_time(cached_JSON, figureOption):
    """ Command to execute when a button related to All Time stats is clicked. """
    if AllTimeStandings.main(cached_JSON, figureOption) is False:
        messagebox.showerror(
            'Unable to retrieve full league history',
            'One or more requests to ESPN failed. Verify you have a stable internet connection.')

def on_click_clear_cache_button(*cached_JSON):
    """ Clears any cached data from previous requests. Will force new requests to be triggered
        the next time we try to create any graphs.
    """
    for cachedList in cached_JSON:
        cachedList.clear()

if __name__ == "__main__":
    start_application()
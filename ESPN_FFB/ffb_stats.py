from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os
from ESPN_FFB.all_time_standings import  generate_all_time_graph
from ESPN_FFB.figure_options import FIGURE_OPTIONS
from ESPN_FFB.league_info import LeagueInfo
from functools import partial

def start_application():
    """ Creates main window for the user to interact with.
    """
    application_window = generate_window()
    application_window.mainloop()

def generate_window() -> Tk:
    window = ApplicationWindow()
    window.geometry('1000x700')
    window.title('Fumbled From Birth')
    Grid.rowconfigure(window, 0, weight=1)
    Grid.columnconfigure(window, 0, weight=1)
    return window

class ApplicationWindow(Tk):

    def __init__(self):
        super().__init__()
        self.league_info = LeagueInfo()
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

    def get_icon(self) -> PhotoImage:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        return PhotoImage(file=os.path.join(current_directory, 'icon.gif'))

    def generate_commands(self):
        self.all_time_record_command = partial(
            on_click_all_time,
            self.league_info,
            FIGURE_OPTIONS.get("All Time Record"))

        self.all_time_record_adjusted_command = partial(
            on_click_all_time,
            self.league_info,
            FIGURE_OPTIONS.get("All Time Record - Adjusted (%)"))

        self.all_time_points_command = partial(
            on_click_all_time,
            self.league_info,
            FIGURE_OPTIONS.get("All Time Points"))

        self.all_time_points_adjusted_command = partial(
            on_click_all_time,
            self.league_info,
            FIGURE_OPTIONS.get("All Time Points - Adjusted (Per Game)"))

        self.clear_cache_command = partial(on_click_clear_cache_button, self.league_info)

    def generate_buttons(self):
        self.all_time_record_button = Button(
            self.layout_frame,
            command=self.all_time_record_command,
            text="All Time Records")

        self.all_time_record_adjusted_button = Button(
            self.layout_frame,
            command=self.all_time_record_adjusted_command,
            text="All Time Record - Adjusted (%)")

        self.all_time_points_button = Button(
            self.layout_frame,
            command=self.all_time_points_command,
            text="All Time Points")

        self.all_time_points_adjusted_button = Button(
            self.layout_frame,
            command=self.all_time_points_adjusted_command,
            text="All Time Points - Adjusted (Per Game)")

        self.assign_buttons_to_grid()

    def assign_buttons_to_grid(self):
        self.all_time_record_button.grid(column=0, row=0, sticky=N+S+E+W)
        self.all_time_record_adjusted_button.grid(column=1, row=0, sticky=N+S+E+W)
        self.all_time_points_button.grid(column=0, row=1, sticky=N+S+E+W)
        self.all_time_points_adjusted_button.grid(column=1, row=1, sticky=N+S+E+W)

    def generate_advanced_options(self):
        self.advanced_options_menu = Menu(self)
        self.clear_cache_item = Menu(self.advanced_options_menu, tearoff=0)
        self.clear_cache_item.add_command(
            label='Clear cached data',
            command=self.clear_cache_command)

        self.advanced_options_menu.add_cascade(
            label='Advanced Options',
            menu=self.clear_cache_item)

        self.config(menu=self.advanced_options_menu)

def on_click_all_time(league_info: LeagueInfo, figure_option: int):
    """ Command to execute when a button related to All Time stats is clicked. """
    if generate_all_time_graph(league_info, figure_option) is False:
        messagebox.showerror(
            'Unable to retrieve full league history',
            'One or more requests to ESPN failed. Verify you have a stable internet connection.')

def on_click_clear_cache_button(league_info: LeagueInfo):
    """ Clears any cached data from previous requests. Will force new requests to be triggered
        the next time we try to create any graphs.
    """
    league_info.clear_cache()

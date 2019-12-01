from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os
import AllTimeStandings
from AllTimeStandings import figureOptions
from functools import partial

def on_click_AllTime(cachedJSON, figureOption):
    """ Command to execute when a button related to All Time stats is clicked. """
    if AllTimeStandings.main(cachedJSON, figureOption) is False:
        messagebox.showerror('Unable to retrieve full league history', 'One or more requests to ESPN failed. Verify you have a stable internet connection.')

def on_click_clearCacheButton(*cachedJSON):
    """ Clears any cached data from previous requests. Will force new requests to be triggered
        the next time we try to create any graphs.
    """
    for cachedList in cachedJSON:
        cachedList.clear()

def main():
    """ Creates main window for the user to interact with.
    """
    cachedJSON = list()   
    #Main Window
    window = Tk()
    window.geometry('1000x700')
    window.title('Fumbled From Birth')
    Grid.rowconfigure(window, 0, weight=1)
    Grid.columnconfigure(window, 0, weight=1)

    #Frame
    frame = Frame(window)
    frame.grid(row=0, column=0, sticky=N+S+E+W)
    for x in range(2):
        Grid.rowconfigure(frame, x, weight=1)
    for y in range(2):
        Grid.columnconfigure(frame, y, weight=1)

    #Images
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    photo = PhotoImage(file=os.path.join(currentDirectory, 'icon.gif'))
    window.iconphoto(False, photo)

    #All Time Record - Commands
    allTimeRecordCommand = partial(on_click_AllTime, cachedJSON, figureOptions.get("All Time Record"))
    allTimeRecordAdjustedCommand = partial(on_click_AllTime, cachedJSON, figureOptions.get("All Time Record - Adjusted (%)"))
    allTimePointsCommand = partial(on_click_AllTime, cachedJSON, figureOptions.get("All Time Points"))
    AlltimePointsAdjustedCommand = partial(on_click_AllTime, cachedJSON, figureOptions.get("All Time Points - Adjusted (Per Game)"))

    #All Time Record - Buttons
    allTimeRecordButton = Button(frame, command=allTimeRecordCommand, text="All Time Records")
    allTimeRecordAdjustedButton = Button(frame, command=allTimeRecordAdjustedCommand, text="All Time Record - Adjusted (%)")
    allTimePointsButton = Button(frame, command=allTimePointsCommand, text="All Time Points")
    allTimePointsAdjustedButton = Button(frame, command=AlltimePointsAdjustedCommand, text="All Time Points - Adjusted (Per Game)")

    #Advanced Options
    menu = Menu(window)
    clearCacheCommand = partial(on_click_clearCacheButton, cachedJSON)
    clearCacheItem = Menu(menu, tearoff=0)
    clearCacheItem.add_command(label='Clear cached data', command=clearCacheCommand)
    menu.add_cascade(label='Advanced Options', menu=clearCacheItem)
    window.config(menu=menu)

    #Assign buttons to grid position
    allTimeRecordButton.grid(column=0, row=0, sticky=N+S+E+W)
    allTimeRecordAdjustedButton.grid(column=1, row=0, sticky=N+S+E+W)
    allTimePointsButton.grid(column=0, row=1, sticky=N+S+E+W)
    allTimePointsAdjustedButton.grid(column=1, row=1, sticky=N+S+E+W)

    window.mainloop()

if __name__ == "__main__":
    main()
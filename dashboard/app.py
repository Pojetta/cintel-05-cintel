from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg
from collections import deque
import pandas as pd

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------


UPDATE_INTERVAL_SECS: int = 1

# --------------------------------------------
# Initialize a REACTIVE VALUE with a common data structure
# The reactive value is used to store state (information)
# Used by all the display components that show this live data.
# This reactive value is a wrapper around a DEQUE of readings
# --------------------------------------------

DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Initialize a REACTIVE CALC that all display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns a tuple with everything needed to display the data.
# Very easy to expand or modify.
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. 
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest

# Define the Shiny UI Page layout
# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI

# Page Options
ui.page_opts(title="PyShiny Express: Live Data (Basic)", fillable=True)

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently

with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )

    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
       href="https://github.com/pojetta/cintel-05-cintel-",
        target="_blank",
  )
    ui.a(
        "GitHub App",
        href="https://pojetta.github.io/cintel-05-cintel/",
        target="_blank",
  )
    ui.a("PyShiny", href="https://shiny.com", target="_blank")


with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-pink-orange",
    ):

        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest = reactive_calc_combined()
            return f"{latest['temp']} C"

        "warmer than usual"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest = reactive_calc_combined()
            return f"{latest['timestamp']}"


with ui.layout_columns():
    with ui.card():
        ui.card_header("Current Data (placeholder only)")

with ui.layout_columns():
    with ui.card():
        ui.card_header("Current Chart (placeholder only)")

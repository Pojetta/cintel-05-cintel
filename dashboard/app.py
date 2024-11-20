from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg

UPDATE_INTERVAL_SECS: int = 1

# Initialize a REACTIVE CALC that our display components can call
@reactive.calc()
def reactive_calc_combined():

    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between -18 and -16 C, rounded to 1 decimal place
    temp = round(random.uniform(-18, -16), 1)

    # Get a timestamp for "now" and use string format strftime() method to format it
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    latest = {"temp": temp, "timestamp": timestamp}

    # Return everything we need
    return latest

# Page Options
ui.page_opts(title="PyShiny Express: Live Data (Basic)", fillable=True)

# Sidebar
with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )

# Main Layout
ui.h2("Current Temperature")

@render.text
def display_temp():
    """Get the latest reading and return a temperature string"""
    latest = reactive_calc_combined()
    return f"{latest['temp']} C"

ui.p("warmer than usual")

icon_svg("sun")

ui.hr()

ui.h2("Current Date and Time")

@render.text
def display_time():
    """Get the latest reading and return a timestamp string"""
    latest = reactive_calc_combined()
    return f"{latest['timestamp']}"

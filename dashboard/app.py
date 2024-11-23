import random
from datetime import datetime
from collections import deque
from shiny import reactive, render
from shiny.express import ui
import pandas as pd
import plotly.express as px
from scipy import stats
from faicons import icon_svg

# https://fontawesome.com/v4/cheatsheet/

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------


UPDATE_INTERVAL_SECS: int = 3

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
ui.page_opts(title="PyShiny Express: Live Data")

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently

with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings.",
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
    with ui.card():
        ui.h2("Meanwhile, in Antarctica...")

        with ui.layout_column_wrap(width=1 / 2):
             with ui.value_box(
                theme=ui.value_box_theme(fg="#0B538E"),
    ):
        
                "At This Very Moment"

                @render.text
                def display_time():
                    """Get the latest reading and return a timestamp string"""
                    deque_snapshot, df, latest = reactive_calc_combined()
                    return f"{latest['timestamp']}"

                "(central standard time)"

        
             with ui.value_box(
                showcase=icon_svg("snowflake"),
                theme=ui.value_box_theme(fg = "#e6f2fd", bg="#0B538E"),
                showcase_layout="top right" 
    ):

                "Current Temperature"

                @render.text
                def display_temp():
                    """Get the latest reading and return a temperature string"""
                    deque_snapshot, df, latest = reactive_calc_combined()
                    return f"{latest['temp']} C"

                "Colder than usual"    


with ui.layout_columns():
    #with ui.card(full_screen=True, min_height="40%"):
    with ui.card(full_screen = True):
        ui.card_header("Most Recent Readings")

        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest = reactive_calc_combined()

            # Rename columns before displaying
            df = df.rename(columns={"temp": "Temperature (°C)", "timestamp": "Time"})
            
            # Use maximum width
            pd.set_option('display.width', None)       
            return render.DataGrid( df,width="100%")        


with ui.card():
    ui.card_header("Current Trend")
    
    @render.plot
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if df.empty:
            return "No data available for plotting."

        # Convert the 'timestamp' column to datetime for better plotting
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Create scatter plot for readings
        fig = px.scatter(df,
                         x="timestamp",
                         y="temp",
                         title="Temperature Readings with Regression Line",
                         labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                         color_discrete_sequence=["darkslategray"])

        # Linear regression - we need to get a list of the
        # Independent variable x values (time) and the
        # Dependent variable y values (temp)
        # Using time in seconds for more accurate regression
        x_vals = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds()
        y_vals = df["temp"]

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
        df['best_fit_line'] = [slope * x + intercept for x in x_vals]

        # Add the regression line to the figure
        fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

        # Update layout as needed to customize further
        fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")

        return fig

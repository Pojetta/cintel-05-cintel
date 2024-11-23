import random
from datetime import datetime
from collections import deque
from shiny import reactive, render
from shiny.express import ui
from shinywidgets import render_plotly
import pandas as pd
import plotly.express as px
from scipy import stats
from faicons import icon_svg

# Constants
UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 5

reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
    # Data generation logic
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # Update deque
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Return the updated data
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    latest = new_dictionary_entry
    return deque_snapshot, df, latest

# Shiny UI
ui.page_opts(title="PyShiny Express: Live Data")

with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p("A demonstration of real-time temperature readings.", class_="text-center")
    ui.hr()
    ui.h4("Links:")  # Increased heading level for better visibility
    ui.a("GitHub Source", href="https://github.com/pojetta/cintel-05-cintel-", target="_blank")
    ui.a("GitHub App", href="https://pojetta.github.io/cintel-05-cintel/", target="_blank")
    ui.a("PyShiny", href="https://shiny.com", target="_blank")

with ui.layout_columns():
    with ui.card():
        ui.h2("Meanwhile, in Antarctica...")

        with ui.layout_column_wrap(width=1 / 2):
            with ui.value_box(theme=ui.value_box_theme(fg="#0B538E")):
                "At This Very Moment"

                @render.text
                def display_time():
                    deque_snapshot, df, latest = reactive_calc_combined()
                    return f"{latest['timestamp']}"

                "(central standard time)"

            with ui.value_box(
                showcase=icon_svg("snowflake"),
                theme=ui.value_box_theme(fg="#e6f2fd", bg="#0B538E"),
                showcase_layout="top right"):
                "Current Temperature"

                @render.text
                def display_temp():
                    deque_snapshot, df, latest = reactive_calc_combined()
                    return f"{latest['temp']} C"

                "Colder than usual"

with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Most Recent Readings")

        @render.data_frame
        def display_df():
            deque_snapshot, df, latest = reactive_calc_combined()

            # Rename columns
            df = df.rename(columns={"temp": "Temperature (°C)", "timestamp": "Time"})
            pd.set_option('display.width', None)  # Use max width for display
            return render.DataGrid(df, width="100%")

with ui.card():
    ui.card_header("Current Trend")

    @render_plotly
    def display_plot():
        deque_snapshot, df, latest = reactive_calc_combined()

        # Ensure DataFrame is not empty
        if df.empty:
            return ui.p("No data available for plotting.")  # UI element for message

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Scatter plot with regression line
        fig = px.scatter(df,
                         x="timestamp",
                         y="temp",
                         title="Temperature Readings with Regression Line",
                         labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                         color_discrete_sequence=["blue"])

        # Linear regression
        x_vals = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds()
        y_vals = df["temp"]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
        df['best_fit_line'] = [slope * x + intercept for x in x_vals]

        # Add regression line
        fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

        # Customize layout
        fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
        return fig

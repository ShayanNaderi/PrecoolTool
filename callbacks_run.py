import json
import time

import dash
import pandas as pd
from dash import CeleryManager, DiskcacheManager, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from app_components import make_progress_graph
from DevelopThermalDynamicsModel import Building, join_PV_load_temp, run_scenarios
from PVPerformance import calculate_PV_output


# Create thermal model
@app.callback(
    output=(
        Output("thermal-model-creation-result", "children"),
        Output("hidden-div-df-data-storage", "children"),
        Output("coefficients-thermal-model", "children"),
    ),
    inputs=(
        Input("create-thermal-model-button", "n_clicks"),
        State("building-type-radio", "value"),
        State("construction-weight-radio", "value"),
        State("dwelling-type-radio", "value"),
        State("floor-area-radio", "value"),
    ),
    background=True,
    running=[
        (Output("create-thermal-model-button", "disabled"), True, False),
        (
            Output("thermal-model-creation-result", "children"),
            "Thermal model creation is in progress! Please wait!",
            "",
        ),
        (
            Output("thermal-model-creation-result", "style"),
            {"visibility": "visible"},
            {"visibility": "visible"},
        ),
    ],
    cancel=[Input("create-thermal-model-button", "n_clicks")],
    progress=Output("thermal-model-creation-result", "children"),
    prevent_initial_call=True,
)
def update_thermal_model(
    set_progress, n_clicks, starRating, weight, dwelling_type, size
):
    total = 20
    if n_clicks:
        building = Building(
            starRating=starRating,
            weight=weight,
            type=dwelling_type,
            size=size,
            city="Adelaide",
        )
        coeffs_df = building.thermal_coefficients.to_frame()
        coeffs_df.to_csv("coefficients.csv")
        coeffs_json = coeffs_df.to_json(date_format="iso", orient="split")
        thermal_dynamics_json = (
            building.thermal_dynamics_df.to_json(date_format="iso", orient="split"),
        )
        # jsonified_object = json.dumps(building.__dict__)

        return (
            "Thermal model is ready! Go to next steps or change the building specifications",
            thermal_dynamics_json,
            coeffs_json,
        )


# PV performance
@dash.callback(
    output=(
        Output("PV-simulation-result", "children"),
        Output("PV-results-hidden-div", "children"),
    ),
    inputs=(
        Input("PV-simulation-button", "n_clicks"),
        State("PV-orientation-radio", "value"),
        State("location-radio", "value"),
        State("PV-rated-capacity", "value"),
        State("inverter-efficiency", "value"),  # should be divided by 100
    ),
    background=True,
    running=[
        (Output("PV-simulation-button", "disabled"), True, False),
        (Output("cancel-button-id", "disabled"), False, True),
        (
            Output("PV-simulation-result", "style"),
            {"visibility": "visible"},
            {"visibility": "visible"},
        ),
        (
            Output("PV-simulation-result", "children"),
            "PV simulation in progress",
            "",
        ),
    ],
    cancel=[Input("PV-simulation-button", "n_clicks")],
    progress=Output("PV-simulation-result", "children"),
    prevent_initial_call=True,
)
def update_progress(
    set_progress,
    n_clicks,
    orientation,
    location,
    PV_rated_capacity,
    inverter_efficiency,
):
    if n_clicks:
        print(orientation, location, PV_rated_capacity, inverter_efficiency)
        inverter_efficiency = inverter_efficiency / 100  # number to
        PV_rated_capacity = PV_rated_capacity * 1000  # kW to Watt

        PV_generation = calculate_PV_output(
            city=location,
            orientation=orientation,
            PV_capacity_W=PV_rated_capacity,
            inv_efficiency=inverter_efficiency,
        )
        print(type(PV_generation))
        # PV_generation_df = PV_generation.to_frame()
        PV_generation_json = PV_generation.to_json(date_format="iso", orient="split")
        return (["PV performance is ready! Go to next steps!"], PV_generation_json)


# Solar pre-cooling main simulation loop
@dash.callback(
    output=Output("paragraph-id", "children"),
    inputs=(
        Input("analyze-button", "n_clicks"),
        State("coefficients-thermal-model", "children"),
        State("hidden-div-df-data-storage", "children"),
        State("PV-results-hidden-div", "children"),
        State("neutral-temp", "value"),
        State("deviation-up-temp", "value"),
        State("deviation-low-temp", "value"),
        State("weekdays-occupancy-checklist", "value"),
        State("weekend-occupancy-checklist", "value"),
        State("AC-rated-capacity", "value"),
        State("PV-rated-capacity", "value"),
        State("AC-year-radio", "value"),
    ),
    background=True,
    running=[
        (Output("analyze-button", "disabled"), True, False),
        (Output("cancel-button-id", "disabled"), False, True),
        (
            Output("paragraph-id", "style"),
            {"visibility": "visible"},
            {"visibility": "visible"},
        ),
        (
            Output("paragraph-id", "children"),
            "Solar pre-cooling simulation in progress",
            "",
        ),
    ],
    cancel=[Input("cancel-button-id", "n_clicks")],
    progress=Output("paragraph-id", "children"),
    prevent_initial_call=True,
)
def update_progress(
    set_progress,
    n_clicks,
    thermal_coefficients,
    hidden_div_thermal,
    hidden_div_PV,
    neutral_temp,
    deviation_up,
    deviation_low,
    weekdays_occ,
    weekends_occ,
    AC_size,
    PV_size,
    AC_made_year,
):
    if n_clicks:
        df_TMY = pd.read_json(hidden_div_thermal[0], orient="split")
        print("TMY ok")
        df_coeffs = pd.read_json(thermal_coefficients, orient="split")

        df_PV = pd.read_json(hidden_div_PV, orient="split")  # check if it is a list
        # print(df_TMY.head())
        print(
            AC_size,
            PV_size,
            AC_made_year,
            # hidden_div_thermal,
            # thermal_coefficients,
        )
        if df_coeffs is None:
            return [
                "No thermal model is available! Please create the thermal model first!"
            ]
        elif df_PV is None:
            return [
                "No PV simulation is available! please simulate PV performance first! "
            ]
        else:
            ready_df = join_PV_load_temp(df_PV, df_TMY)
            run_scenarios(ready_df)
            ready_df.to_csv("ready_df.csv")
            # print(ready_df.head())
            # I need thermal coefficients as well with the dataframe to simulate the baseline and SPC scenarios
            return []

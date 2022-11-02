import dash
import pandas as pd
from dash import CeleryManager, DiskcacheManager, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from DevelopThermalDynamicsModel import Building, join_PV_load_temp, run_scenarios
from PVPerformance import calculate_PV_output
from functions import create_tariff_column,read_demand_from_xlsx_file
from figures import line_plot


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
    print("Callback thermal model before click: OK", "nclicks",n_clicks)

    if n_clicks:
        building = Building(
            starRating=starRating,
            weight=weight,
            type=dwelling_type,
            size=size,
            AC_size=0,
            city="Adelaide",
            )
        print("Callback thermal model after click: OK")
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
        inverter_efficiency = inverter_efficiency / 100  # number to percent
        PV_rated_capacity = PV_rated_capacity * 1000  # kW to Watt

        PV_generation = calculate_PV_output(
            city=location,
            orientation=orientation,
            PV_capacity_W=PV_rated_capacity,
            inv_efficiency=inverter_efficiency,
        )
        print("PV output calculation OK")


        # PV_generation_df = PV_generation.to_frame()
        PV_generation_json = PV_generation.to_json(date_format="iso", orient="split")
        return (["PV performance is ready! Go to next steps!"], PV_generation_json)


# Solar pre-cooling main simulation loop
@dash.callback(
    output=(Output("paragraph-id", "children"),
    Output("PV-simulation-demand-figure", "children"),
    Output("surplus-PV-fig", "children"),
    Output("temperature-hourly", "children"),
    Output("AC-demand-hourly", "children"),
    Output("discomfort-hourly", "children")
            ),
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
        State("selected-demand-div-id", "children"),
        State("tariff-table", "data"),
        State("tariff-structure", "value"),
        State("flat-tariff-rate", "value"),
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
    upper_limit,
    lower_limit,
    weekdays_occ,
    weekends_occ,
    AC_size,
    PV_size,
    AC_made_year,
        site_id,
        tariff_data,
        tariff_structure,
        flat_rate,
):
    if n_clicks:
        print("click run simulation OK", n_clicks)
        if hidden_div_thermal is None:
            return ["No thermal model is available! Please create the thermal model first!"]
        elif hidden_div_PV is None:
            return ["No PV simulation is available! Please simulate PV performance first!"]
        elif site_id is None:
            return ["No demand profile is selected! Please select a demand profile first!"]
        print("Selected solar home {}".format(site_id))

        df_TMY = pd.read_json(hidden_div_thermal[0], orient="split")
        print("Thermal model ok")

        df_coeffs = pd.read_json(thermal_coefficients, orient="split")
        print("Coefficient reading OK")

        df_PV = pd.read_json(hidden_div_PV, orient="split")  # check if it is a list
        print("read PV simulation results OK")

        df_demand = read_demand_from_xlsx_file(site_id)
        print("Read demand file Ok")

        ready_df = join_PV_load_temp(PV=df_PV,load_temp = df_TMY, real_demand=df_demand)
        # This df is used for baseline and pre-cooling scenarios
        print("ready df ok")

        building = Building(
            starRating="2star",
            weight="heavy",
            type="Apartment",
            size="small",
            AC_size=AC_size,
            city="Adelaide",
        )
        building.occupancy_checklist = weekdays_occ
        tariff_df = pd.DataFrame.from_records(tariff_data)
        create_tariff_column(building=building,tariff_type=tariff_structure,tariff_table=tariff_df,flat_rate=flat_rate)
        building = run_scenarios(building,ready_df,neutral_temp,upper_limit,lower_limit)
        print("run scenarios Ok")

        fig_PV_demand = line_plot(building.averaged_hourly_results,'hour',["PV","Demand"],
                                  x_title="Time of the day [h]",y_title="[kW]",
                                  title="PV generation and AC excluded demand")
        fig_surplus_PV = line_plot(building.averaged_hourly_results,'hour',["Surplus_PV"],
                                  x_title="Time of the day [h]",y_title="[kW]",
                                  title="Surplus PV generation")
        fig_temperature = line_plot(building.averaged_hourly_results,'hour',["T_bs","T_spc"],x_title="Time of the day [h]",y_title="Temperature [°C]",title="Indoor temperature trajectory")
        fig_AC_demand = line_plot(building.averaged_hourly_results,'hour',["E_bs","E_spc"],x_title="Time of the day [h]",y_title="AC demand [kW]",title="AC demand profile")
        fig_thermal_discomfort = line_plot(building.averaged_hourly_results,'hour',
                                           ["W_bs","W_spc"],x_title="Time of the day [h]",
                                           y_title="Thermal discomfort [°C.hour]",title="Thermal discomfort",plot_type="bar_chart")
        print("figure Ok")
        return (["Successful!"],
                dcc.Graph(figure = fig_PV_demand),
                dcc.Graph(figure = fig_surplus_PV),
                dcc.Graph(figure = fig_temperature),
                dcc.Graph(figure=fig_AC_demand),
                dcc.Graph(figure=fig_thermal_discomfort))




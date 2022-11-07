import dash
import pandas as pd
from dash import CeleryManager, DiskcacheManager, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
import pickle
from app import app
from DevelopThermalDynamicsModel import Building, join_PV_load_temp, run_scenarios
from PVPerformance import calculate_PV_output
from functions import create_tariff_column,read_demand_from_xlsx_file
from figures import line_plot
from dynamicFigures import generate_single_building_graphs
import os

figure_border_style = {"border-style": "solid",
                          'border-color': '#ff4d4d', 'border-width': '1px', 'border-radius': "0.25rem"
                          }

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
        State("location-radio", "value"),

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
    set_progress, n_clicks, starRating, weight, dwelling_type, size,location
):
    if n_clicks:
        building = Building(
            starRating=starRating,
            weight=weight,
            type=dwelling_type,
            size=size,
            AC_size=0,
            city=location,
            )
        print("Callback thermal model after click: OK")
        coeffs_df = building.thermal_coefficients.to_frame()
        # coeffs_df.to_csv("coefficients.csv")
        coeffs_json = coeffs_df.to_json(date_format="iso", orient="split")
        thermal_dynamics_json = (
            building.thermal_dynamics_df.to_json(date_format="iso", orient="split"),
        )

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
        # print(orientation, location, PV_rated_capacity, inverter_efficiency)
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
        print("PV to Json ok")
        PV_generation.to_csv("PV_generation.csv")
        return (["PV performance is ready! Go to next steps!"], 1)


# Solar pre-cooling main simulation loop
@dash.callback(
    output=(Output("paragraph-id", "children"),
    Output("single-building-results-div", "children"),
    Output("single-building-results-div", "style"),
    Output("run-simulation-hidden-div", "children"),
    Output("list-of-buildings-hidden-div", "children"),
            ),
    inputs=(
        Input("add-case-study-button", "n_clicks"),
        Input("clean-case-study-button", "n_clicks"),
        Input("run-button", "n_clicks"),
        State("case-study-name", "value"),
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
        State("run-simulation-hidden-div", "children"),
        State("list-of-buildings-hidden-div", "children"),
        State("building-type-radio", "value"),
        State("construction-weight-radio", "value"),
        State("dwelling-type-radio", "value"),
        State("floor-area-radio", "value"),
        State("location-radio", "value"),
    ),
    background=True,
    running=[
        (Output("add-case-study-button", "disabled"), True, False),
        (Output("run-button", "disabled"), True, False),
        (Output("clean-case-study-button", "disabled"), True, False),
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
    n_click_add,
    n_cklick_clean_cases,
    n_clicks,
    name_case_study,
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
        hidden_div_run,
        hidden_div_list_buildings,starRating,weight,building_type,building_size,location
):

    list_of_buildings_name = hidden_div_list_buildings
    if len(list_of_buildings_name) == 0:
        isExist  = os.path.exists('list_of_buildings.pkl')
        if isExist == True:
            os.remove("list_of_buildings.pkl")
            print("PKL is removed")
        list_of_buildings = []
    else:
        print("PKL is loading")
        with open('list_of_buildings.pkl', 'rb') as inp:
            list_of_buildings = pickle.load(inp)
            print("PKL is loaded")

    if n_click_add != hidden_div_run[0]:
        print("click add simulation OK", n_click_add, hidden_div_run[0])

        if hidden_div_thermal is None:
            output_text = "No thermal model is available! Please create the thermal model first!"
            return (
            [output_text],[],None,
            hidden_div_run,
            []
            )
        elif hidden_div_PV is None:
            output_text = "No PV simulation is available! Please simulate PV performance first!"
            return (
            [output_text],[],None,
            hidden_div_run,
            []
            )
        elif site_id is None:
            output_text = "No demand profile is selected! Please select a demand profile first!"
            return (
            [output_text],[],None,
            hidden_div_run,
            []
            )
        elif name_case_study is None:
            output_text = "Please write a name for the case study!"
            return (
            [output_text],[],None,
            hidden_div_run,
            []
            )

        df_TMY = pd.read_json(hidden_div_thermal[0], orient="split")
        print("Thermal model ok")

        df_coeffs = pd.read_json(thermal_coefficients, orient="split")
        print("Coefficient reading OK")
        df_PV= pd.read_csv("PV_generation.csv")
        # df_PV = pd.read_json(hidden_div_PV, orient="split")  # check if it is a list
        print("read PV simulation results OK")

        df_demand = read_demand_from_xlsx_file(site_id)
        print("Read demand file Ok")

        ready_df = join_PV_load_temp(PV=df_PV,load_temp = df_TMY, real_demand=df_demand)
        # This df is used for baseline and pre-cooling scenarios
        print("ready df ok")

        building = Building(
            starRating=starRating,
            weight=weight,
            type=building_type,
            size=building_size,
            AC_size=AC_size,
            city=location,
        )
        building.name = name_case_study
        building.occupancy_checklist = weekdays_occ
        tariff_df = pd.DataFrame.from_records(tariff_data)
        create_tariff_column(building=building,tariff_type=tariff_structure,tariff_table=tariff_df,flat_rate=flat_rate)
        building.update_temperature_preferences(ready_df,neutral_temp,upper_limit,lower_limit)

        list_of_buildings.append(building)
        list_of_buildings_name.append(building.name)
        hidden_div_run = [n_click_add,n_cklick_clean_cases,n_clicks]
        with open("list_of_buildings.pkl", 'wb') as outp:
            pickle.dump(list_of_buildings, outp, pickle.HIGHEST_PROTOCOL)
        print("Hi, {} is added".format(name_case_study))

        return (["Hi, {} is added. number of case studies = {}".format(name_case_study,len(list_of_buildings_name))],
                [],None,
                hidden_div_run,
                list_of_buildings_name
                )
    if n_cklick_clean_cases != hidden_div_run[1]:
        hidden_div_run = [n_click_add,n_cklick_clean_cases,n_clicks]
        list_of_buildings_name = []
        isExist  = os.path.exists('list_of_buildings.pkl')
        if isExist == True:
            os.remove("list_of_buildings.pkl")

        return (["All case studies are removed. Number of case studies = {}".format(len(list_of_buildings_name))],
                [],None,
                hidden_div_run,
                list_of_buildings_name
                )
    if n_clicks != hidden_div_run[2]:
        print("click run simulation OK. number of case studies = ", n_clicks, hidden_div_run[1],len(list_of_buildings_name))

        if len(list_of_buildings_name) == 0:
            hidden_div_run = [n_click_add, n_cklick_clean_cases, n_clicks]

            return (["ٔNo case studies to run! Please create case studies"],
                    [],None,
                    hidden_div_run,
                    hidden_div_list_buildings
                    )
        else:
            with open('list_of_buildings.pkl', 'rb') as inp:
                list_of_buildings = pickle.load(inp)
            print("PKL is opened")

            list_of_buildings_name = hidden_div_list_buildings
            for building in list_of_buildings:
                print(building.name)
                building = run_scenarios(building)
                print("run scenarios Ok")

            with open("list_of_buildings.pkl", 'wb') as outp:
                pickle.dump(list_of_buildings, outp, pickle.HIGHEST_PROTOCOL)
            print("figure Ok")
            hidden_div_run = [n_click_add,n_cklick_clean_cases,n_clicks]
            return (["Successful!"],
                    generate_single_building_graphs(),figure_border_style,
                    hidden_div_run,
                    hidden_div_list_buildings
                    )




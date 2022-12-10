import pickle

import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html

from app import app
from figures import line_plot

single_building_available_figures = [
    "Indoor temperature",
    "AC demand",
    "Surplus PV generation",
    "Thermal discomfort",
    "PV Generation Vs AC excluded demand",
    "Monthly savings",
]


def generate_single_building_graphs(building):
    figures = {
        "PV Generation Vs AC excluded demand": line_plot(
            building.averaged_hourly_results,
            x_axis="hour",
            y_axes=["PV", "Demand"],
            names={"PV": "PV generation", "Demand": "Demand excluding AC"},
            x_title="Time of the day [h]",
            y_title="[kW]",
            title="PV generation and AC excluded demand",
        ),
        "Surplus PV generation": line_plot(
            building.averaged_hourly_results,
            x_axis="hour",
            y_axes=["Surplus_PV"],
            names={
                "Surplus_PV": "Surplus PV generation after meeting demand excluding AC"
            },
            x_title="Time of the day [h]",
            y_title="[kW]",
            title="Surplus PV generation",
        ),
        "Indoor temperature": line_plot(
            building.averaged_hourly_results,
            x_axis="hour",
            y_axes=["T_bs", "T_spc"],
            names={"T_bs": "Baseline", "T_spc": "Solar pre-cooling"},
            x_title="Time of the day [h]",
            y_title="Temperature [°C]",
            title="Indoor temperature trajectory",
        ),
        "AC demand": line_plot(
            building.averaged_hourly_results,
            x_axis="hour",
            y_axes=["E_bs", "E_spc"],
            names={"E_bs": "Baseline", "E_spc": "Solar pre-cooling"},
            x_title="Time of the day [h]",
            y_title="AC demand [kW]",
            title="Average AC demand profile",
        ),
        "Thermal discomfort": line_plot(
            building.averaged_hourly_results,
            x_axis="hour",
            y_axes=["W_bs", "W_spc"],
            names={"W_bs": "Baseline", "W_spc": "Solar pre-cooling"},
            x_title="Time of the day [h]",
            y_title="Thermal discomfort [°C.hour]",
            title="Thermal discomfort",
            plot_type="bar_chart",
        ),
        "Monthly savings": line_plot(
            building.monthly_saving,
            x_axis="month",
            y_axes=["Savings"],
            names={"Savings": "Monthly savings"},
            x_title="Month",
            y_title="Cost savings [$]",
            title="Monthly cost savings",
            plot_type="bar_chart",
        ),
    }

    single_building_graphs = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=figures["AC demand"]), md=5, sm=12),
                    dbc.Col(dcc.Graph(figure=figures["Monthly savings"]), md=5, sm=12),
                ]
            ),
            dbc.Row(
                [dbc.Col(dcc.Graph(figure=figures["Thermal discomfort"]), md=5, sm=12)]
            ),
            html.Br(),
        ],
    )

    return single_building_graphs


# @app.callback(
#     [
#         Output("Hidden-Div-single-figure", "children"),
#         Output("single-graph-dynamic-div", "children"),
#     ],
#     [Input("update-single-graph", "n_clicks"), Input("clear-single-graph", "n_clicks")],
#     [
#         State("single-building-figure-type", "value"),
#         State("select-single-building-name", "value"),
#         State("Hidden-Div-single-figure", "children"),
#         State("single-graph-dynamic-div", "children"),
#     ],
# )
# def update_single_building_figures(
#     n_clicks, clear_canvas, figure_type, building_name, hidden_div, dynamic_div_children
# ):
#
#     if n_clicks != hidden_div[0]:
#         with open("list_of_buildings.pkl", "rb") as inp:
#             list_of_buildings = pickle.load(inp)
#
#         for b in list_of_buildings:
#             if b.name == building_name:
#                 building = b
#         # fig = figures.dynamic_one_column_multiple_source(provider=provider,column=column,y_axis_title=y_axis_title)
#         figures = {
#             "PV Generation Vs AC excluded demand": line_plot(
#                 building.averaged_hourly_results,
#                 x_axis="hour",
#                 y_axes=["PV", "Demand"],
#                 names={"PV": "PV generation", "Demand": "Demand excluding AC"},
#                 x_title="Time of the day [h]",
#                 y_title="[kW]",
#                 title="PV generation and AC excluded demand_{}".format(building_name),
#             ),
#             "Surplus PV generation": line_plot(
#                 building.averaged_hourly_results,
#                 x_axis="hour",
#                 y_axes=["Surplus_PV"],
#                 names={
#                     "Surplus_PV": "Surplus PV generation after meeting demand excluding AC"
#                 },
#                 x_title="Time of the day [h]",
#                 y_title="[kW]",
#                 title="Surplus PV generation_{}".format(building_name),
#             ),
#             "Indoor temperature": line_plot(
#                 building.averaged_hourly_results,
#                 x_axis="hour",
#                 y_axes=["T_bs", "T_spc"],
#                 names={"T_bs": "Baseline", "T_spc": "Solar pre-cooling"},
#                 x_title="Time of the day [h]",
#                 y_title="Temperature [°C]",
#                 title="Indoor temperature trajectory_{}".format(building_name),
#             ),
#             "AC demand": line_plot(
#                 building.averaged_hourly_results,
#                 x_axis="hour",
#                 y_axes=["E_bs", "E_spc"],
#                 names={"E_bs": "Baseline", "E_spc": "Solar pre-cooling"},
#                 x_title="Time of the day [h]",
#                 y_title="AC demand [kW]",
#                 title="AC demand profile_{}".format(building_name),
#             ),
#             "Thermal discomfort": line_plot(
#                 building.averaged_hourly_results,
#                 x_axis="hour",
#                 y_axes=["W_bs", "W_spc"],
#                 names={"W_bs": "Baseline", "W_spc": "Solar pre-cooling"},
#                 x_title="Time of the day [h]",
#                 y_title="Thermal discomfort [°C.hour]",
#                 title="Thermal discomfort_{}".format(building_name),
#                 plot_type="bar_chart",
#             ),
#             "Monthly savings": line_plot(
#                 building.monthly_saving,
#                 x_axis="month",
#                 y_axes=["Savings"],
#                 names={"Savings": "Monthly savings"},
#                 x_title="Month",
#                 y_title="Cost savings [$]",
#                 title="Monthly cost savings_{}".format(building_name),
#                 plot_type="bar_chart",
#             ),
#         }
#
#         fig = figures[figure_type]
#
#         new_child = html.Div(
#             style={
#                 "outline": "thin lightgrey solid",
#                 "align": "center",
#                 # "padding": 5,
#                 # "marginLeft": "auto",
#                 # "marginRight": "auto",
#                 "display": "inline-block",
#             },  #
#             children=[
#                 dcc.Graph(
#                     id={"type": "dynamic-graph", "index": n_clicks},
#                     figure=fig,
#                     style={"width": "50vh", "margin": 0},
#                 ),
#             ],
#         )
#         dynamic_div_children.append(new_child)
#
#     elif clear_canvas != hidden_div[1]:
#         dynamic_div_children = []
#
#     hidden_div = [n_clicks, clear_canvas]
#
#     return hidden_div, dynamic_div_children


if __name__ == "__main__":
    generate_single_building_graphs()

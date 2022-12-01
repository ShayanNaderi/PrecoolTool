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


def generate_single_building_graphs():
    with open("list_of_buildings.pkl", "rb") as inp:
        list_of_buildings = pickle.load(inp)

    single_building_graphs = [
        dbc.CardHeader(html.H5("Results for a single building")),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-sankey",
                    children=[
                        dbc.Alert(
                            "Something's gone wrong! Give us a moment, but try loading this page again if problem persists.",
                            id="no-data-alert-sankey",
                            color="warning",
                            style={"display": "none"},
                        ),
                        html.Br(),
                        dbc.Select(
                            id="single-building-figure-type",
                            options=[
                                {"label": i, "value": i}
                                for i in single_building_available_figures
                            ],
                            value=single_building_available_figures[0],
                            style={
                                "width": "50%",
                                "margin-left": "0px",
                                "fontColor": "black",
                                "fontSize": 15,
                                "color": "black",
                            },
                        ),
                        dbc.Select(
                            id="select-single-building-name",
                            options=[
                                {"label": i.name, "value": i.name}
                                for i in list_of_buildings
                            ],
                            value=list_of_buildings[0].name,
                            style={
                                "width": "30%",
                                "margin-left": "0px",
                                "fontColor": "black",
                                "fontSize": 15,
                                "color": "black",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Add Figure",
                            color="danger",
                            id="update-single-graph",
                            n_clicks=0,
                            className="me-1",
                        ),
                        dbc.Button(
                            "Clear Canvas",
                            color="primary",
                            id="clear-single-graph",
                            n_clicks=0,
                            className="me-1",
                        ),
                        html.Div(
                            id="Hidden-Div-single-figure",
                            children=[0, 0],
                            style={"display": "none"},
                        ),
                        html.Div(
                            id="single-graph-dynamic-div",
                            children=[],
                            style={
                                "margin-top": "15px",
                                "margin-left": "0px",
                                "margin-right": "0px",
                            },
                        ),
                        html.Br(),
                    ],
                    type="default",
                )
            ],
            style={"marginTop": 0, "marginBottom": 0},
        ),
    ]
    return single_building_graphs


@app.callback(
    [
        Output("Hidden-Div-single-figure", "children"),
        Output("single-graph-dynamic-div", "children"),
    ],
    [Input("update-single-graph", "n_clicks"), Input("clear-single-graph", "n_clicks")],
    [
        State("single-building-figure-type", "value"),
        State("select-single-building-name", "value"),
        State("Hidden-Div-single-figure", "children"),
        State("single-graph-dynamic-div", "children"),
    ],
)
def update_single_building_figures(
    n_clicks, clear_canvas, figure_type, building_name, hidden_div, dynamic_div_children
):

    if n_clicks != hidden_div[0]:
        with open("list_of_buildings.pkl", "rb") as inp:
            list_of_buildings = pickle.load(inp)

        for b in list_of_buildings:
            if b.name == building_name:
                building = b
        # fig = figures.dynamic_one_column_multiple_source(provider=provider,column=column,y_axis_title=y_axis_title)
        figures = {
            "PV Generation Vs AC excluded demand": line_plot(
                building.averaged_hourly_results,
                x_axis="hour",
                y_axes=["PV", "Demand"],
                names={"PV": "PV generation", "Demand": "Demand excluding AC"},
                x_title="Time of the day [h]",
                y_title="[kW]",
                title="PV generation and AC excluded demand_{}".format(building_name),
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
                title="Surplus PV generation_{}".format(building_name),
            ),
            "Indoor temperature": line_plot(
                building.averaged_hourly_results,
                x_axis="hour",
                y_axes=["T_bs", "T_spc"],
                names={"T_bs": "Baseline", "T_spc": "Solar pre-cooling"},
                x_title="Time of the day [h]",
                y_title="Temperature [°C]",
                title="Indoor temperature trajectory_{}".format(building_name),
            ),
            "AC demand": line_plot(
                building.averaged_hourly_results,
                x_axis="hour",
                y_axes=["E_bs", "E_spc"],
                names={"E_bs": "Baseline", "E_spc": "Solar pre-cooling"},
                x_title="Time of the day [h]",
                y_title="AC demand [kW]",
                title="AC demand profile_{}".format(building_name),
            ),
            "Thermal discomfort": line_plot(
                building.averaged_hourly_results,
                x_axis="hour",
                y_axes=["W_bs", "W_spc"],
                names={"W_bs": "Baseline", "W_spc": "Solar pre-cooling"},
                x_title="Time of the day [h]",
                y_title="Thermal discomfort [°C.hour]",
                title="Thermal discomfort_{}".format(building_name),
                plot_type="bar_chart",
            ),
            "Monthly savings": line_plot(
                building.monthly_saving,
                x_axis="month",
                y_axes=["Savings"],
                names={"Savings": "Monthly savings"},
                x_title="Month",
                y_title="Cost savings [$]",
                title="Monthly cost savings_{}".format(building_name),
                plot_type="bar_chart",
            ),
        }

        fig = figures[figure_type]

        new_child = html.Div(
            style={
                "outline": "thin lightgrey solid",
                "align": "center",
                # "padding": 5,
                # "marginLeft": "auto",
                # "marginRight": "auto",
                "display": "inline-block",
            },  #
            children=[
                dcc.Graph(
                    id={"type": "dynamic-graph", "index": n_clicks},
                    figure=fig,
                    style={"width": "50vh", "margin": 0},
                ),
            ],
        )
        # if (
        #     (figure_type == "Thermal discomfort")
        #     & (building.averaged_hourly_results.W_bs.max() == 0)
        #     & (building.averaged_hourly_results.W_spc.max() == 0)
        # ):
        #     new_child = html.Div(
        #         style={
        #             "outline": "thin lightgrey solid",
        #             "align": "center",
        #             # "padding": 5,
        #             # "marginLeft": "auto",
        #             # "marginRight": "auto",
        #             "display": "inline-block",
        #         },  #
        #         children=[
        #             html.Div(
        #                 "No thermal discomfort reduction with the selected AC size and demand profile",
        #                 style={"width": "50vh", "margin": 0},
        #             )
        #         ],
        #     )

        dynamic_div_children.append(new_child)

    elif clear_canvas != hidden_div[1]:
        dynamic_div_children = []

    hidden_div = [n_clicks, clear_canvas]

    return hidden_div, dynamic_div_children


if __name__ == "__main__":
    generate_single_building_graphs()

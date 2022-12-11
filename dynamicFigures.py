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


def generate_card_deck_2(title, unit, value, image):
    cards = dbc.Card(
        [
            dbc.CardImg(
                src="assets/{}.png".format(image),
                top=True,
            ),
            dbc.CardBody(
                [
                    html.H4(title, className="card-title", style={"color": "white"}),
                    html.P(
                        "{}".format(round(value, 0)) + " " + unit,
                        className="card-text",
                        style={"color": "white"},
                    ),
                ]
            ),
        ],
        style={"width": "18rem"},
    )
    return cards


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
        "Import reduction": line_plot(
            building.averaged_hourly_results,
            x_axis="hour",
            y_axes=["Import_reduction"],
            names={
                "Import_reduction": "Baseline",
            },
            x_title="Time of the day [h]",
            y_title="[kWh]",
            title="Import reduction from the grid",
            plot_type="bar_chart",
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
                    dbc.Col(
                        generate_card_deck_2(
                            title="Savings",
                            unit="$/Summer",
                            value=building.total_cost_Savings,
                            image="money-bag",
                        ),
                        md=4,
                        sm=12,
                    ),
                    dbc.Col(
                        generate_card_deck_2(
                            title="Emission reduction",
                            unit="kg/Summer",
                            value=building.total_emission_reduction,
                            image="emissions",
                        ),
                        md=4,
                        sm=12,
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=figures["Import reduction"]), md=5, sm=12),
                    dbc.Col(
                        dcc.Graph(figure=figures["Thermal discomfort"]), md=5, sm=12
                    ),
                ]
            ),
            html.Br(),
        ],
    )

    return single_building_graphs


if __name__ == "__main__":
    generate_single_building_graphs()

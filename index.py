import dash_bootstrap_components as dbc
from dash import dcc, html

import callbacks  # noqa: F401
import callbacks_run  # noqa: F401
from app import app
from app_components import (
    AC_year_radio_item,
    PV_orientation_radio_item,
    construction_weight_radio_item,
    construction_weight_toast,
    demand_profile_radio_item,
    dwelling_type_radio_item,
    floor_area_radio_item,
    generate_select,
    location_radio_item,
    neutral_temp_select,
    occupancy_checklist,
    star_rating_radio_item,
    star_rating_toast,
    tariff_radio_checklist,
    tariff_table,
)

# VALID_USERNAME_PASSWORD_PAIRS = {
#     'hello': 'world'
# }sdfdsasas
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(
                            """
                # Solar Pre-cooling Potential Assessment Tool

                By [Shayan Naderi]
                (https://www.linkedin.com/in/shayan-naderi-461aa097/)
                """
                        )
                    ],
                    # width=True,
                    lg=8,
                    md=12,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="assets/UNSWLogo.png", alt="UNSW Logo", height="100px"
                        ),
                    ],
                    lg=2,
                    md=12,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="assets/CEEMLogo.png", alt="CEEM Logo", height="100px"
                        ),
                    ],
                    lg=2,
                    md=12,
                ),
            ],
            align="end",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            "Create thermal model of the building",
                            id="building-type-button",
                        ),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        location_radio_item,
                                        html.Hr(),
                                        star_rating_toast,
                                        html.Br(),
                                        html.P(
                                            "Select star rating and construction weight"
                                        ),
                                        star_rating_radio_item,
                                        html.Hr(),
                                        construction_weight_toast,
                                        html.Br(),
                                        construction_weight_radio_item,
                                        html.Hr(),
                                        dwelling_type_radio_item,
                                        html.Br(),
                                        floor_area_radio_item,
                                        html.Hr(),
                                        dbc.Button(
                                            id="create-thermal-model-button",
                                            children=["Create thermal model"],
                                            color="danger",
                                        ),
                                    ]
                                )
                            ),
                            id="building-type-collapse",
                            is_open=False,
                        ),
                        dbc.Spinner(
                            html.Div(id="thermal-model-creation-result", children=[]),
                        ),
                        html.Div(
                            id="coefficients-thermal-model",
                            style={"display": "None"},
                        ),
                        html.Div(
                            id="hidden-div-df-data-storage",
                            # children=["Hidden Div"],
                            style={"display": "None"},
                        ),
                        html.Div(id="store-building-instance"),
                        html.Hr(),
                        dbc.Button("Occupancy Pattern", id="occupancy-pattern-button"),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(occupancy_checklist)),
                            id="occupancy-pattern-collapse",
                            is_open=False,
                        ),
                        html.Hr(),
                        dbc.Button("Thermal Comfort", id="thermal-comfort-button"),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        neutral_temp_select,
                                        html.Br(),
                                    ]
                                )
                            ),
                            id="thermal-comfort-collapse",
                            is_open=False,
                        ),
                        html.Hr(),
                        dbc.Button("Electricity Tariff", id="tariff-button"),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        tariff_radio_checklist,
                                        html.Hr(),
                                        html.P(
                                            "In case of TOU, please enter hourly rates"
                                        ),
                                        tariff_table,
                                        html.Div(
                                            id="table-test",
                                        ),
                                    ]
                                )
                            ),
                            id="tariff-collapse",
                            is_open=False,
                        ),
                        html.Hr(),
                        dbc.Button("Demand Profile", id="demand-profile-button"),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        demand_profile_radio_item,
                                        html.Hr(),
                                        html.Div(
                                            id="upload-demand-data-div", children=[]
                                        ),
                                        html.Br(),
                                        html.Div(id="dump-selected-div"),
                                    ]
                                )
                            ),
                            id="demand-profile-collapse",
                            is_open=False,
                        ),
                        html.Hr(),
                        dbc.Button("Simulate PV performance", id="PV-AC-spec-button"),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        generate_select(
                                            id="AC-rated-capacity",
                                            title="AC rated thermal capacity kW:",
                                            min=2,
                                            max=70,
                                            value=15,
                                            step=1,
                                        ),
                                        html.P(
                                            "Select the model year of the air conditioning unit"
                                        ),
                                        AC_year_radio_item,
                                        html.Hr(),
                                        generate_select(
                                            id="PV-rated-capacity",
                                            title="PV system rated capacity kW:",
                                            min=2,
                                            max=70,
                                            value=5,
                                            step=1,
                                        ),
                                        generate_select(
                                            id="inverter-efficiency",
                                            title="Inverter efficiency %:",
                                            min=10,
                                            max=100,
                                            value=96,
                                            step=1,
                                        ),
                                        # html.Br(),
                                        PV_orientation_radio_item,
                                        dbc.Button(
                                            id="PV-simulation-button",
                                            children="Simulate PV generation",
                                            color="danger",
                                            style={"margin": "5px"},
                                        ),
                                    ]
                                )
                            ),
                            id="PV-AC-spec-collapse",
                            is_open=False,
                        ),
                        dbc.Spinner(
                            html.Div(id="PV-simulation-result", children=[]),
                        ),
                        html.Div(
                            id="PV-results-hidden-div",
                            style={"display": "None"},
                        ),
                        html.Hr(),
                        dcc.Markdown(id="selected-building"),
                        dbc.Button(
                            id="analyze-button",
                            children="Run solar pre-cooling!",
                            color="danger",
                            style={"margin": "5px"},
                        ),
                        dbc.Button(
                            id="cancel-button-id",
                            children="Cancel!",
                            color="danger",
                        ),
                        dbc.Spinner(html.Div(id="paragraph-id", children=[])),
                        html.Hr(),
                        dcc.Markdown("##### Aerodynamic Performance"),
                        dbc.Spinner(
                            html.P(id="text_output"),
                            color="primary",
                        ),
                    ],
                    lg=3,
                    md=12,
                ),
                dbc.Col(
                    [
                        html.Div(id="demand-selection-top-div"),
                        html.Div(id="selected-demand-div"),
                    ],
                    width=9,
                    align="start",
                ),
            ]
        ),
        html.Hr(),
        dcc.Markdown(
            """
            Solar pre-cooling potential assessment tool developed by
             [Shayan Naderi]
             (https://www.linkedin.com/in/shayan-naderi-461aa097/)
             , at [Collaboration on Energy and Environmental Markets
              (CEEM)](https://www.ceem.unsw.edu.au/)
        """
        ),
    ],
    fluid=True,
)


if __name__ == "__main__":
    # app.run_server(host='0.0.0.0',debug=False,port=8080,dev_tools_ui=False,dev_tools_props_check=False)#MapnaMind
    app.run_server(
        debug=True, dev_tools_ui=False, dev_tools_props_check=False
    )  # ShayanLaptop

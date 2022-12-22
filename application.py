import dash_bootstrap_components as dbc
from dash import dcc, html

import callbacks  # noqa: F401
import callbacks_run  # noqa: F401
from app import app, application
from app_components import (
    PV_orientation_radio_item,
    construction_weight_radio_item,
    demand_questions_radio_item,
    dwelling_type_radio_item,
    floor_area_radio_item,
    generate_select,
    location_radio_item,
    neutral_temp_select,
    occupancy_checklist,
    star_rating_radio_item,
    create_tariff_drpdwn,
)


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(
                            """
                # Solar Pre-cooling Potential Assessment Tool

                
                [Source code and user guide](https://github.com/ShayanNaderi/RESPCT) 

                """,
                            style={"color": "green"},
                        )
                    ],
                    # width=True,
                    lg=5,
                    sm=12,
                    md=12,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="assets/UNSWLogo.png", alt="UNSW Logo", height="100px"
                        ),
                    ],
                    lg=3,
                    sm=12,
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="assets/CEEMLogo.png", alt="CEEM Logo", height="100px"
                        ),
                    ],
                    lg=2,
                    md=3,
                    sm=12,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="assets/DGFI.gif", alt="DGFI Logo", height="100px"
                        ),
                    ],
                    lg=2,
                    md=3,
                    sm=12,
                ),
            ],
            align="end",
            style={"background-color": "white"},
        ),
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Solar pre-cooling potential in Australia",
                    active_tab_style={"textTransform": "uppercase"},
                    active_label_style={"color": "#FF0000"},
                    tab_id="summary-tab",
                ),
                dbc.Tab(
                    label="Simulation tool",
                    active_tab_style={"textTransform": "uppercase"},
                    active_label_style={"color": "#FF0000"},
                    tab_id="simulation-tab",
                ),
            ],
            id="tabs",
            active_tab="simulation-tab",
            style={"padding": "1rem" "1rem"},
        ),
        html.Br(),
        html.Div(id="Visible-content"),
        dcc.Markdown(
            """
            Solar pre-cooling potential assessment tool developed by
             [Shayan Naderi]
             (https://www.linkedin.com/in/shayan-naderi-461aa097/)
             , at [Collaboration on Energy and Environmental Markets
              (CEEM)](https://www.ceem.unsw.edu.au/)
        """
        ),
        dcc.Markdown(
            """
            This project is supported and funded buy 
             [UNSW Digital Grid Future Institute (DGFI)]
             (https://www.dgfi.unsw.edu.au/)
        """
        ),
    ],
    fluid=True,
)


if __name__ == "__main__":
    application.run(debug=True, port=8080)  # ShayanLaptop

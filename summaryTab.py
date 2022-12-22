from dash import html, dcc
import dash_bootstrap_components as dbc
import figures

figure_border_style = {
    "border-style": "solid",
    "border-color": "#ff4d4d",
    "border-width": "1px",
    "border-radius": "0.25rem",
}
home_distribution_pie = [
    html.Br(),
    dbc.CardHeader(
        html.H5(
            "Summary of the solar pre-cooling potential in Australia",
            style={"color": "white", "justify": "center"},
        )
    ),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-bigrams-transit",
                children=[
                    dbc.Alert(
                        "Something's gone wrong! Give us a moment, but try loading this page again if problem persists.",
                        id="no-data-alert-transit_comp",
                        color="warning",
                        style={"display": "none"},
                    ),
                    html.Div(
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.P(
                                            "Air conditioning is responsible for 40-50% of electricity demand "
                                            "in residential buildings  ",
                                            style={"color": "white", "margin": "10px"},
                                        ),
                                        html.P(
                                            "Buildings are responsible for 40-50% of world's energy consumption "
                                            "and carbon emissions ",
                                            style={"color": "white", "margin": "10px"},
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    dcc.Graph(
                                        id="sankey", figure=figures.create_sankey()
                                    ),
                                    lg=10,
                                    md=12,
                                    sm=12,
                                ),
                            ],
                            justify="center",
                        ),
                        style=figure_border_style,
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="pie-distribution-2022",
                                        figure=figures.create_pie_distribution(),
                                    ),
                                    style=figure_border_style,
                                ),
                                md=12,
                                lg=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="pie-distribution-2050",
                                        figure=figures.create_pie_distribution(
                                            year=2050
                                        ),
                                    ),
                                    style=figure_border_style,
                                ),
                                md=12,
                                lg=6,
                            ),
                        ],
                        justify="center",
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(figures.create_savings_table(), md=6, sm=12),
                            dbc.Col(
                                html.Div(figures.table_of_savings(field="saving")),
                                md=12,
                                lg=6,
                            ),
                        ],
                        justify="center",
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    figures.table_of_savings(field="emission"),
                                ),
                                md=12,
                                lg=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    figures.table_of_savings(field="discomfort"),
                                ),
                                md=12,
                                lg=6,
                            ),
                        ],
                        justify="center",
                    ),
                    html.Hr(),
                ],
            )
        ]
    ),
]


summaryTabContent = dbc.Row([dbc.Col(home_distribution_pie, md=12)])

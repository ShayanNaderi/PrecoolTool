from dash import dcc, html,Input, Output, State
import dash_bootstrap_components as dbc
from app import app
import pickle

from figures import line_plot
single_building_available_figures = ["Indoor temperature", "AC demand", "Surplus PV generation", "Thermal discomfort",
                     "PV Generation Vs AC excluded demand"]

def generate_single_building_graphs():
    with open('list_of_buildings.pkl', 'rb') as inp:
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
                                {"label": i, "value": i} for i in single_building_available_figures
                            ],
                            value=single_building_available_figures[0],
                            style={'width': "50%", 'margin-left': "0px", 'fontColor': 'black', 'fontSize': 15,
                                   'color': 'black'},
                        ),
                        dbc.Select(
                            id="select-single-building-name",
                            options=[
                                {"label": i.name, "value": i.name} for i in list_of_buildings
                            ],
                            value=list_of_buildings[0].name,
                            style={'width': "30%", 'margin-left': "0px", 'fontColor': 'black', 'fontSize': 15,
                                   'color': 'black','display': 'inline-block'},
                        ),
                        dbc.Button("Add Figure", color="danger", id='update-single-graph', n_clicks=0,
                                   className="me-1",),
                        dbc.Button("Clear Canvas", color="primary", id='clear-single-graph', n_clicks=0,
                                   className="me-1"),
                        html.Div(id='Hidden-Div-single-figure', children=[0, 0], style={'display': 'none'}),
                        html.Div(id='single-graph-dynamic-div', children=[],
                                 style={'margin-top': '15px', 'margin-left': '20px','margin-right': '20px'}),
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
    Output('Hidden-Div-single-figure', "children"),
    Output('single-graph-dynamic-div', 'children'),
        ],
    [Input('update-single-graph', 'n_clicks'),
    Input('clear-single-graph', 'n_clicks')],
    [State("single-building-figure-type", "value"),
     State("select-single-building-name", "value"),
     State('Hidden-Div-single-figure', "children"),
     State('single-graph-dynamic-div', 'children'),
     ]
)
def update_single_building_figures(n_clicks,clear_canvas,figure_type,building_name,hidden_div,dynamic_div_children):

    if n_clicks != hidden_div[0]:
        with open('list_of_buildings.pkl', 'rb') as inp:
            list_of_buildings = pickle.load(inp)

        for b in list_of_buildings:
            if b.name == building_name:
                building = b
        # fig = figures.dynamic_one_column_multiple_source(provider=provider,column=column,y_axis_title=y_axis_title)
        figures = {
        "PV Generation Vs AC excluded demand":line_plot(building.averaged_hourly_results, 'hour', ["PV", "Demand"],
                                  x_title="Time of the day [h]", y_title="[kW]",
                                  title="PV generation and AC excluded demand"),
        "Surplus PV generation":line_plot(building.averaged_hourly_results, 'hour', ["Surplus_PV"],
                                   x_title="Time of the day [h]", y_title="[kW]",
                                   title="Surplus PV generation"),
                         "Indoor temperature": line_plot(building.averaged_hourly_results, 'hour', ["T_bs", "T_spc"],
                                    x_title="Time of the day [h]", y_title="Temperature [°C]",
                                    title="Indoor temperature trajectory"),
            "AC demand":line_plot(building.averaged_hourly_results, 'hour', ["E_bs", "E_spc"],
                                  x_title="Time of the day [h]", y_title="AC demand [kW]", title="AC demand profile"),
            "Thermal discomfort":line_plot(building.averaged_hourly_results, 'hour',
                                           ["W_bs", "W_spc"], x_title="Time of the day [h]",
                                           y_title="Thermal discomfort [°C.hour]", title="Thermal discomfort",
                                           plot_type="bar_chart")
        }
        fig = figures[figure_type]
        new_child = html.Div(
            style={ 'outline': 'thin lightgrey solid', 'padding': 5,'marginLeft': 10, 'marginRight': 10,'display': 'inline-block',},#
            children=[
                dcc.Graph(
                    id={
                        'type': 'dynamic-graph',
                        'index': n_clicks
                    },
                    figure=fig,
                    style={'width': '80vh',"margin":0}
                ),
            ]
        )
        dynamic_div_children.append(new_child)

    elif clear_canvas != hidden_div[1]:
        dynamic_div_children = []

    hidden_div = [n_clicks,clear_canvas]

    return hidden_div,dynamic_div_children

if __name__ == "__main__":
    generate_single_building_graphs()

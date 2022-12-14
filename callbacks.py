import json

import pandas as pd
from dash import Input, Output, State, html

from app import app
from app_components import (
    create_select_demand_profile_fig,
    create_selected_profile_fig,
    simulation_tab_content,
)
from summaryTab import summaryTabContent


@app.callback(Output("Visible-content", "children"), Input("tabs", "active_tab"))
def switch_tab(tab):
    if tab == "summary-tab":
        return summaryTabContent
    elif tab == "simulation-tab":
        return simulation_tab_content


# Callback to make construction weight menu expand
@app.callback(
    Output("construction-weight-collapse", "is_open"),
    [Input("construction-weight-button", "n_clicks")],
    [State("construction-weight-collapse", "is_open")],
)
def toggle_construction_weight_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to make demand profile menu expand
@app.callback(
    Output("thermal-comfort-collapse", "is_open"),
    [Input("thermal-comfort-button", "n_clicks")],
    [State("thermal-comfort-collapse", "is_open")],
)
def toggle_comfort_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to make star rating menu expand
@app.callback(
    Output("building-type-collapse", "is_open"),
    [Input("building-type-button", "n_clicks")],
    [State("building-type-collapse", "is_open")],
)
def toggle_star_rating_collapse(n_clicks, is_open):

    if n_clicks:
        return not is_open
    return is_open


# Callback to make occupancy patterns menu expand
@app.callback(
    Output("occupancy-pattern-collapse", "is_open"),
    [Input("occupancy-pattern-button", "n_clicks")],
    [State("occupancy-pattern-collapse", "is_open")],
)
def toggle_occupancy_pattern_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to make tariff menu expand
@app.callback(
    Output("tariff-collapse", "is_open"),
    [Input("tariff-button", "n_clicks")],
    [State("tariff-collapse", "is_open")],
)
def toggle_tariff_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to make demand profile menu expand
@app.callback(
    Output("demand-profile-collapse", "is_open"),
    [Input("demand-profile-button", "n_clicks")],
    [State("demand-profile-collapse", "is_open")],
)
def toggle_demand_profile_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to make demand profile menu expand
@app.callback(
    Output("PV-AC-spec-collapse", "is_open"),
    [Input("PV-AC-spec-button", "n_clicks")],
    [State("PV-AC-spec-collapse", "is_open")],
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    [Output("floor-area-radio", "options"), Output("floor-area-radio", "value")],
    [Input("dwelling-type-radio", "value")],
)
def floor_area_radio_item_update(dwelling_type):
    options_dictionary = {
        "Apartment": [
            {
                "label": "Small (1-bed, 50-75 m2 floor area)",
                "value": "Small",
            },
            {"label": "Medium (3-bed, 80-105 m2 floor area)", "value": "Medium"},
            {"label": "Large (3-bed, 110-130 m2 floor area)", "value": "Large"},
        ],
        "House": [
            {
                "label": "Small (3-bed, 90-110 m2 floor area",
                "value": "Small",
            },
            {"label": "Medium (4-bed, 140-160 m2 floor area)", "value": "Medium"},
            {"label": "Large (5-bed, 170-300 m2 floor area)", "value": "Large"},
        ],
    }

    return options_dictionary[dwelling_type], "Small"


@app.callback(
    Output("demand-selection-top-div", "children"),
    [
        # Input("demand-profile-availability-radio", "value"),
        Input("demand-profile-collapse", "is_open"),
        Input("net-demand-questions", "value"),
    ],
)
def update_graphs(
    # availability,
    is_open,
    answer_cluster_question,
):
    cluster_dic = {
        "no-surplus": [4],
        "surpluss-available": [2],
        "modest-surplus": [1],
    }
    cluster = cluster_dic[answer_cluster_question]
    if is_open == True:
        df = pd.read_csv("Data/average_demand_and_clusters_for_demand_selection.csv")
        df = df[df["Cluster"].isin(cluster)]
        if (cluster == [1]) | (cluster == [2]):
            unique_ids = df["site_ID"].unique()
            unique_ids = unique_ids[:40]
            df = df[df["site_ID"].isin(unique_ids)]
        fig = create_select_demand_profile_fig(
            df,
            title="Click on the most similar net demand profile to your average hourly net demand profile",
        )
        return fig

    elif is_open == False:
        return []


@app.callback(
    # [
    # Output("dump-selected-div", "children"),
    Output("selected-demand-div", "children"),
    Output("selected-demand-div-id", "children"),
    # ],
    [
        Input("select-demand-profile-fig", "clickData"),
        Input("demand-profile-collapse", "is_open"),
    ],
    [
        State("select-demand-profile-fig", "selectedData"),
        State("net-demand-questions", "value"),
        # State("demand-profile-availability-radio", "value"),
    ],
)
def display_selected_data(
    clickData,
    is_open,
    selectedData,
    asnwer_net_demand,
):
    if clickData is not None:
        # if clickData["points"][0]["customdata"][0] is not None:

        site_id = clickData["points"][0]["customdata"][0]
        df = pd.read_csv("Data/average_demand_and_clusters_for_demand_selection.csv")
        df = df[df["site_ID"] == site_id]
        fig = create_selected_profile_fig(df)

        if is_open == True:
            return fig, site_id

        elif is_open == False:
            return [], site_id


# # Upload Data component
# @app.callback(
#     # [
#     # Output("dump-selected-div", "children"),
#     # # Output("selected-demand-div", "children"),
#         Output("selected-demand-div-id", "children"),
#     # ],
#         Input('upload-demand-data', 'filename'),
#         [State("demand-profile-collapse", "is_open"),
#         State("demand-profile-availability-radio", "value"),
#         State('upload-demand-data', 'contents'),
#         State('upload-demand-data', 'last_modified')]
# )
# def upload_data(upload_content_list,is_open, availability,upload_name,last_modified):
#     if upload_content_list is not None:
#         df = pd.read_csv("Data/average_demand_and_clusters_for_demand_selection.csv")
#         # df = df[df["site_ID"] == site_id]
#         fig = create_selected_profile_fig(df)
#
#         if (is_open == True) & (availability == "available"):
#             return ["Hi"],
#
#         elif (is_open == False) & (availability == "available"):
#             # print(file_name,content)
#             return [],


@app.callback(
    Output("table-test", "children"),
    Input("tariff-table", "data"),
)
def update_tables(data):
    """This function return the updated tariff tables when the user edits it"""
    tariff_df = pd.DataFrame.from_records(data)
    tariff_df.rename(columns={"Rate-weekdays": "Tariff"}, inplace=True)
    # print(tariff_df.columns)
    return data


if __name__ == "__main__":
    app.run_server(debug=False)

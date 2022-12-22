from dash import html, dcc, dash_table
import dash.dash_table.FormatTemplate as FormatTemplate
from dash.dash_table.Format import Sign
from collections import OrderedDict
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go


def generate_select(id, title, min=0, max=300, step=1, value=30):
    content = html.Div(
        [
            dbc.InputGroup(
                [
                    dbc.InputGroupText(title),
                    dbc.Input(
                        placeholder="Amount",
                        value=value,
                        step=step,
                        type="number",
                        id=id,
                        min=min,
                        max=max,
                    ),
                    # dbc.InputGroupText(".00"),
                ],
                className="mb-3",
            ),
        ]
    )
    return content


star_rating_radio_item = html.Div(
    dbc.RadioItems(
        id="building-type-radio",
        options=[
            {"label": "1-4 star", "value": "2star"},
            {"label": "4-6 star", "value": "6star"},
            {"label": "+6 star", "value": "8star"},
        ],
        value="6star",
        inline=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    ),
)

construction_weight_radio_item = html.Div(
    dbc.RadioItems(
        id="construction-weight-radio",
        options=[
            {"label": "Light (Timber clad, Fibre cement)", "value": "Light"},
            {"label": "Medium (Brick veneer)", "value": "Medium"},
            {"label": "Heavy (Cavity brick)", "value": "Heavy"},
        ],
        value="Light",
        inline=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    ),
)


dwelling_type_radio_item = html.Div(
    [
        html.P("Select dwelling type and its floor area"),
        dbc.RadioItems(
            id="dwelling-type-radio",
            options=[
                {"label": "Apartment", "value": "Apartment"},
                {"label": "House", "value": "House"},
            ],
            value="Apartment",
            inline=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ]
)
floor_area_radio_item = html.Div(
    [
        html.P("Select the closest floor area"),
        dbc.RadioItems(
            id="floor-area-radio",
            # options=[
            #     {"label": "Light", "value": "small"},
            #     {"label": "Medium", "value": "medium"},
            #     {"label": "Heavy", "value": "large"},
            # ],
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ]
)
location_radio_item = html.Div(
    [
        html.P("Select a city"),
        dbc.RadioItems(
            id="location-radio",
            options=[
                {"label": "Adelaide", "value": "Adelaide"},
                {"label": "Brisbane", "value": "Brisbane"},
                {"label": "Melbourne", "value": "Melbourne"},
                {"label": "Sydney", "value": "Sydney"},
            ],
            value="Sydney",
            inline=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ]
)

neutral_temp_select = html.Div(
    [
        html.P("Preferred indoor temperature during the occupied hours"),
        generate_select(
            "neutral-temp",
            "Desired indoor temperature °C:",
            value=23,
            min=18,
            max=30,
            step=0.5,
        ),
        html.Hr(),
        html.P(
            "Acceptable deviation from the desired temperature during occupied hours"
        ),
        generate_select(
            "deviation-up-temp",
            "Upper limit °C:",
            value=24,
            min=15,
            max=35,
            step=0.25,
        ),
        generate_select(
            "deviation-low-temp",
            "Lower limit °C:",
            value=18,
            min=14,
            max=30,
            step=0.25,
        ),
    ]
)


star_rating_toast = html.Div(
    [
        dbc.Button(
            "Star Rating guide",
            id="star-rating-toggle",
            color="info",
            n_clicks=0,
        ),
        dbc.Toast(
            "2-star: Building works (construciton, renovation) before 2006 did not have any"
            "compulsary standard in terms of annual thermal energy demand. Their star rating is mostly around 2-star \n"
            "After 2006, meeting 6-star standards became mandatory for all building works. So if "
            "the building was built or renovated after 2006, it should be 6-star"
            "8-star:",
            id="star-rating-toast",
            header="How to select star rating?",
            is_open=False,
            dismissable=True,
            icon="info",
            # top: 66 positions the toast below the navbar
            style={
                "font": {"size": 16},
                "position": "fixed",
                "top": 60,
                "left": 10,
                "width": 450,
                "z-index": 1,
            },
        ),
    ]
)

construction_weight_toast = html.Div(
    [
        dbc.Button(
            "Construction weight guide",
            id="construction-weight-toggle",
            color="info",
            n_clicks=0,
        ),
        dbc.Toast(
            "2-star: Building works (construciton, renovation) before 2006 did not have any"
            "compulsary standard in terms of annual thermal energy demand. Their star rating is mostly around 2-star \n"
            "After 2006, meeting 6-star standards became mandatory for all building works. So if "
            "the building was built or renovated after 2006, it should be 6-star"
            "8-star:",
            id="construction-weight-toast",
            header="How to select star rating?",
            is_open=False,
            dismissable=True,
            icon="info",
            # top: 66 positions the toast below the navbar
            style={
                "font": {"size": 16},
                "position": "fixed",
                "top": 60,
                "left": 10,
                "width": 450,
                "z-index": 1,
            },
        ),
    ]
)
AC_year_radio_item = html.Div(
    dbc.RadioItems(
        id="AC-year-radio",
        options=[
            {"label": "Before 2006", "value": 2.75},
            {"label": "2006 - 2010", "value": 3.25},
            {"label": "2010 - 2016", "value": 3.75},
            {"label": "After 2016", "value": 4.0},
        ],
        value=3.75,
        inline=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    ),
)

occupancy_checklist = html.Div(
    [
        html.Div("Please select typical occopied periods during weekdays"),
        html.Br(),
        dbc.Checklist(
            id="weekdays-occupancy-checklist",
            options=[
                {"label": "7 am - 10 am", "value": 1},
                {"label": "10 am - 2 pm", "value": 2},
                {"label": "2 pm - 6 pm", "value": 3},
                {"label": "6 pm - midnight", "value": 4},
                {"label": "Overnight", "value": 5},
            ],
            value=[4, 5],
            inline=True,
            label_checked_style={"color": "red"},
            input_checked_style={
                "backgroundColor": "#fa7268",
                "borderColor": "#ea6258",
            },
        ),
    ]
)


tariff_radio_checklist = html.Div(
    [
        dbc.RadioItems(
            id="tariff-structure",
            options=[
                {"label": "Flat Rate ", "value": "flat-rate"},
                {"label": "Time of Use", "value": "TOU"},
            ],
            inline=True,
            value="flat-rate",
        ),
        html.Br(),
        generate_select("flat-tariff-rate", "Flat rate c/kWh:"),
        html.Br(),
        generate_select(
            "FiT", "Solar Feed-in-Tariff c/kWh:", min=0, max=30, step=1, value=6
        ),
    ]
)

df_typing_formatting = pd.DataFrame(
    OrderedDict(
        [
            (
                "Hour",
                [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                ],
            ),
            (
                "Rate-weekdays",
                [
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                ],
            ),
            (
                "Rate-weekends",
                [
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                    30,
                ],
            ),
        ]
    )
)

tariff_table = html.Div(
    [
        dash_table.DataTable(
            id="tariff-table",
            data=df_typing_formatting.to_dict("records"),
            columns=[
                {"id": "Hour", "name": "Hour", "type": "text", "editable": False},
                {
                    "id": "Rate-weekdays",
                    "name": "Weekdays Rate (c/kWh)",
                    "type": "numeric",
                    "editable": True,
                },
                {
                    "id": "Rate-weekends",
                    "name": "Weekends Rate (c/kWh)",
                    "type": "numeric",
                    "editable": True,
                },
            ],
            style_cell={
                "backgroundColor": "rgb(50, 50, 50)",
                "color": "white",
                "textAlign": "left",
                "fontSize": 18,
                "font-family": "Calibri",
                "height": "auto",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
        )
    ]
)


demand_profile_radio_item = html.Div(
    [
        dbc.RadioItems(
            id="demand-profile-availability-radio",
            options=[
                {"label": "Upload data", "value": "available"},
                {"label": "Using the database", "value": "unavailable"},
            ],
            value="available",
            inline=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ]
)


def create_upload_data(id):

    upload_data = html.Div(
        [
            dcc.Upload(
                id=id,
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                # Allow multiple files to be uploaded
                multiple=False,
            ),
        ],
    )
    return upload_data


demand_questions_radio_item = html.Div(
    [
        dbc.RadioItems(
            id="net-demand-questions",
            options=[
                {
                    "label": "Other than AC, other appliance usages are shifted to daytime and almost all PV generation is consumed",
                    "value": "no-surplus",
                },
                {
                    "label": "There are usually surplus PV generation after meeting household's gross demand",
                    "value": "surpluss-available",
                },
                {
                    "label": "Surplus PV generation is available but is not significant",
                    "value": "modest-surplus",
                },
            ],
            value="surpluss-available",
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ]
)


def create_select_demand_profile_fig(df, title, selected=False):
    if selected == False:
        fig = px.line(
            df, x="Time", y="Values", color="site_ID", custom_data=["site_ID"]
        )
    elif selected == True:
        fig = px.line(df, x="Time", y="Values", custom_data=["site_ID"])
    fig.update_layout(
        clickmode="event+select",
        showlegend=False,
        title=title,
    ),
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
        },
        font=dict(family="Calibri", size=16, color="white"),
    ),
    fig.update_yaxes(
        title_text="Average AC excluded demand [kW]",
        showline=True,
        showgrid=False,
        linecolor="black",
        # gridcolor="black",
    )
    fig.update_xaxes(
        showline=True,
        showgrid=False,
        linecolor="black",
        title_text="Time of the day [h]",
    )
    # margin=dict(l=0, r=0, t=0, b=0)
    graph = dcc.Graph(id="select-demand-profile-fig", figure=fig)
    return graph


def create_selected_profile_fig(df):
    fig = px.line(df, x="Time", y="Values", color="site_ID", custom_data=["site_ID"])
    fig.update_layout(
        clickmode="event+select",
        showlegend=False,
        title="You selected the following demand profile",
    ),
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
        },
        font=dict(family="Calibri", size=16, color="white"),
    ),
    fig.update_yaxes(
        title_text="Average AC excluded demand [kW]",
        showline=True,
        showgrid=False,
        linecolor="black",
        # gridcolor="black",
    )
    fig.update_xaxes(
        showline=True,
        showgrid=False,
        linecolor="black",
        title_text="Time of the day [h]",
    )
    # margin=dict(l=0, r=0, t=0, b=0)
    graph = dcc.Graph(id="selected-demand-profile-fig", figure=fig)
    return graph


def make_progress_graph(progress, total):
    progress_graph = (
        go.Figure(data=[go.Bar(x=[progress])])
        .update_xaxes(range=[0, total])
        .update_yaxes(
            showticklabels=False,
        )
        .update_layout(height=100, margin=dict(t=20, b=40))
    )
    return progress_graph


PV_orientation_radio_item = html.Div(
    [
        html.P("Select the orientation of the PV system"),
        dbc.RadioItems(
            id="PV-orientation-radio",
            options=[
                {"label": "North", "value": "North"},
                {"label": "Northeast", "value": "Northeast"},
                {"label": "East", "value": "East"},
                {"label": "Southeast", "value": "Southeast"},
                {"label": "South", "value": "South"},
                {"label": "Southwest", "value": "Southwest"},
                {"label": "West", "value": "West"},
                {"label": "Northwest", "value": "Northwest"},
            ],
            value="North",
            inline=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ]
)


def create_tariff_drpdwn():
    filtered_tariffs = []

    json = pd.read_json("RetailTariffs.json")
    tariff_dicts = json.Tariffs[0]
    for i in tariff_dicts:
        if "Year" in i.keys():
            if (i["CustomerType"] == "Residential") & (
                i["State"] in ["VIC", "QLD", "NSW", "SA", "All"]
            ):
                filtered_tariffs.append(i)
    tariff_drpdwn = dbc.Select(
        id="dropdown-tariff",
        required=True,
        options=[
            {"label": i["Name"], "value": i["Tariff ID"]} for i in filtered_tariffs
        ],
        value=filtered_tariffs[0]["Tariff ID"],
    )
    return tariff_drpdwn


simulation_tab_content = (
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Button(
                        "Create thermal model of the building",
                        style={"width": "70%"},
                        id="building-type-button",
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    location_radio_item,
                                    html.Hr(),
                                    html.P("Select star rating"),
                                    star_rating_radio_item,
                                    html.Hr(),
                                    html.P("Select construction weight (material)"),
                                    construction_weight_radio_item,
                                    html.Hr(),
                                    dwelling_type_radio_item,
                                    html.Hr(),
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
                        style={"display": "None"},
                    ),
                    html.Div(id="store-building-instance"),
                    html.Hr(),
                    dbc.Button(
                        "Occupancy Pattern",
                        style={"width": "70%"},
                        id="occupancy-pattern-button",
                    ),
                    dbc.Collapse(
                        dbc.Card(dbc.CardBody(occupancy_checklist)),
                        id="occupancy-pattern-collapse",
                        is_open=False,
                    ),
                    html.Hr(),
                    dbc.Button(
                        "Ideal indoor temperature",
                        style={"width": "70%"},
                        id="thermal-comfort-button",
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    neutral_temp_select,
                                ]
                            )
                        ),
                        id="thermal-comfort-collapse",
                        is_open=False,
                    ),
                    html.Hr(),
                    dbc.Button(
                        "Electricity Tariff",
                        style={"width": "70%"},
                        id="tariff-button",
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    create_tariff_drpdwn(),
                                ]
                            )
                        ),
                        id="tariff-collapse",
                        is_open=False,
                    ),
                    html.Hr(),
                    dbc.Button(
                        "Demand Profile",
                        style={"width": "70%"},
                        id="demand-profile-button",
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    demand_questions_radio_item,
                                ]
                            )
                        ),
                        id="demand-profile-collapse",
                        is_open=False,
                    ),
                    html.Hr(),
                    dbc.Button(
                        "AC and PV technical specifications",
                        id="PV-AC-spec-button",
                        style={"width": "70%"},
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    generate_select(
                                        id="AC-rated-capacity",
                                        title="AC rated electrical capacity kW:",
                                        min=2,
                                        max=70,
                                        value=6,
                                        step=1,
                                    ),
                                    html.Hr(),
                                    generate_select(
                                        id="PV-rated-capacity",
                                        title="PV system rated capacity kW:",
                                        min=2,
                                        max=70,
                                        value=6,
                                        step=0.5,
                                    ),
                                    PV_orientation_radio_item,
                                    dbc.Button(
                                        id="PV-simulation-button",
                                        children="Simulate PV generation",
                                        color="danger",
                                        style={"margin": "5px", "width": "70%"},
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
                        id="run-button",
                        children="Run solar pre-cooling!",
                        color="success",
                        n_clicks=0,
                        style={"margin": "5px", "width": "70%"},
                    ),
                    # dbc.Button(
                    #     id="cancel-button-id",
                    #     children="Cancel!",
                    #     color="danger",
                    #     style={"width": "30%"},
                    # ),
                    dbc.Spinner(html.Div(id="paragraph-id", children=[])),
                    html.Hr(),
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
                    html.Div(id="selected-demand-div-id", style={"display": "None"}),
                    html.Div(
                        id="run-simulation-hidden-div",
                        children=[0],
                        style={"display": "None"},
                    ),
                    html.Div(
                        id="list-of-buildings-hidden-div",
                        children=[],
                        style={"display": "None"},
                    ),
                    html.Div(id="single-building-results-div"),
                ],
                width=9,
                align="start",
            ),
        ]
    ),
)

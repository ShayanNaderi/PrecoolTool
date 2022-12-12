import pandas as pd
import plotly
from dash import html, dash_table
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import dash_bootstrap_components as dbc

font_color = "white"
simple_template = dict(
    layout=go.Layout(
        title_font=dict(family="Rockwell", size=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Calibri", size=15, color=font_color),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="grey"),
    )
)


def line_plot(
    df,
    x_axis,
    y_axes,
    names,
    y_title,
    x_title,
    title,
    plot_type="line_plot",
):

    fig = go.Figure()
    for y in y_axes:
        if plot_type == "line_plot":
            fig.add_trace(go.Scatter(x=df[x_axis], y=df[y], name=names[y]))
        elif plot_type == "bar_chart":
            fig.add_trace(go.Bar(x=df[x_axis], y=df[y], name=names[y]))

    fig.update_layout(template=simple_template)
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title, height=400)
    return fig


def create_pie_distribution(year=2022):
    df = pd.read_excel("Data/Overview of the savings.xlsx")

    fig = px.sunburst(
        df,
        path=["Star Rating", "Construction weight"],
        values="Percentage of buildings {}".format(year),
        color="Star Rating",
    )
    fig.update_traces(textinfo="label+percent entry")
    fig.update_layout(
        template=simple_template,
        title="Distribution of different building types in {}".format(year),
    )

    return fig


def table_of_savings(field, year=2022):
    df = pd.read_excel("Data/Overview of the savings.xlsx")
    if field == "saving":
        df.sort_values(by="Maximum savings", inplace=True, ascending=False)
        df["% of households"] = df["Percentage of buildings {}".format(year)].cumsum()
        df["% of households"] = df["% of households"].round(1)
        df.rename(
            columns={"Maximum savings": "Potential cost savings ($/Summer)"},
            inplace=True,
        )
        df = df[["% of households", "Potential cost savings ($/Summer)"]]
        # df = df.iloc[:-1]

    elif field == "discomfort":
        df = pd.read_excel("Data/Overview of the savings.xlsx")
        df.sort_values(by="Discomfort reduction", inplace=True, ascending=False)
        df["% of households"] = df["Percentage of buildings {}".format(year)].cumsum()
        df["% of households"] = df["% of households"].round(1)
        df.rename(
            columns={
                "Discomfort reduction": "Daily discomfort reduction (degree.hour)"
            },
            inplace=True,
        )
        df = df[["% of households", "Daily discomfort reduction (degree.hour)"]]
        # df = df.iloc[:-1]

    elif field == "emission":
        df = pd.read_excel("Data/Overview of the savings.xlsx")
        df.sort_values(by="Emission Reduction", inplace=True, ascending=False)
        df["% of households"] = df["Percentage of buildings {}".format(year)].cumsum()
        df["% of households"] = df["% of households"].round(1)
        df.rename(
            columns={"Emission Reduction": "Emission Reduction (kg/summer)"},
            inplace=True,
        )
        df = df[["% of households", "Emission Reduction (kg/summer)"]]
        # df = df.iloc[:-1]
    # fig = ff.create_table(df)
    fig = html.Div(
        [
            dash_table.DataTable(
                data=df.to_dict("records"),
                # sort_action="None",
                columns=[{"name": i, "id": i} for i in df.columns],
                style_as_list_view=False,
                style_header={
                    "backgroundColor": "rgb(30, 30, 30)",
                    "fontWeight": "bold",
                    "border": "1px solid grey",
                    # 'textAlign': 'left',
                },
                style_data={
                    "border": "1px solid grey",
                    "whiteSpace": "normal",
                    "height": "auto",
                },
                style_cell={
                    "textAlign": "center",
                    "padding": "5px",
                    "backgroundColor": "rgba(0, 0, 0, 0)",
                    "color": "white",
                },
                # style_data_conditional=styles,
            ),
        ]
    )
    return fig


def create_sankey():
    import pandas
    import plotly

    import plotly.graph_objects as go

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=50,
                    thickness=5,
                    line=dict(color="black", width=0.1),
                    label=[
                        "Rooftop PV",
                        "Grid",
                        "Electricity supplied",
                        "Temperature sensitive",
                        "Temperature insensitive",
                        "Air conditioning",
                        "Hot water",
                        "Lighting",
                        "Cooking",
                        "TV and computers",
                        "Washer and dryer",
                        "Refrigerator",
                        "Other electrical loads",
                    ],
                    color="brown",
                ),
                link=dict(
                    # source = [0, 1, 2, 2,2,2,2,2,2,2], # indices correspond to labels, eg A1, A2, A1, B1, ...
                    # target = [2, 2, 3, 4,5,6,7,8,9,10],
                    # value = [7, 5, 4, 2,1,1,1,1,1,1,1],    #
                    source=[
                        0,
                        1,
                        2,
                        2,
                        3,
                        4,
                        4,
                        4,
                        4,
                        4,
                        4,
                        4,
                    ],  # indices correspond to labels, eg A1, A2, A1, B1, ...
                    target=[2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    value=[7, 5, 4, 8, 4, 2, 1, 1, 1, 1, 1, 1, 1],
                    color=[
                        "lightgreen",
                        "black",
                        "red",
                        "lightblue",
                        "red",
                        "purple",
                        "pink",
                        "blue",
                        "orange",
                        "olive",
                        "violet",
                        "yellowgreen",
                    ],
                ),
            )
        ]
    )
    # fig.update_layout(
    #     height=700, width=1300, font=dict(family="Calibri", size=25, color="black")
    # )
    # fig.update_layout(font=dict(family="Calibri", size=23, color="white"))
    fig.update_layout(template=simple_template)
    # fig.update_layout(margin=0)

    return fig


def discrete_background_color_bins(df, n_bins=5, columns="all"):
    import colorlover

    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == "all":
        if "id" in df:
            df_numeric_columns = df.select_dtypes("number").drop(["id"], axis=1)
        else:
            df_numeric_columns = df.select_dtypes("number")
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [((df_max - df_min) * i) + df_min for i in bounds]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]["seq"]["YlGn"][i - 1]
        color = "white" if i > len(bounds) / 2.0 else "inherit"

        for column in df_numeric_columns:
            styles.append(
                {
                    "if": {
                        "filter_query": (
                            "{{{column}}} >= {min_bound}"
                            + (
                                " && {{{column}}} < {max_bound}"
                                if (i < len(bounds) - 1)
                                else ""
                            )
                        ).format(
                            column=column, min_bound=min_bound, max_bound=max_bound
                        ),
                        "column_id": column,
                    },
                    "backgroundColor": backgroundColor,
                    "color": color,
                }
            )
        legend.append(
            html.Div(
                style={"display": "inline-block", "width": "60px"},
                children=[
                    html.Div(
                        style={
                            "backgroundColor": backgroundColor,
                            "borderLeft": "1px rgb(50, 50, 50) solid",
                            "height": "10px",
                        }
                    ),
                    html.Small(round(min_bound, 2), style={"paddingLeft": "2px"}),
                ],
            )
        )

    return (styles, html.Div(legend, style={"padding": "5px 0 5px 0"}))


def create_savings_table():
    df = pd.read_excel("Data/Savings_80_locations_naximum.xlsx", sheet_name="max")
    df["Cost savings ($/Summer)"] = df["Cost savings ($/Summer)"].astype(int)
    (styles, legend) = discrete_background_color_bins(df)

    table = html.Div(
        dash_table.DataTable(
            data=df.to_dict("records"),
            # sort_action="native",
            columns=[{"name": i, "id": i} for i in df.columns],
            style_as_list_view=False,
            style_header={
                "backgroundColor": "rgb(30, 30, 30)",
                "fontWeight": "bold",
                "border": "1px solid grey",
                # 'textAlign': 'left',
            },
            style_data={
                "border": "1px solid grey",
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_cell={
                "textAlign": "center",
                "padding": "5px",
                "backgroundColor": "rgba(0, 0, 0, 0)",
                "color": "white",
            },
            # style_data_conditional=styles,
        ),
    )

    return table


if __name__ == "__main__":
    # df = pd.read_csv("ready_df.csv")
    # df["Time"] = df["Time"].astype(str)
    # df["PV"] = df["PV"] / 1000
    # fig = line_plot(
    #     df,
    #     "Time",
    #     ["PV", "Demand"],
    #     "[KW]",
    #     "Time [h]",
    #     "PV generation and AC excluded demand",
    #     plot_type="line_plot",
    # )
    # # fig = line_plot(df,'hour',["E_bs","Q_spc"])
    # fig.show()
    from dash import Dash

    app = Dash()

    def generate_card_deck_2():

        cards = dbc.Card(
            [
                dbc.CardImg(src="assets/money-bag.png", top=True),
                dbc.CardBody(
                    [
                        html.H4("Savings", className="card-title"),
                        html.P(
                            "{} $/Summer",
                            className="card-text",
                        ),
                    ]
                ),
            ],
            style={"width": "18rem"},
        )
        return cards

    app.layout = html.Div(dbc.Row(dbc.Col(generate_card_deck_2(), md=3)))
    app.run_server(debug=True)

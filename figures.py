import pandas as pd
import plotly
import plotly.graph_objects as go
font_color = "black"
simple_template = dict(
layout=go.Layout(title_font=dict(family="Rockwell", size=24),
                     plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                     font=dict(
                         family="Calibri",
                         size=16,
                         color=font_color
                     ),
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                     ),
                 xaxis=dict(showgrid = False),
                 yaxis=dict(gridcolor="grey")
                 ))

def line_plot(df,x_axis,y_axes,y_title,x_title,title,plot_type='line_plot'):

    fig = go.Figure()
    print("lineplot started")
    for y in y_axes:
        if plot_type == "line_plot":
            fig.add_trace(go.Scatter(x=df[x_axis], y=df[y], name=y))
        elif plot_type == "bar_chart":
            fig.add_trace(go.Bar(x=df[x_axis], y=df[y], name=y))

    fig.update_layout(template = simple_template)
    fig.update_layout(title=title,
                         xaxis_title=x_title,
                         yaxis_title=y_title,)
    print("lineplot OK")
    return fig


if __name__ == "__main__":
    df= pd.read_csv("ready_df.csv")
    df["Time"] = df["Time"].astype(str)
    df["PV"]= df["PV"]/1000
    fig = line_plot(df, "Time", ["PV","Demand"], "[KW]", 'Time [h]',
                       "PV generation and AC excluded demand", plot_type="line_plot")
    # fig = line_plot(df,'hour',["E_bs","Q_spc"])
    fig.show()
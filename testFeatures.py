import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# df = px.data.tips()
#
# fig = px.treemap(df, path=["day", "time", "tip"], values="total_bill", color="sex")
# print(df.head())
#

df = pd.read_excel("Data/Overview of the savings.xlsx")
# df["Maximum savings"] = df["Maximum savings"].astype(int)

print(df.head())
# fig = px.treemap(
#     df,
#     path=[
#         "Star Rating",
#         "Construction weight",
#         "Maximum savings",
#     ],
#     names="Maximum savings",
#     values="Percentage o buildings",
#     # color="sex",
# )
# fig.update_layout(
#     uniformtext=dict(minsize=10, mode="hide"),  # margin=dict(t=50, l=25, r=25, b=25
#     font={"size": 30},
# )

fig = px.sunburst(
    df,
    path=["Star Rating", "Construction weight"],
    values="Percentage o buildings",
)
fig.update_traces(textinfo="label+percent entry")

fig.show()

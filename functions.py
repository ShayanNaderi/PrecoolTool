import pandas as pd
from dash import html


def read_demand_from_upload():
    pass


def read_demand_from_xlsx_file(site_id):
    df_demand = pd.read_excel(
        "Data/three_month_demand.xlsx"
    )  # convert it to online query
    df_demand = df_demand[["day", "month", "hour", site_id]]
    df_demand.rename(columns={site_id: "Demand"}, inplace=True)
    return df_demand


def create_tariff_column(building, tariff_type, tariff_table, flat_rate, FiT):
    if tariff_type == "flat-rate":
        building.ready_df["Tariff"] = flat_rate
    elif tariff_type == "TOU":
        tariff_table.rename(
            columns={"Rate-weekdays": "Tariff", "Hour": "hour"}, inplace=True
        )
        building.ready_df = building.ready_df.merge(tariff_table, on="hour")
    building.ready_df["FiT"] = FiT
    building.ready_df.to_csv("tariff_added.csv")
    return building


def parse_data(contents, filename):
    import base64
    import io

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df


if __name__ == "__main__":
    create_occupancy_column()

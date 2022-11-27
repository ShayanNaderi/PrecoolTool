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


def process_tariff_rates(building, tariff_id):
    json = pd.read_json("RetailTariffs.json")
    tariff_dicts = json.Tariffs[0]
    print(tariff_id)
    building.ready_df["Tariff"] = 0

    for t in tariff_dicts:
        if t["Tariff ID"] == tariff_id:
            tariff = t

    if tariff["Type"] == "TOU":
        off_peak_rate = tariff["Parameters"]["TOU"]["Off Peak Weekdays"]["Value"]
        building.ready_df["Tariff"] = off_peak_rate

        if "Peak Weekdays" in tariff.keys():
            peak_intervals = tariff["Parameters"]["TOU"]["Peak Weekdays"][
                "TimeIntervals"
            ]
            peak_rate = tariff["Parameters"]["TOU"]["Peak Weekdays"]["Value"]
            for key in peak_intervals.keys():
                start = pd.to_datetime(peak_intervals[key][0]).hour
                end = pd.to_datetime(peak_intervals[key][1]).hour
                building.ready_df.loc[
                    (building.ready_df["hour"] < end)
                    & (building.ready_df["hour"] >= start),
                    "Tariff",
                ] = peak_rate
                print(start, end)

        if "Shoulder Weekdays" in tariff.keys():
            shoulder_rate = tariff["Parameters"]["TOU"]["Shoulder Weekdays"]["Value"]
            shoulder_intervals = tariff["Parameters"]["TOU"]["Shoulder Weekdays"][
                "TimeIntervals"
            ]
            for key in shoulder_intervals.keys():
                start = pd.to_datetime(shoulder_intervals[key][0]).hour
                end = pd.to_datetime(shoulder_intervals[key][1]).hour
                building.ready_df.loc[
                    (building.ready_df["hour"] < end)
                    & (building.ready_df["hour"] >= start),
                    "Tariff",
                ] = shoulder_rate
                print(start, end)

    elif tariff["Type"] == "Single_Rate":
        flat_rate = tariff_dicts[0]["Parameters"]["FlatRate"]["Value"]
        building.ready_df["Tariff"] = flat_rate

    building.ready_df["FiT"] = tariff["Parameters"]["FiT"]["Value"]
    building.ready_df.to_csv("tariff_added.csv")

    return building


if __name__ == "__main__":
    create_occupancy_column()

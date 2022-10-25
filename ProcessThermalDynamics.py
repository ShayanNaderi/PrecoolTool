import logging

import pandas as pd

# flake8: noqa
logger = logging.getLogger(__name__)


dic_zones = {
    "Large_House_zones_conditioned": [
        "Family/Kitchen",
        "Laundry",
        "Bed 5",
        "Lounge",
        "Bed 3",
        "Bed 2",
        "Upper Hall",
        "Bathroom",
        "Bed 4",
        "Bed 1",
        "WIR",
        "Ensuite",
    ],
    "Large_House_zones_all": [
        "Garage",
        "Family/Kitchen",
        "Powder",
        "Laundry",
        "Bed 5",
        "Lounge",
        "Bed 3",
        "WC",
        "Bed 2",
        "Upper Hall",
        "Bathroom",
        "Bed 4",
        "Bed 1",
        "WIR",
        "Ensuite",
        "Roofspace",
    ],
    "Large_House_conditioned_area": {  # fixed
        "Family/Kitchen": 80,
        "Laundry": 5,
        "Bed 5": 15,
        "Lounge": 20,
        "Bed 3": 13,
        "Bed 2": 15,
        "Upper Hall": 15,
        "Bathroom": 10,
        "Bed 4": 15,
        "Bed 1": 15,
        "WIR": 10,
        "Ensuite": 10,
    },
    "Small_House_zones_conditioned": [
        "BED 1",
        "ENTRY",
        "FAMILY/KITCHEN",
        "GALLERY",
        "BED 2",
        "ENS",
        "BED 3",
    ],
    "Small_House_zones_all": [
        "BED 1",
        "ENTRY",
        "WC",
        "FAMILY/KITCHEN",
        "GALLERY",
        "BED 2",
        "ENS",
        "BATH",
        "BED 3",
    ],
    "Small_House_conditioned_area": {  # fixed
        "BED 1": 10,
        "ENTRY": 10,
        "FAMILY/KITCHEN": 35,
        "GALLERY": 5,
        "BED 2": 15,
        "ENS": 5,
        "BED 3": 15,
    },
    "Small_Apartment_zones_conditioned": ["Kitchen/Living", "Bed 1", "Entrance"],
    "Small_Apartment_zones_all": ["Kitchen/Living", "Bed 1", "Entrance", "Bath"],
    "Small_Apartment_conditioned_area": {  # fixed
        "Kitchen/Living": 30,
        "Bed 1": 10,
        "Entrance": 7,
    },
    "Medium_Apartment_zones_conditioned": [
        "Living/Kitchen",
        "Laundry",
        "Bath",
        "Bed1",
        "Ensuite",
        "Bed2",
        "Study",
    ],
    "Medium_Apartment_zones_all": [
        "Living/Kitchen",
        "Laundry",
        "Bath",
        "Bed1",
        "Ensuite",
        "Bed2",
        "Study",
    ],
    "Medium_Apartment_conditioned_area": {  # fixed
        "Living/Kitchen": 45,
        "Laundry": 5,
        "Bath": 5,
        "Bed1": 15,
        "Ensuite": 5,
        "Bed2": 15,
        "Study": 5,
    },
    "Large_Apartment_zones_conditioned": [
        "Kitchen/Living",
        "Master Bed",
        "Ens (Master)",
        "Bed 2",
        "Bed 3",
        "Hall",
    ],
    "Large_Apartment_zones_all": [
        "Kitchen/Living",
        "Master Bed",
        "Bath",
        "Ens (Master)",
        "Bed 2",
        "Bed 3",
        "Hall",
    ],
    "Large_Apartment_conditioned_area": {  # fixed
        "Kitchen/Living": 45,
        "Master Bed": 25,
        "Ens (Master)": 5,
        "Bed 2": 15,
        "Bed 3": 15,
        "Hall": 15,
    },
}


def read_TMY_weather_files(city, all_fields=False):
    climate_zones_list = {"Melbourne": 62, "Brisbane": 10, "Adelaide": 16, "Sydney": 56}

    weather = pd.read_fwf(
        "Data/TMY/climat{}.txt".format(climate_zones_list[city]),
        widths=[
            2,
            2,
            2,
            2,
            2,
            4,
            3,
            4,
            3,
            2,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            4,
            3,
            4,
            2,
            3,
            1,
            1,
            5,
            5,
            20,
        ],
        header=None,
    )
    if all_fields == False:
        # print("Hi")
        weather = weather.iloc[:, 17:18]
        weather.columns = ["SR"]
        return weather

    elif all_fields == True:
        # weather = weather.iloc[:, 17:22]
        weather = weather.iloc[
            :,
            [1, 2, 3, 4, 5, 8, 17, 18, 19, 20, 21],
        ]
        weather.columns = [
            "year",
            "month",
            "day",
            "hour",
            "DBT",
            "Wspd",
            "GHI",
            "DHI",
            "DNI",
            "Altitude",
            "Azimuth",
        ]
        weather[["DBT", "Wspd"]] = weather[["DBT", "Wspd"]] / 10
        # weather["year"] = 2020
        weather.loc[weather["year"] > 30, "year"] = weather["year"] + 1900
        weather.loc[weather["year"] <= 30, "year"] = weather["year"] + 2000

        weather["DateTime"] = pd.to_datetime(weather[["year", "month", "day", "hour"]])
        weather.set_index("DateTime", inplace=True, drop=True)

        return weather


def convert_raw_to_csv():

    """This function converts raw data to processed aggregated data files (csv)

    This funciton reads .ene and .tem files for all buildings from /Data
    and aggregates the indoor temperature, then writes .csv files
    in /Data/Processed_thermal_dynamics"""
    for city in ["Adelaide", "Melbourne", "Brisbane", "Sydney"]:
        for size in ["Small", "Large"]:
            for type in ["House", "Apartment"]:
                for star in ["2star", "6star", "8star"]:
                    for weight in ["Light", "Medium", "Heavy"]:
                        print(city, size, type, star, weight)
                        ene_string = "Data/{}{}/{}{}_{}___{}-{}.ene".format(
                            size, type, type, size, city, weight, star
                        )
                        tmp_string = "Data/{}{}/{}{}_{}___{}-{}.tem".format(
                            size, type, type, size, city, weight, star
                        )

                        # "Data/LargeHouse/HouseLarge_Adelaide___Heavy-2star.ene"
                        load_df = pd.read_csv(
                            ene_string,
                            skiprows=[0, 1, 2, 3, 4],
                            header=None,
                            delim_whitespace=True,
                        )
                        load_df.drop(columns=[0, 1, 2], axis=1, inplace=True)

                        header = pd.MultiIndex.from_product(
                            [
                                dic_zones["{}_{}_zones_conditioned".format(size, type)],
                                ["Heat", "CoolS", "CoolL"],
                            ],
                            names=["Zone", "loadType"],
                        )

                        load_df = pd.DataFrame(load_df.to_numpy(), columns=header)
                        level_0 = load_df.columns.get_level_values(level=0).unique()
                        for i in level_0:
                            load_df.loc[:, (i, ["CoolL", "CoolS"])] *= -1

                        load_df = load_df.groupby(level=0, axis=1).sum()  #
                        load_df["agg_AC"] = load_df.sum(axis=1)
                        load_df = load_df.loc[:, ["agg_AC"]]

                        temp_df = pd.read_csv(
                            tmp_string,
                            skiprows=[0, 1, 2, 3],
                            delim_whitespace=True,
                            header=None,
                        )

                        outdoor_temp = temp_df[3]
                        datetime = temp_df.iloc[:, :3]
                        datetime.columns = ["Month", "Day", "Hour"]
                        time = temp_df[[0, 1, 2]].copy(deep=True)
                        # print(time.head(3))
                        temp_df.drop(columns=[0, 1, 2, 3], axis=1, inplace=True)
                        # flake8: noqa
                        try:  # noqa: E722
                            temp_df.columns = dic_zones[
                                "{}_{}_zones_all".format(size, type)
                            ]
                        except Exception as ve:  # noqa: E722
                            temp_df = temp_df.iloc[:, :-1]
                            temp_df.columns = dic_zones[
                                "{}_{}_zones_all".format(size, type)
                            ]
                            # logger.exception(ve)

                        temp_df = temp_df.loc[
                            :, dic_zones["{}_{}_zones_conditioned".format(size, type)]
                        ]

                        total_conditioned_area = sum(
                            dic_zones[
                                "{}_{}_conditioned_area".format(size, type)
                            ].values()
                        )

                        for key, value in dic_zones[
                            "{}_{}_conditioned_area".format(size, type)
                        ].items():
                            temp_df[key] = temp_df[key] * value / total_conditioned_area

                        temp_df["agg_temp"] = temp_df.sum(axis=1)
                        temp_df["outdoor"] = outdoor_temp
                        temp_df = temp_df.loc[:, ["agg_temp", "outdoor"]]

                        weather = read_TMY_weather_files(city)

                        processed_df = pd.concat(
                            [time, temp_df, load_df, weather], axis=1
                        )
                        processed_df.rename(
                            columns={0: "month", 1: "day", 2: "hour"}, inplace=True
                        )

                        print(processed_df.head(3))
                        processed_df.to_csv(
                            "Data/Processed_thermal_dynamics/{}_{}_{}_{}_{}.csv".format(
                                size, type, star, weight, city
                            )
                        )


if __name__ == "__main__":
    convert_raw_to_csv()

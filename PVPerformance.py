locations = {
    "Sydney": {"lat": -33.8688, "long": 151.2093},
    "Melbourne": {"lat": -37.8136, "long": 144.9631},
    "Brisbane": {"lat": -27.4705, "long": 153.0260},
    "Adelaide": {"lat": -34.9285, "long": 138.6007},
}
tilt_angle_Aus = {
    "Sydney": 33.9,
    "Melbourne": 37.8,
    "Brisbane": 27.5,
    "Adelaide": 34.9,
    "Darwing": 12.5,
    "Hobart": 42.9,
    "Perth": 31.9,
}
altitude = {"Sydney": 34, "Melbourne": 169, "Brisbane": 800, "Adelaide": 50}
azimuth = {
    "North": 0,
    "Northeast": 45,
    "East": 90,
    "Southeast": 135,
    "South": 180,
    "Southwest": 225,
    "West": 270,
    "Northwest": 315,
}


def calculate_PV_output(
    city, PV_capacity_W, temp_coeff=-0.004, inv_efficiency=0.96, orientation="North"
):
    from ProcessThermalDynamics import read_TMY_weather_files

    tmy_manual = read_TMY_weather_files(city, True)

    # tmy_manual.year = 2020
    # tmy_manual.index = pd.to_datetime(
    #             tmy_manual[["year", "month", "day", "hour"]]
    #         )
    if city == "Sydney":
        tmy_manual = tmy_manual[tmy_manual.index != "1990-10-28 02:00:00"]  #
    elif city == "Adelaide":
        tmy_manual = tmy_manual[tmy_manual.index != "1985-10-27 02:00:00"]  #

    tmy_manual.index = tmy_manual.index.tz_localize(
        "Australia/{}".format(city), ambiguous=False
    )

    import inspect
    import os

    import matplotlib.pyplot as plt
    import pvlib

    tmy_manual.index.name = "Time"

    loc = pvlib.location.Location(
        latitude=locations[city]["lat"],
        longitude=locations[city]["long"],
        tz="Australia/{}".format(city),
        altitude=altitude[city],
        name=city.replace('"', ""),
    )

    times = (
        tmy_manual.index
    )  # - pd.Timedelta('30min') #convert to local time otherwise UTC will be assumed with the specefied location

    solar_position = loc.get_solarposition(times)
    # solar_position.index += pd.Timedelta('30min')

    df_poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt_angle_Aus[city],  # tilted 20 degrees from horizontal
        surface_azimuth=azimuth[orientation],  # facing South
        dni=tmy_manual["DNI"],
        ghi=tmy_manual["GHI"],
        dhi=tmy_manual["DHI"],
        solar_zenith=solar_position["apparent_zenith"],
        solar_azimuth=solar_position["azimuth"],
        model="isotropic",
    )
    poa = df_poa["poa_global"]

    parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"][
        "close_mount_glass_glass"
    ]
    cell_temperature = pvlib.temperature.sapm_cell(
        poa, tmy_manual["DBT"], tmy_manual["Wspd"], **parameters
    )

    gamma_pdc = temp_coeff  # divide by 100 to go from %/°C to 1/°C
    nameplate = PV_capacity_W  # Rated capacity W

    array_power = pvlib.pvsystem.pvwatts_dc(poa, cell_temperature, nameplate, gamma_pdc)

    array_power.index = array_power.index.map(lambda t: t.replace(year=2020))

    pdc0 = PV_capacity_W / inv_efficiency  # W
    ac_power_time_series = pvlib.inverter.pvwatts(array_power, pdc0)
    ac_power_time_series = ac_power_time_series.to_frame()
    ac_power_time_series["month"] = ac_power_time_series.index.month
    ac_power_time_series["day"] = ac_power_time_series.index.day
    ac_power_time_series["hour"] = ac_power_time_series.index.hour
    ac_power_time_series.rename(columns={0: "PV"}, inplace=True)
    ac_power_time_series["date"] = ac_power_time_series.index.date
    ac_power_time_series.reset_index(inplace=True)
    print(ac_power_time_series[:10])
    # print(ac_power_time_series.columns)

    return ac_power_time_series


if __name__ == "__main__":
    calculate_PV_output(city="Adelaide", PV_capacity_W=5000)

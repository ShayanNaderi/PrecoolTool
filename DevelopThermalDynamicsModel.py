import pandas as pd


class Building:
    def __init__(self, starRating, weight, type, size, city="Adelaide"):
        self.starRating = starRating
        self.weight = weight
        self.type = type
        self.city = city
        self.size = size

        self.read_thermal_dynamics_file()
        self.thermal_coefficients = self.create_thermal_model(self.thermal_dynamics_df)

    def read_thermal_dynamics_file(self):
        """
        Reads the processed thermal dynamics file

        This function simply reads the file containing the aggregated
        thermal dynamics, AC demand (simulated using AccuRate), and solar
        radiation, date and hour. The file is used to develop thermal
        dynamics model and extract coefficients.

        :return:
        df: DataFrame
            One year AC demand, indoor temperature, and solar ratiation
        """
        self.thermal_dynamics_df = pd.read_csv(
            "Data/Processed_thermal_dynamics/{}_{}_{}_{}_{}.csv".format(
                self.size, self.type, self.starRating, self.weight, self.city
            )
        )
        self.thermal_dynamics_df.drop("Unnamed: 0", inplace=True, axis=1)

    def create_lags(self, df, lags):
        """Create lags of the thermal dynamics dataframe


        :returns
        --------




        """
        for c in df.columns:
            for l in range(1, lags + 1):
                df[c + str(l)] = df[c].shift(l)

        df.dropna(axis=0, how="any", inplace=True)
        return df

    def create_thermal_model(self, df, lags=2):
        """creates the linear model and returns the coefficients

        df: The dataframe with four coloumns (agg_temp, outdoor,agg_AC, SR).It can be read from processed csv files
        """
        import statsmodels.api as sm
        from sklearn import linear_model

        lags_df = self.create_lags(
            df=df.iloc[:, 3:].copy(deep=True),
            lags=lags,
        )

        x = lags_df.iloc[:, 1:]
        y = lags_df["agg_temp"]

        regr = linear_model.LinearRegression()
        regr.fit(x, y)

        x = sm.add_constant(x)  # adding a constant

        model = sm.OLS(y, x).fit()
        predictions = model.predict(x)

        print_model = model.summary()
        # print(model.params)

        return model.params

    def baseline_summer(self, neutral, upper):
        T_setpoint = neutral
        for i, row in self.SH_ahead.iterrows():
            if i < 2:
                self.SH_ahead.at[i, "Q_bs"] = 0
                self.SH_ahead.at[i, "T_bs"] = self.T_n
                self.SH_ahead.at[i, "Q_bs_im"] = 0
            else:

                self.SH_ahead.at[i, "Q_bs"] = 0
                self.SH_ahead.at[i, "T_bs"] = (
                    self.popt[0] * self.SH_ahead.at[i - 1, "Out"]
                    + self.popt[1] * self.SH_ahead.at[i - 1, "T_bs"]
                    + self.popt[2] * self.SH_ahead.at[i - 1, "SR"]
                    + self.popt[3] * self.SH_ahead.at[i - 1, "Q_bs"]
                    + self.popt[4] * self.SH_ahead.at[i, "Q_bs"]
                    + self.popt[5] * self.SH_ahead.at[i, "Out"]
                    + self.popt[6] * self.SH_ahead.at[i, "SR"]
                    + self.popt[7] * self.SH_ahead.at[i - 2, "Out"]
                    + self.popt[8] * self.SH_ahead.at[i - 2, "T_bs"]
                    + self.popt[9] * self.SH_ahead.at[i - 2, "Q_bs"]
                    + self.popt[10] * self.SH_ahead.at[i - 2, "SR"]
                )
                if self.SH_ahead.at[i, "T_bs"] > self.Temperature_range_c[1]:
                    Q_bs = (
                        -(
                            -T_setpoint
                            + self.popt[0] * self.SH_ahead.at[i - 1, "Out"]
                            + self.popt[1] * self.SH_ahead.at[i - 1, "T_bs"]
                            + self.popt[2] * self.SH_ahead.at[i - 1, "SR"]
                            + self.popt[3] * self.SH_ahead.at[i - 1, "Q_bs"]
                            + self.popt[5] * self.SH_ahead.at[i, "Out"]
                            + self.popt[6] * self.SH_ahead.at[i, "SR"]
                            + self.popt[7] * self.SH_ahead.at[i - 2, "Out"]
                            + self.popt[8] * self.SH_ahead.at[i - 2, "T_bs"]
                            + self.popt[9] * self.SH_ahead.at[i - 2, "Q_bs"]
                            + self.popt[10] * self.SH_ahead.at[i - 2, "SR"]
                        )
                        / self.popt[4]
                    )
                    Q_bs = min(Q_bs, 0)
                    self.SH_ahead.at[i, "Q_bs"] = max(Q_bs, -self.AC_size)
                    self.SH_ahead.at[i, "T_bs"] = (
                        self.popt[0] * self.SH_ahead.at[i - 1, "Out"]
                        + self.popt[1] * self.SH_ahead.at[i - 1, "T_bs"]
                        + self.popt[2] * self.SH_ahead.at[i - 1, "SR"]
                        + self.popt[3] * self.SH_ahead.at[i - 1, "Q_bs"]
                        + self.popt[4] * self.SH_ahead.at[i, "Q_bs"]
                        + self.popt[5] * self.SH_ahead.at[i, "Out"]
                        + self.popt[6] * self.SH_ahead.at[i, "SR"]
                        + self.popt[7] * self.SH_ahead.at[i - 2, "Out"]
                        + self.popt[8] * self.SH_ahead.at[i - 2, "T_bs"]
                        + self.popt[9] * self.SH_ahead.at[i - 2, "Q_bs"]
                        + self.popt[10] * self.SH_ahead.at[i - 2, "SR"]
                    )

                self.SH_ahead.at[i, "Q_bs_im"] = min(
                    0,
                    self.SH_ahead.at[i, "Q_bs"]
                    + self.SH_ahead.at[i, "Surpluss_PV"] * self.cop,
                )


def join_PV_load_temp(PV, load_temp):
    joined_df = PV.merge(load_temp, on=["month", "day", "hour"])
    return joined_df


def run_scenarios(df):
    available_dates = df.date.unique()
    return available_dates


if __name__ == "__main__":
    building = Building(
        starRating="2star",
        weight="heavy",
        type="Apartment",
        size="small",
        city="Adelaide",
    )

    ready_df = pd.read_csv("ready_df.csv")
    unique_dates = run_scenarios(ready_df)
    #
    # for date in available dates:
    # simualte baseline
    # simulate SPC
    # quantify metrics
    print(unique_dates)

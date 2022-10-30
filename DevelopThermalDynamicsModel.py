import pandas as pd


class Building:
    def __init__(self, starRating, weight, type, size, city="Adelaide"):
        self.starRating = starRating
        self.weight = weight
        self.type = type
        self.city = city
        self.size = size
        self.cop = 3.5
        self.read_thermal_dynamics_file()

        self.thermal_coefficients = self.create_thermal_model(self.thermal_dynamics_df)
        # print(self.thermal_coefficients)

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
        """
        Simulates the baseline scenario during the summer
        ------

        This funciton is called for each day of the summer,
        and it returns an hourly daily dataframe for each day containing
        indoor temperature, AC demand, and imports.

        :param neutral: User's preffered Neutral temperature entered via the GUI
        :param upper: Upper limit of thermal comfort entered via GUI
        :return: SH_ahead(DataFrame): DataFrame that contains the solved solution
        """
        self.SH_ahead.reset_index(inplace=True,drop=True)
        self.SH_ahead.loc[:,'T_bs'] = 0
        self.SH_ahead.loc[:,'Q_bs'] = 1000
        self.SH_ahead.loc[:,"Q_bs_im"] = 0

        T_setpoint = neutral
        for i, row in self.SH_ahead.iterrows():
            if i < 2:
                self.SH_ahead.at[i, "Q_bs"] = 0
                self.SH_ahead.at[i, "T_bs"] = neutral
                self.SH_ahead.at[i, "Q_bs_im"] = 0
            else:

                self.SH_ahead.at[i, "Q_bs"] = 0
                self.SH_ahead.at[i, "T_bs"] = (
                    self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                    + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_bs"]
                    + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                    + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_bs"]
                    + self.thermal_coefficients['agg_AC'] * self.SH_ahead.at[i, "Q_bs"]
                    + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                    + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                    + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                    + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_bs"]
                    + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_bs"]
                    + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]
                )
                if self.SH_ahead.at[i, "T_bs"] > upper:
                    Q_bs = (
                        -(
                            -T_setpoint
                            + self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                            + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_bs"]
                            + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                            + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_bs"]
                            + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                            + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                            + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                            + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_bs"]
                            + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_bs"]
                            + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]
                        )
                        / self.thermal_coefficients['agg_AC']
                    )
                    Q_bs = min(Q_bs, 0)
                    self.SH_ahead.at[i, "Q_bs"] = max(Q_bs, -self.AC_size)
                    self.SH_ahead.at[i, "T_bs"] = (
                            self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                            + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_bs"]
                            + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                            + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_bs"]
                            + self.thermal_coefficients['agg_AC'] * self.SH_ahead.at[i, "Q_bs"]
                            + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                            + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                            + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                            + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_bs"]
                            + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_bs"]
                            + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]
                    )

        # print(self.SH_ahead.head(24))


    def baseline_winter(self,night_setpoint,day_setpoint):
        print("Miad inja?")
        self.SH_ahead.reset_index(inplace=True,drop=True)
        for i, row in self.SH_ahead.iterrows():
            if i < 2:
                self.SH_ahead.at[i, 'Q_bs'] = 0
                self.SH_ahead.at[i, 'T_bs'] = night_setpoint
                self.SH_ahead.at[i, 'Q_bs_im'] = 0
                self.SH_ahead.at[i,'W_bs'] = 0
            else:
                if (i > 1) & (i < 7):
                    T_setpoint = night_setpoint
                elif i > 6:
                    T_setpoint = day_setpoint
                self.SH_ahead.at[i, 'Q_bs'] = 0
                self.SH_ahead.at[i, "T_bs"] = (self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                    + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_bs"]
                    + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                    + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_bs"]
                    + self.thermal_coefficients['agg_AC'] * self.SH_ahead.at[i, "Q_bs"]
                    + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                    + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                    + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                    + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_bs"]
                    + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_bs"]
                    + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]
                )
                if self.SH_ahead.at[i, 'T_bs'] < T_setpoint:
                    # T_setpoint = self.Temperature_range_h_daytime[0]
                    Q_bs = (
                        -(-T_setpoint
                            + self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                            + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_bs"]
                            + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                            + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_bs"]
                            + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                            + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                            + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                            + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_bs"]
                            + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_bs"]
                            + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]
                        )/ self.thermal_coefficients['agg_AC'])
                    Q_bs = max(0,Q_bs)
                    self.SH_ahead.at[i, 'Q_bs'] = min(Q_bs, self.AC_size)
                    self.SH_ahead.at[i, "T_bs"] = self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"] +\
                                                  self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_bs"]\
                                                  + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]+\
                                                  self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_bs"]+\
                                                  self.thermal_coefficients['agg_AC'] * self.SH_ahead.at[i, "Q_bs"]+\
                                                  self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]+\
                                                  self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]+\
                                                  self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]+\
                                                  self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_bs"]+\
                                                  self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_bs"]+\
                                                  self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]
                # self.SH_ahead.at[i, 'Q_bs_im'] = max(0, self.SH_ahead.at[i, 'Q_bs'] - self.SH_ahead.at[
                #     i, 'Surpluss_PV'] * self.cop)
            # if (i > 1) & (i < 7):
            #     self.SH_ahead.at[i, 'W_bs'] = 0
            # elif i > 6:
            #     self.SH_ahead.at[i, 'W_bs'] = day_setpoint - self.SH_ahead.at[i, 'T_bs']
def join_PV_load_temp(PV, load_temp):
    joined_df = PV.merge(load_temp, on=["month", "day", "hour"])
    return joined_df


def run_scenarios(building,df):

    available_dates = df.date.unique()
    for date in available_dates:
        building.SH_ahead = df[df['date'] == date]
        datetime= pd.to_datetime(date)
        if datetime.month in[12,1,2,9,10,11]:
            building.baseline_summer(neutral=22,upper=25)
            print(building.SH_ahead.head(20))

        elif datetime.month in[3,4,5,6,7,8]:
        # if datetime.month in[3,4,5,6,7,8]:
            pass
            # building.baseline_winter(18,20)
            # print(a.month)

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
    building.AC_size = 25
    # print(type(building.thermal_coefficients['SR2']))
    unique_dates = run_scenarios(building,ready_df)
    #
    # for date in available dates:
    # simualte baseline
    # simulate SPC
    # quantify metrics
    # print(unique_dates)

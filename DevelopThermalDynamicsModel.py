import pandas as pd
import functions
from figures import line_plot

class Building:

    def __init__(self, starRating, weight, type, size,AC_size, city="Adelaide"):
        self.starRating = starRating
        self.weight = weight
        self.type = type
        self.city = city
        self.size = size
        self.AC_size = AC_size
        self.cop = 3.5
        self.tariff_df = None
        self.ready_df = None
        self.name = None
        self.occupancy_checklist = [1,3,4]
        self.daily_results_dic = {}
        self.final_df = pd.DataFrame()
        self.read_thermal_dynamics_file()
        self.upper_limit =0
        self.neutral_temp = 0
        self.lower_limit = 0
        self.thermal_coefficients = self.create_thermal_model(self.thermal_dynamics_df)


    def update_temperature_preferences(self,ready_df,neutral_temp,upper_limit,lower_limit):
        self.upper_limit = upper_limit
        self.neutral_temp = neutral_temp
        self.lower_limit = lower_limit
        self.ready_df = ready_df

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

    def baseline_summer(self, neutral, upper,setpoint="Upper"):
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
        setpoint_dic = {"Neutral":neutral, "Upper":upper}
        # self.SH_ahead.reset_index(inplace=True,drop=True)
        self.SH_ahead.loc[:,'T_bs'] = 0
        self.SH_ahead.loc[:,'Q_bs'] = 1000

        for i, row in self.SH_ahead.iterrows():
            if i < 6:
                self.SH_ahead.at[i, "Q_bs"] = 0
                self.SH_ahead.at[i, "T_bs"] = neutral -1
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
                    + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]+ self.thermal_coefficients['const']
                )
                if (self.SH_ahead.at[i, "T_bs"] > upper)&(self.SH_ahead.at[i, "Occupancy"] == 1):
                    T_setpoint = setpoint_dic[setpoint]

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
                            + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']
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
                            + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']
                    )
        self.SH_ahead['W_bs'] = (self.SH_ahead['T_bs'] - upper) * self.SH_ahead['Occupancy']
        self.SH_ahead['W_bs'] = self.SH_ahead['W_bs'].clip(lower=0)

        # print(self.SH_ahead.head(24))
    def solar_precool(self, neutral,upper,lower,setpoint="Upper"):
        setpoint_dic = {"Neutral":neutral, "Upper":upper}
        # self.SH_ahead.reset_index(inplace=True, drop=True)
        self.SH_ahead.loc[:,'T_spc'] = 0
        self.SH_ahead.loc[:,'Q_spc'] = 1000
        for i, row in self.SH_ahead.iterrows():
            if i < 6:
                self.SH_ahead.at[i, 'Q_spc'] = 0
                self.SH_ahead.at[i, 'T_spc'] = neutral - 1
            elif i > 5:
                T_setpoint = lower
                Q_spc = -(-T_setpoint +
                          + self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                          + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_spc"]
                          + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                          + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_spc"]
                          + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                          + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                          + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                          + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_spc"]
                          + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_spc"]
                          + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]+self.thermal_coefficients['const'])/ self.thermal_coefficients['agg_AC']
                Q_spc = min(Q_spc, 0)  # Just cooling mode
                self.SH_ahead.at[i, 'Q_spc'] = max(
                    [Q_spc, -self.SH_ahead.at[i, 'Surplus_PV'] * self.cop, -self.AC_size])

                self.SH_ahead.at[i, 'T_spc'] = (self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                    + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_spc"]
                    + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                    + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_spc"]
                    + self.thermal_coefficients['agg_AC'] * self.SH_ahead.at[i, "Q_spc"]
                    + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                    + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                    + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                    + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_spc"]
                    + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_spc"]
                    + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']
                )

                if (self.SH_ahead.at[i, 'T_spc'] > upper)&(self.SH_ahead.at[i, 'Occupancy'] == 1):
                    if self.SH_ahead.at[i, 'Q_spc'] > -self.AC_size: #It means the suprluss PV generation is smaller than AC capacity

                        T_setpoint = setpoint_dic[setpoint]

                        self.SH_ahead.at[i, 'Q_spc'] = -(-T_setpoint +
                          + self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                          + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_spc"]
                          + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                          + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_spc"]
                          + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                          + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                          + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                          + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_spc"]
                          + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_spc"]
                          + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"]+
                                                         self.thermal_coefficients['const'])/ self.thermal_coefficients['agg_AC']

                        self.SH_ahead.at[i, 'Q_spc'] = max([self.SH_ahead.at[i, 'Q_spc'], -self.AC_size])  # negative

                        self.SH_ahead.at[i, 'T_spc'] = (self.thermal_coefficients['outdoor1'] * self.SH_ahead.at[i - 1, "outdoor"]
                        + self.thermal_coefficients['agg_temp1'] * self.SH_ahead.at[i - 1, "T_spc"]
                        + self.thermal_coefficients['SR1'] * self.SH_ahead.at[i - 1, "SR"]
                        + self.thermal_coefficients['agg_AC1'] * self.SH_ahead.at[i - 1, "Q_spc"]
                        + self.thermal_coefficients['agg_AC'] * self.SH_ahead.at[i, "Q_spc"]
                        + self.thermal_coefficients['outdoor'] * self.SH_ahead.at[i, "outdoor"]
                        + self.thermal_coefficients['SR'] * self.SH_ahead.at[i, "SR"]
                        + self.thermal_coefficients['outdoor2'] * self.SH_ahead.at[i - 2, "outdoor"]
                        + self.thermal_coefficients['agg_temp2'] * self.SH_ahead.at[i - 2, "T_spc"]
                        + self.thermal_coefficients['agg_AC2'] * self.SH_ahead.at[i - 2, "Q_spc"]
                        + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']
                         )

        self.SH_ahead['W_spc'] = (self.SH_ahead['T_spc'] - upper) * self.SH_ahead['Occupancy']
        self.SH_ahead['W_spc'] = self.SH_ahead['W_spc'].clip(lower=0)


    def baseline_winter(self,night_setpoint,day_setpoint):
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
                    + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']
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
                            + self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']
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
                                                  self.thermal_coefficients['SR2'] * self.SH_ahead.at[i - 2, "SR"] + self.thermal_coefficients['const']

    def groupby_final_results(self):

        self.averaged_hourly_results = self.final_df.groupby("hour").agg({"outdoor":"mean","Demand":"mean","E_spc":"mean",
                                                                          "PV":"mean",
                                                                          "E_bs":"mean", "Surplus_PV":"mean",
                                                                          "T_bs":'mean',"T_spc":"mean",
                                                                          "W_bs":"sum","W_spc":"sum","Q_bs":"mean","Q_spc":"mean"})
        self.averaged_hourly_results["PV"] = self.averaged_hourly_results["PV"]
        self.averaged_hourly_results.reset_index(inplace=True)
        self.averaged_hourly_results.to_csv("Average_hourly_result.csv")

    def calculate_imports_exports(self):
        self.final_df[["E_bs","E_spc"]] = abs(self.final_df[["Q_bs","Q_spc"]])/self.cop

        self.final_df["Net_spc"] = self.final_df["Demand"] + self.final_df["E_spc"] - self.final_df["PV"]
        self.final_df["Net_bs"] = self.final_df["Demand"] + self.final_df["E_bs"] - self.final_df["PV"]

        self.final_df["Imports_spc"] = self.final_df["Net_spc"].clip(lower=0)
        self.final_df["Imports_bs"] = self.final_df["Net_bs"].clip(lower=0)

        self.final_df["Export_spc"] = -self.final_df["Net_spc"].clip(upper=0)
        self.final_df["Export_bs"] = -self.final_df["Net_bs"].clip(upper=0)

    def calculate_savings(self):
        self.final_df['cost_bs'] = (self.final_df["Imports_bs"] * 22 - self.final_df["Export_bs"] * 6)/100
        self.final_df['cost_spc'] = (self.final_df["Imports_spc"] * 22 - self.final_df["Export_spc"] * 6)/100
        self.final_df['Savings'] = self.final_df['cost_bs'] - self.final_df['cost_spc']
        self.monthly_saving = self.final_df.groupby("month").agg({"Savings":"sum"})
        # print(self.monthly_saving)

    def create_occupancy_column(self):
        """This function creates the occupancy column

        Based on the checklist edited bu the user, it creates
        a dataframe

        1: Building is occupied
        0: building is unoccupied
        """
        if 1 in self.occupancy_checklist:
            self.SH_ahead.loc[7:9,"Occupancy"] = 1
        if 2 in self.occupancy_checklist:
            self.SH_ahead.loc[10:13,"Occupancy"] = 1
        if 3 in self.occupancy_checklist:
            self.SH_ahead.loc[14:17,"Occupancy"] = 1
        if 4 in self.occupancy_checklist:
            self.SH_ahead.loc[18:23,"Occupancy"] = 1
        if 5 in self.occupancy_checklist:
            self.SH_ahead.loc[0:6,"Occupancy"] = 1

        # print(self.SH_ahead)



def join_PV_load_temp(PV, load_temp,real_demand):
    joined_df = PV.merge(load_temp, on=["month", "day", "hour"])
    joined_df = joined_df.merge(real_demand,on=["month", "day", "hour"])
    joined_df['PV'] = joined_df['PV']/1000
    joined_df['Surplus_PV'] = joined_df['PV'] - joined_df['Demand']
    joined_df['Surplus_PV'] = joined_df['Surplus_PV'].clip(lower=0)

    joined_df.to_csv("ready_df.csv")

    return joined_df


def run_scenarios(building):

    available_dates = building.ready_df.date.unique()
    building.ready_df['Occupancy'] = 0
    for date in available_dates:

        building.SH_ahead = building.ready_df[building.ready_df['date'] == date]
        building.SH_ahead.reset_index(inplace=True,drop=True)
        building.create_occupancy_column()
        datetime= pd.to_datetime(date)
        if datetime.month in[12,1,2,9,10,11]:
            building.baseline_summer(neutral=building.neutral_temp,upper=building.upper_limit,setpoint="Neutral")
            building.solar_precool(neutral=building.neutral_temp,lower=building.lower_limit,upper=building.upper_limit,setpoint="Neutral")
            building.daily_results_dic[date] = building.SH_ahead
            building.final_df = pd.concat([building.final_df,building.SH_ahead])

        elif datetime.month in[3,4,5,6,7,8]:
        # if datetime.month in[3,4,5,6,7,8]:
            pass
            # building.baseline_winter(18,20)

    building.calculate_imports_exports()
    print("Imports exports OK")

    building.groupby_final_results()
    print("groupby final results Ok")
    building.calculate_savings()
    print("Calculate savings Ok")

    # building.final_df.to_csv("Final_df_results.csv")


    print("scenarios are successfuly finished!")
    return building




if __name__ == "__main__":
    import json
    building = Building(
        starRating="2star",
        weight="heavy",
        type="Apartment",
        size="small",
        AC_size = 2,
        city="Adelaide",
    )
    # ready_df = pd.read_csv("ready_df.csv")
    # building = run_scenarios(building,ready_df,22,26,18)
    # #
    # # fig =line_plot(building.averaged_hourly_results,'hour',["E_bs","E_spc"],x_title="Time of the day [h]",y_title="Temperature [°C]",title="Indoor temperature trajectory")
    # fig =line_plot(building.averaged_hourly_results,'hour',["W_bs","W_spc"],
    #                x_title="Time of the day [h]",y_title="Temperature [°C]",
    #                title="Indoor temperature trajectory",plot_type="bar_chart")
    # fig.show()

    # df = pd.read_csv("Data/AC_excluded_average_demand.csv")
    # df = df.melt(id_vars = 'Time',var_name = "ID",value_name = "Values")
    # df['ID'] = df['ID'].astype(int)
    # df_class = pd.read_csv("Data/AC_excluded_and_clusters.csv")
    # df = df.merge(df_class[['site_ID',"Cluster"]],left_on = "ID",right_on="site_ID")
    # df.to_csv("Data/average_demand_and_clusters_for_demand_selection.csv")
    # print(building.thermal_coefficients)

    jsonStr = json.to_json(building.__dict__)
    print(jsonStr)

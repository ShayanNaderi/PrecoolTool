import pandas as pd



def read_demand_from_xlsx_file(site_id):
    df_demand = pd.read_excel("Data/three_month_demand.xlsx") #convert it to online query
    df_demand = df_demand[["day",'month','hour',site_id]]
    df_demand.rename(columns={site_id:"Demand"},inplace=True)
    return df_demand

def create_tariff_column(building,tariff_type,tariff_table,flat_rate):
    if tariff_type == "flat-rate":
        building.final_df['Tariff'] = flat_rate
    elif tariff_type == "TOU":
        tariff_table.rename(columns = {"Rate-weekdays":"Tariff","Hour":"hour"},inplace=True)
        building.final_df = building.final_df.merge(tariff_table,on="hour")



if __name__ == "__main__":
    create_occupancy_column()
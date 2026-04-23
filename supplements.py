import pandas as pd
import cdsapi
import xarray as xr
import cfgrib

class TurnInfo:
    #Input parameters
    turn_start_timestamp: pd.Timestamp=pd.Timestamp("1942-08-19 08:00:00") #YYYY-MM-DD HH:MM:SS
    duration_timedelta: pd.Timedelta=pd.Timedelta("00:25:00") #HH:MM:SS
    orders_path: str=r"Resources\ONS-122 Orders Doc - Conjoined 08-19-0800 to 1200.csv" #Relative or absolute path to orders csv file
    game_name= "ONS-122"
    give_weather_report=False
    #Calculated time parameters
    turn_end_timestamp: pd.Timestamp=turn_start_timestamp+duration_timedelta
    duration_min: int =int(duration_timedelta.total_seconds()/60)
    turn_start_time: int=60*turn_start_timestamp.hour+turn_start_timestamp.minute
    turn_end_time: int=turn_start_time+duration_min
    #Calculated file paths
    output_csv_path: str=rf"Output\CSVs\{game_name}__{turn_end_timestamp.strftime('%d-%H%M')}__Output.csv"
    output_plot_path: str=rf"Output\Plots\{game_name}__{turn_end_timestamp.strftime('%d-%H%M')}__Plot.txt"
    weather_report_path: str=rf"Output\Reports\{game_name}__{turn_end_timestamp.strftime('%d-%H%M')}__Weather Report.txt"
    master_file_path: str=rf"Master Files\{game_name}__{turn_start_timestamp.strftime('%m-%d-%H%M')}__MASTER.txt"
    master_output_path: str=rf"Master Files\{game_name}__{turn_end_timestamp.strftime('%m-%d-%H%M')}__MASTER.txt"
    #Static parameters
    grib_path: str=rf"Resources\weather_data_{turn_end_timestamp.strftime('%m-%d-%H%M')}.grib"
    

def download_weather_data(grib_path: str=TurnInfo.grib_path, area: list[float]=[75, -70, 30, 5], timestamp:pd.Timestamp=TurnInfo.turn_end_timestamp):
    year=timestamp.year
    month=f"{timestamp.month:02d}"
    day=f"{timestamp.day:02d}"
    time_str=f"{timestamp.hour:02d}:00"
    
    dataset = "reanalysis-era5-single-levels"
    request = {
        "product_type": ["reanalysis"],
        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "instantaneous_10m_wind_gust",
            "10m_wind_gust_since_previous_post_processing",
            "2m_dewpoint_temperature",
            "2m_temperature",
            "mean_sea_level_pressure",
            "mean_wave_direction",
            "mean_wave_period",
            "sea_surface_temperature",
            "significant_height_of_combined_wind_waves_and_swell",
            "surface_pressure",
            "total_precipitation",
            "sea_ice_cover",
            "precipitation_type",
            "cloud_base_height",
            "total_cloud_cover",
            "surface_solar_radiation_downwards",
            "surface_thermal_radiation_downwards"
        ],
        "year": [f"{year}"],
        "month": [f"{month}"],
        "day": [f"{day}"],
        "time": [f"{time_str}"],
        "data_format": "grib",
        "download_format": "unarchived",
        "area": area
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(grib_path)
    
def read_weather_data(grib_path: str=TurnInfo.grib_path) -> pd.DataFrame:
    ds = xr.merge(cfgrib.open_datasets(grib_path), compat='override')
    # ds = xr.open_datasets(grib_path, engine="cfgrib", backend_kwargs={'filter_by_keys':{'typeOfLevel':'surface','edition': 1}}) # 'typeOfLevel':'meanSea', 
    # ds_meansea = xr.open_dataset(grib_path, engine="cfgrib", backend_kwargs={'filter_by_keys':{'typeOfLevel':'meanSea','edition': 1}})
    # ds=ds_surface.merge(ds_meansea)
    df = ds.to_dataframe()
    return df, ds

def weighted_average_weather_data(df: pd.DataFrame, lat: float, long: float):
    sea_lat_floor=lat//.5*.5
    sea_lat_ceil=sea_lat_floor+.5
    sea_long_floor=long//.5*.5
    sea_long_ceil=sea_long_floor+.5
    sea_lat_weight=(lat-sea_lat_floor)/(sea_lat_ceil-sea_lat_floor) if sea_lat_ceil!=sea_lat_floor else 0
    sea_long_weight=(long-sea_long_floor)/(sea_long_ceil-sea_long_floor) if sea_long_ceil!=sea_long_floor else 0
    
    atm_lat_floor=lat//.25*.25
    atm_lat_ceil=atm_lat_floor+.25  
    atm_long_floor=long//.25*.25
    atm_long_ceil=atm_long_floor+.25
    atm_lat_weight=(lat-atm_lat_floor)/(atm_lat_ceil-atm_lat_floor) if atm_lat_ceil!=atm_lat_floor else 0
    atm_long_weight=(long-atm_long_floor)/(atm_long_ceil-atm_long_floor) if atm_long_ceil!=atm_long_floor else 0
    sea_data=(
        df.loc[(sea_lat_floor, sea_long_floor), "swh":"mwp"]*(1-sea_lat_weight)*(1-sea_long_weight)+
        df.loc[(sea_lat_floor, sea_long_ceil), "swh":"mwp"]*(1-sea_lat_weight)*sea_long_weight+
        df.loc[(sea_lat_ceil, sea_long_floor), "swh":"mwp"]*sea_lat_weight*(1-sea_long_weight)+
        df.loc[(sea_lat_ceil, sea_long_ceil), "swh":"mwp"]*sea_lat_weight*sea_long_weight
    )
    atm_data=(
        df.loc[(atm_lat_floor, atm_long_floor), "siconc":"i10fg"]*(1-atm_lat_weight)*(1-atm_long_weight)+
        df.loc[(atm_lat_floor, atm_long_ceil), "siconc":"i10fg"]*(1-atm_lat_weight)*atm_long_weight+
        df.loc[(atm_lat_ceil, atm_long_floor), "siconc":"i10fg"]*atm_lat_weight*(1-atm_long_weight)+
        df.loc[(atm_lat_ceil, atm_long_ceil), "siconc":"i10fg"]*atm_lat_weight*atm_long_weight
    )
    data=pd.concat([sea_data, atm_data])
    match (atm_lat_weight>.5, atm_long_weight>.5):
        case (True, True):
            data=pd.concat([data, pd.Series([df.loc[(atm_lat_ceil, atm_long_ceil), "ptype"]], index=["ptype"])])
        case (True, False):
            data=pd.concat([data, pd.Series([df.loc[(atm_lat_ceil, atm_long_floor), "ptype"]], index=["ptype"])])
        case (False, True):
            data=pd.concat([data, pd.Series([df.loc[(atm_lat_floor, atm_long_ceil), "ptype"]], index=["ptype"])])
        case (False, False):
            data=pd.concat([data, pd.Series([df.loc[(atm_lat_floor, atm_long_floor), "ptype"]], index=["ptype"])])
        case _:
            data=pd.concat([data, pd.Series([0], index=["ptype"])])
    return data

def convert_nmi_to_meters(nmi: float):
    return nmi*1852


def convert_kt_to_mps(kt: float):
    return kt*0.514444


def convert_mps_to_kt(mps: float):
    return mps/0.514444


def convert_meters_to_nmi(meters: float):
    return meters/1852


def position_along_arc(lat_arc_center, long_arc_center, radius):
    pass

def minutes_to_time(minutes: int):
    
    hours=int((minutes//60))%24
    mins=int(minutes%60)
    return f"{hours:02d}{mins:02d}"
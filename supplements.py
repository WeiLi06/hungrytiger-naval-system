import pandas as pd

class TurnInfo:
    turn_start_timestamp: pd.Timestamp=pd.Timestamp("1942-08-15 20:00:00")
    duration_timedelta: pd.Timedelta=pd.Timedelta("12:00:00")
    turn_end_timestamp: pd.Timestamp=turn_start_timestamp+duration_timedelta
    duration_min: int =60*12
    turn_start_time: int=20*60
    turn_end_time: int=turn_start_time+duration_min
    
@staticmethod
def convert_nmi_to_meters(nmi: float):
    return nmi*1852

@staticmethod
def convert_kt_to_mps(kt: float):
    return kt*0.514444

@staticmethod
def convert_mps_to_kt(mps: float):
    return mps/0.514444

@staticmethod
def convert_meters_to_nmi(meters: float):
    return meters/1852

@staticmethod
def position_along_arc(lat_arc_center, long_arc_center, radius):
    pass

def minutes_to_time(minutes: int):
    
    hours=int((minutes//60))%24
    mins=int(minutes%60)
    return f"{hours:02d}{mins:02d}"
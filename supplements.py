class TurnInfo:
    duration_min: int =60*84
    turn_start_time: int=8*60 #8am in minutes
    
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
    hours=int(minutes//60)
    mins=int(minutes%60)
    return f"{hours:02d}{mins:02d}"
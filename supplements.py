class TurnInfo:
    duration_min: int =6
    turn_start_time: int=1200
    
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
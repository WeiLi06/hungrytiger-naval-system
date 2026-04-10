from nav_vision import Direction, MoveAction, MoveType, Navigation, ShipPose
import ship_data as sd
import supplements as sp
import pandas as pd

timestamp1=pd.Timestamp("1942-08-15 08:00:00")
timedelta1=pd.Timedelta("34:34:00")
print(timestamp1+timedelta1)
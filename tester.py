from nav_vision import Direction, MoveAction, MoveType, Navigation, ShipPose
import ship_data as sd
import supplements as sp
import pandas as pd

# sp.download_weather_data()
df, ds = sp.read_weather_data()
print(df.columns)
for v in ds:
    print("{}, {}, {}".format(v, ds[v].attrs["long_name"], ds[v].attrs["units"]))
print(df.loc[(55.5, -7.5)])
print(sp.weighted_average_weather_data(df, 56, -7.25))



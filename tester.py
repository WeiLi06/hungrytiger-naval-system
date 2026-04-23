from nav_vision import Direction, MoveAction, MoveType, Navigation, ShipPose
import ship_data as sd
import supplements as sp
import pandas as pd

# sp.download_weather_data()
# df, ds = sp.read_weather_data()
# print(df.columns)
# for v in ds:
#      print("{}, {}, {}".format(v, ds[v].attrs["long_name"], ds[v].attrs["units"]))
# print(df.loc[(56, -9)])

txt_path=sp.TurnInfo.master_output_path
name_list=["Athelprince", "U-135","U-174", "U-176", "U-256", "U-373", "U-438", "U-569", "U-596","U-604","U-605","U-660","U-705","U-755"]
for name in name_list:
     output_path=rf"Output\Reports\{name} {sp.TurnInfo.turn_end_timestamp.round(freq='min').strftime('%m-%d-%H%M')}.txt"
     output=open(output_path, "w")
     output.write("type	latitude	longitude	name	desc	icon	color\n")
     for line in open(txt_path, "r").readlines()[1:]:
          if name in line:
               if "W" in line:
                    output.write(line+"\n")
                    output.write("type	latitude	longitude	name	desc	icon	color\n")
               else:
                    output.write(line)
     output.close()


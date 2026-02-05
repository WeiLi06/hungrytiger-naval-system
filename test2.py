import pandas as pd
import ship_data as sd

df=pd.read_csv("resources/test_fleet.csv", index_col=0)
fleet_names=df.loc[:, "FLEET"].unique()
print("GRAND FLEET" in fleet_names)
print(list(fleet_names).index("GRAND FLEET"))
fleets: list[sd.Fleet]=[]
for fleet_name in df.loc[:, "FLEET"].unique():
    fleets.append(sd.Fleet(fleet_name))
for ship_name in (df.index):
    for fleet in fleets:
        if df.loc[ship_name, "FLEET"]==fleet.name:
            new_ship=sd.Warship(sd.ShipPose(df.loc[ship_name, "INITIAL LAT"], df.loc[ship_name, "INITIAL LONG"], df.loc[ship_name, "INITIAL BEARING"]),
                                ship_name)
            fleet.add_ship(new_ship)
            break
print([ship.name for ship in fleets[0].ships])

for x in range(int(len(df.columns)/3)):
    
    break
#print(df)
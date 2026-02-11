import pandas as pd
import ship_data as sd
import supplements as sp    

df=pd.read_csv(r"C:\Users\Weijia\python\hungrytiger-naval-system\Resources\Fleet Template - Sheet1.csv", index_col=0)
fleet_names=df.loc[:, "FLEET"].unique()
print("GRAND FLEET" in fleet_names)
print(list(fleet_names).index("GRAND FLEET"))
fleets: list[sd.Fleet]=[]
for fleet_name in df.loc[:, "FLEET"].unique():
    fleets.append(sd.Fleet(fleet_name))
for fleet in fleets:
    for ship_name in df.loc[df["FLEET"]==fleet.name].index:
            
            new_ship=sd.Warship(sd.ShipPose(df.loc[ship_name, "INITIAL LAT"], df.loc[ship_name, "INITIAL LONG"], df.loc[ship_name, "INITIAL BEARING"]),
                                ship_name, df.loc[ship_name, "INITIAL SPEED"], df.loc[ship_name, "IS COMMANDED"], ship_class=df.loc[ship_name, "CLASS"])
            move_list: list[sd.MoveAction]=[]
            print(f"created ship: {new_ship.name}, with {len(new_ship.navigator.moves)} moves")
            for x in range(int((len(df.columns)-7)/4)):
                print(x)
                if not pd.isna(df.loc[ship_name, f"{x} ORDER TYPE"]):
                    print(f"found move: {df.loc[ship_name, f'{x} ORDER TYPE']}")
                    match df.loc[ship_name, f"{x} ORDER TYPE"]:
                        case "COURSE SPEED":
                            if pd.isna(df.loc[ship_name, f"{x}C"]):
                                move_list.append(sd.MoveAction().course_speed(course=df.loc[ship_name, f"{x}A"], speed=sp.convert_kt_to_mps(df.loc[ship_name, f"{x}B"])))
                            else:
                                move_list.append(sd.MoveAction().course_speed(course=df.loc[ship_name, f"{x}A"], speed=sp.convert_kt_to_mps(df.loc[ship_name, f"{x}B"]), duration_min=df.loc[ship_name, f"{x}C"]))
                        case "WAYPOINT SPEED":
                            move_list.append(sd.MoveAction().to_waypoint(waypoint=sd.ShipPose(df.loc[ship_name, f"{x}A"], df.loc[ship_name, f"{x}B"], 0), speed=sp.convert_kt_to_mps(df.loc[ship_name, f"{x}C"])))
                    print(f"move list length: {len(move_list)}")
            print(move_list)
            new_ship.navigator.give_moves(move_list)
            fleet.add_ship(new_ship)
            print("added ship")
# print(df)
navigator_list: list[sd.Navigator]=[]
for fleet in fleets:
    fleet.move_ships()
    for ship in fleet.ships:
        navigator_list.append(ship.navigator)
sd.plot_course(navigator_list)
print(fleets[1].ships[1])

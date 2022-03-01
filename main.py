import pandas as pd
import numpy as np
import fastf1

import matplotlib.pyplot as plt
import fastf1.plotting


fastf1.Cache.enable_cache("Cache")  # replace with your cache directory

# enable some matplotlib patches for plotting timedelta values and load
# FastF1's default color scheme
fastf1.plotting.setup_mpl()

# load a session and its telemetry data
quali = fastf1.get_session(2021, "Spanish Grand Prix", "R")
laps = quali.load_laps(with_telemetry=True)

laps.pick_driver("VER").get_car_data()


# ver_lap = laps.pick_driver("VER").pick_fastest()
# ham_lap = laps.pick_driver("HAM").pick_fastest()

# ver_tel = ver_lap.get_car_data().add_distance()
# ham_tel = ham_lap.get_car_data().add_distance()

# rbr_color = fastf1.plotting.team_color("RBR")
# mer_color = fastf1.plotting.team_color("MER")

# fig, ax = plt.subplots()
# ax.plot(ver_tel["Distance"], ver_tel["Speed"], color=rbr_color, label="VER")
# ax.plot(ham_tel["Distance"], ham_tel["Speed"], color=mer_color, label="HAM")

# ax.set_xlabel("Distance in m")
# ax.set_ylabel("Speed in km/h")

# ax.legend()

# plt.suptitle(
#     f"Fastest Lap Comparison \n "
#     f"{quali.weekend.name} {quali.weekend.year} Qualifying"
# )

# plt.show()

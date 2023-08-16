from functools import reduce
import numpy as np
from datetime import datetime, timedelta
import fastf1
from fastf1 import utils
from update import *


def delta_time_updated(yr, rc, sn, driver1, lap1, driver2, lap2):
    
    # ref = reference_lap.get_car_data(interpolate_edges=True).add_distance()
    # comp = compare_lap.get_car_data(interpolate_edges=True).add_distance()
    ref = get_telemetry(yr, rc, sn, driver1, lap1)
    comp = get_telemetry(yr, rc, sn, driver2, lap2)

    def mini_pro(stream):
        # Ensure that all samples are interpolated
        dstream_start = stream[1] - stream[0]
        dstream_end = stream[-1] - stream[-2]
        return np.concatenate([[stream[0] - dstream_start], stream, [stream[-1] + dstream_end]])

    ltime = mini_pro(comp['Time'].dt.total_seconds().to_numpy())
    ldistance = mini_pro(comp['Distance'].to_numpy())
    lap_time = np.interp(ref['Distance'], ldistance, ltime)

    delta = lap_time - ref['Time'].dt.total_seconds()

    return delta, ref, comp
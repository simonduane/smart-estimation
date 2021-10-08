"""\
                                smart_script_A.py
        script A version 00                            using module version 03

The test code originally in the module, has been split off and developed here.
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import smart_meters_03 as sm

# read in all my smart data:
smart = {}
for data in ["daily", "half-hourly"]:
    f_path = (f"./json/20WE/")
    f_all = os.listdir(f_path + data)
    f_all.sort()
    smart[data] = sm.read_ovo(f_all[0], data, f_path)
    for f in f_all[1:]:
        s = sm.read_ovo(f, data, f_path)
        smart[data] = sm.extend(smart[data], s)
    print(f"{len(smart[data]['times'])} records of {data} data read ...")
# plot the half-hourly consumption data:
data = "half-hourly"
all_times = smart[data]['times']
datetimes = [sm.dt_from_dt64(t) for t in all_times]
datetimes = [datetimes[0] - (datetimes[1] - datetimes[0])] + datetimes
for supply in ['gas']:
    smart_data = smart[data][supply]
    is_smart = np.array([t in smart_data for t in all_times], bool)
    all_smart = np.array([smart_data[t]['consumption']
                         if t in smart_data else 0.0
                         for t in all_times])
    units = "kWh"
    if supply == 'gas':
        all_smart *= 3.6 / 39.5 / 1.02264 # convert from kWh to m^3
        units = "m^3"
# using the value (2^24-1)/1000 m^3 to flag up missing data is a BAD IDEA
# enforce a physical limit: nb U6 meter limit is ~6 m^3 per hour:
        all_smart = np.where(np.greater(all_smart, 50), 0.0, all_smart)
    if data == "half-hourly":
        all_smart *= 48
    units += " per day"
    model_data = np.array([sm.model(supply,t)
                         for t in all_times])
    estimated = np.where(is_smart, all_smart, model_data)
    error = np.where(is_smart, model_data - all_smart, 0.0)
    estimated_read = estimated.cumsum()/48
    k=1440
    x, y1 = sm.bars(datetimes, all_smart,k)
    x, y2 = sm.bars(datetimes, error,k)
    fig, (ax1, ax2, ax3) = plt.subplots(1,3)
    ax1.fill_between(x, y1)
    ax1.set_title(f"{supply} consumption")
    ax1.set_ylabel(f"{units}")
    ax1.set_xlabel("date:time")
    ax2.fill_between(x, y2)
    ax2.set_title(f"error in modelled consumption")
    fig, (ax3, ax4) = plt.subplots(2,1)
    ax4.plot(estimated_read)
# plot daily meter readings where available:
data = "daily"
all_times = smart[data]['times']
datetimes = [sm.dt_from_dt64(t) for t in all_times]
datetimes = [datetimes[0] - (datetimes[1] - datetimes[0])] + datetimes
for supply in ['electricity', 'gas']:
    smart_data = smart[data][supply]
    is_smart = np.array([t in smart_data for t in all_times], bool)
    lo_smart = np.array([smart_data[t]['meterReadings']['start']
                         if t in smart_data and
                            'meterReadings' in smart_data[t]
                         else 0.0
                         for t in all_times])
    hi_smart = np.array([smart_data[t]['meterReadings']['end']
                         if t in smart_data and
                            'meterReadings' in smart_data[t]
                         else 0.0
                         for t in all_times])
    x, y_lo = sm.bars(datetimes, lo_smart)
    x, y_hi = sm.bars(datetimes, hi_smart)
    fig, ax = plt.subplots()
    ax.fill_between(x, y_lo, y_hi)
plt.show()
    


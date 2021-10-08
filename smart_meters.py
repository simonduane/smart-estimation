"""\
                                smart_meters.py
        module version 03

There is some basic test code at the end here, guarded by

    if __name__ == "__main__":

but applications of this module are really best set up as independent scripts.


This version of the module introduces a model of demand, for use in predicting
consumption where smart usage data is unavailable. Meter reading estimation is
only possible if some assumptions about demand are made, and they're made
explicit here. (Consumption aka usage can be the same as demand, but only if the
installed system has the capacity to meet that demand - otherwise you get cold.)

    def model(supply, dt64):

Returns a prediction of usage (metered units per day), where

        supply = 'electricity'|'gas'
        dt64 is a numpy datetime64

The details of the model don't matter so much as its very existence.


    def read_cv(file="./calorific_value.csv"):

Returns a dictionary of national grid calorific values. I copy-pasted these
data from the NG website. I chose the data for the region where I live.


    def read_ovo(name="2019-12", dataset="daily",
                 path="./json/20WE/", verbose=False):

Returns information from an ovo smart meter dataset as a dictionary.

My local copies of these datasets are saved as files named

    "./json/20WE/daily/2019-12.json"
    "./json/20WE/half-hourly/2019-12-17.json"
    etc.


    def extend(s1, s2):

Returns the smart dataset dictionary result of "merging" two existing smart
dataset dictionaries.


    def dt_from_dt64(dt64):

Convert numpy datetime64 to python datetime.
I find numpy datetime64 works better as a dictionary key, while python datetime
makes for nicer tick labelling in matplotlib.


    def bars(a, b, k=1):

Returns (2N//k,), (2N//k,) arrays, given (N+1,), (N,) arrays, for bar charts.
Using k>1 is a cool way of aggregating usage for display.
"""

import calendar
import csv
import datetime as dt
import json
import math
import numpy as np
import os


def bars(a, b, k=1):
    "Returns two (2N//k + 2,) arrays, given two (N,) arrays. Good for bar charts."
    N = len(a)  # there are len(a) = N intervals,
    a_block = np.reshape(a[:k*(N//k)],(N//k,k))[:,k-1]      # all the block ends
    b_block = np.reshape(b[:k*(N//k)],(N//k,k))     # group the data into blocks
    b_block = b_block.sum(1)/k                      #       ... and average them
    x = [a_block[0], a_block[0]] # x-coord of the left side of the first bar ...
    y = [0.0, b_block[0]]                   # ... y-coords of its bottom and top
    for i in range(1,len(a_block)):     # for each bar, set the ...
        x += [a_block[i], a_block[i]]   # x-coord of the right side, and the ...
        y += [b_block[i-1], b_block[i]] # y of the tops of this bar and the next
    x += [a_block[-1], # the right of the last bar
          a_block[-1]] # is here in x, and ...
    y += [b_block[-1], 0.0]                         # goes from here down to y=0
    return np.array(x), np.array(y) # fill_between(x,y) is nicer than plot(x,y)


def cummax(a):
    "Returns an array, the cumulative maximum of a."
    m = [a[0]]
    for i,p in enumerate(a[:-1]):
# by keeping track of the latest result at each stage ...
        m.append(max(m[-1],a[i+1]))     # ... only one pair needs to be compared
    return np.array(m)


def dt_from_dt64(dt64):
    "Convert numpy datetime64 to python datetime - better for matplotlib plots."
    if type(dt64) != type(np.datetime64(0,"m")):
        raise Exception(f"{dt64} has bad type {type(dt64)}")
    s = str(dt64)                               # looks like "1970-01-01T00:01"
    return dt.datetime(int(s[:4]),int(s[5:7]),int(s[8:10]),     # (1970, 1, 1,
                       int(s[11:13]),int(s[14:16]))             #  0, 1)


def extend(s1, s2):
    "Return a copy of data dictionary s1, extended to include data from s2."
    s = s1.copy()
    s['times'] = np.append(s1['times'], s2['times'])
    for supply in ['electricity', 'gas']:
        s[supply] = {**s1[supply], **s2[supply]}    # assumes no keys in common
    return s


model_d = {'electricity':
                  {'d_0': 15,   # 15 Jan is around the time of maximum demand
                   'p': [1.0,   # dimensionless calibration coefficient
                         9.5,   # kWh/day (typical minimum) demand
                         0.0,   # kWh/day (average of seasonal part of) demand
                         0.0]}, # kWh/day (typical seasonal oart of max) demand
           'gas':
                  {'d_0': 15,   # 15 Jan is around the time of maximum demand
                   'p': [1.0,   # dimensionless calibration coefficient
                         0.85,  # kWh/day (typical minimum) demand
                         6.35,  # kWh/day (average of seasonal part of) demand
                         8.8]}} # kWh/day (typical seasonal oart of max) demand
A = 2 * math.pi / 365


def model(supply, dt64):
    "Returns the expected consumption in metered units per day."

    d = (dt64 - np.datetime64("2020-01-01","D")     # convert to time in days
         ) / np.timedelta64(1,"D")                  # elapsed since 2020-01-01
    if not (supply in model_d):
        raise Exception(f"bad supply: {supply}?")
    d_0 = model_d[supply]['d_0']
    p = model_d[supply]['p']
    return p[0] * (p[1] + max(0, p[2] + p[3] * math.cos(A * (d - d_0))))


def read_cv(file="./calorific_value.csv"):  # copy-pasted from NG website
    "Returns a dictionary of national grid calorific values."
    cv = {}
    with open(file) as cv_data: 
        cv_reader = csv.reader(cv_data)
        next(cv_reader)                 # skip one line of headings
        while True:
            try:
                date, v = next(cv_reader)
            except:
                break
            t = np.datetime64(f"20{date[6:8]}-{date[3:5]}-{date[:2]}"
                              .format(date), "m")
            cv[t] = round(float(v), 1)
    return cv


def read_ovo(name="2019-12", dataset="daily",
             path="./json/20WE/", verbose=False):
    "Returns information from an ovo file of smart meter data as a dictionary."
    if name[-5:] == ".json":
        name = name[:-5]
    f_name = path + dataset + "/" + name + ".json"
    if verbose:
        print(f"reading {f_name} ...")
    with open(f_name) as data:
        data_d = json.load(data)
    minutes = np.timedelta64(1, "m")    # the "unit" of time
    hh = 30 * minutes
    day = 48 * hh
    first_time = np.datetime64(name, "m")    # time of first interval
    if dataset == "half-hourly":
        duration = hh
        period = 48 * hh
        first_time += duration # correcting ovo's mis-labelling
    elif dataset == "daily":
        duration = day
        period = calendar.monthrange(int(name[:4]), int(name[5:7]))[1] * day
    else:
        raise Exception(f"Sorry, filename {name} not understood")
# intervals are labelled by their end times (OVO please note)
    after_time = first_time + period       # also, the first time of next period
    all_times = np.arange(first_time, after_time, step=duration) #- duration
    smart = {'times': all_times}      # end times of all intervals in the period
    for supply in data_d: 
        smart_list = data_d[supply]['data'] # the smart data as a list ...
        smart[supply] = {}
        for s in smart_list:
            key = np.datetime64(s['interval']['start'][:-7],"m")
            if dataset == "half-hourly":
                key -= duration
            smart[supply][key] = s  # ... and as a dictionary (with correct key)
    return smart


if __name__ == "__main__":
    datasets = ["daily", "half-hourly"]
    supplies = ["electricity", "gas"]
    colors = {"electricity": "orange", "gas": "blue"}       # ovo colour scheme
    smart = {}
    axes = {}
# read just enough smart meter data (readings and usage) to make sensible plots
    for (data, n) in [("daily", 2), ("half-hourly", 27)]:
        f_path = (f"./json/20WE/")
        f_all = os.listdir(f_path + data)
        f_all.sort()
        smart[data] = read_ovo(f_all[0], data, f_path)
        for f in f_all[1:]: # f_all[1:n]:      # temporary hack - read it all in
            s = read_ovo(f, data, f_path)
            smart[data] = extend(smart[data], s)
        print(f"{len(smart[data]['times'])} records of {data} data read ...")
        all_times = smart[data]['times']
        datetimes = [dt_from_dt64(t) for t in all_times]
        axes[data] = {}
# plot the early data: the user should zoom in interactively to verify timing
    import matplotlib.pyplot as plt
    fig = plt.figure()
    iplot = 220
    for data in datasets:
        all_times = smart[data]['times']
        datetimes = [dt_from_dt64(t) for t in all_times]
        for supply in supplies:
            iplot += 1
            if data == "daily" and supply == "electricity":
                axes[data][supply] = fig.add_subplot(iplot) # tie others to this
            else:
                axes[data][supply] = fig.add_subplot(   # time axes zoom as one
                                iplot, sharex = axes["daily"]["electricity"]
                                                     )
            smart_data = smart[data][supply]
            is_smart = np.array([t in smart_data for t in all_times], bool)
            if data == "daily":
                lo_smart = [smart_data[t]['meterReadings']['start']
                                     if t in smart_data and
                                        'meterReadings' in smart_data[t]
                                     else 0.0
                                     for t in all_times]
                lo_smart = cummax(lo_smart)
                hi_smart = np.array([smart_data[t]['meterReadings']['end']
                                     if t in smart_data and
                                        'meterReadings' in smart_data[t]
                                     else 0.0
                                     for t in all_times])
                hi_smart = cummax(hi_smart)
                x, y_lo = bars(datetimes, lo_smart)
                x, y_hi = bars(datetimes, hi_smart)
                axes[data][supply].fill_between(x, y_lo, y_hi,
                                                color=colors[supply])
            else:
                usage = np.array([smart_data[t]['consumption']
                                  if t in smart_data and
                                     smart_data[t]['consumption'] < 50
                                  else 0.0
                                  for t in all_times])
                x, y = bars(datetimes, usage, k=1)
                axes[data][supply].fill_between(x, y, color=colors[supply])
    axes["daily"]["electricity"].set_title("electricity (units = kWh)")
    axes["half-hourly"]["electricity"].set_xlabel("datetime (M-D hh:mm)")
    axes["half-hourly"]["electricity"].set_ylabel("usage (units)")
    axes["daily"]["electricity"].set_ylabel("meter reading (units)")
    axes["daily"]["gas"].set_title("gas (units = m^3)")
    axes["half-hourly"]["gas"].set_xlabel("datetime (M-D hh:mm)")
    plt.show()

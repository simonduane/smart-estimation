"""\
                                smart_meters.py
        module version 03
"""

import calendar
import csv
import datetime as dt
import json
import math
import numpy as np
import os


def groups(a, b, k=1):
    """\
Returns (2N//k,)-shaped arrays of x, y  given (N,)-shaped arrays of x, y.

For plotting group averages over the appropriate interval.
First two intervals assumed to be of equal duration.
Group size may be 1.
"""
    N = len(b)                                      # number of intervals
    a_group = np.reshape(a[:k*(N//k)],(N//k,k))[:,k-1]      # all the group ends
    b_group = np.reshape(b[:k*(N//k)],(N//k,k))     # data taken in groups ...
    b_group = b_group.sum(1)/k                      #...  of size k and averaged
    x = [a_group[0] + (a_group[1] - a_group[0])]    # first group start ...
    y = [b_group[0]]                                #  ... and its average level
    for i,a in enumerate(a_group[:-1]):          # for each interior boundary ...
        x += [a_group[i], a_group[i]]           # ... set x (both groups)
        y += [b_group[i], b_group[i+1]]         # ... and y (both groups)
    x += [a_group[-1]]                              # the last x ...
    y += [b_group[-1]]                              #      ... and y
    return np.array(x), np.array(y) # fill_between(x,y) or fill_between(x,y1,y2)


def cummax(a):
    "Returns an array, the cumulative maximum of a."
    m = [a[0]]
    for i,p in enumerate(a[:-1]):       # keep track of the latest result so ...
        m.append(max(m[-1],a[i+1]))     # ... only one pair needs to be compared
    return np.array(m)


def dt_from_dt64(dt64):
    "Convert numpy datetime64 to python datetime - better for matplotlib plots."
    if type(dt64) != type(np.datetime64(0,"m")):
        raise Exception(f"{dt64} has bad type {type(dt64)}")
    s = str(dt64)                                           # "1970-01-01T00:01"
    return dt.datetime(int(s[:4]),int(s[5:7]),int(s[8:10]), # (1970, 1, 1, 0, 1)
                       int(s[11:13]),int(s[14:16]))


def extend(s1, s2):
    """\
Return a copy of data dictionary s1, extended to include data from s2.

Dictionaries s1 and s1 are assumed to be contiguous smart meter datasets.
"""
    s = s1.copy()
    s['times'] = np.append(s1['times'], s2['times'])
    for supply in ['electricity', 'gas']:
        s[supply] = {**s1[supply], **s2[supply]}    # assumes no keys in common
    return s

# Simple model of seasonal variations in consumption (may be customer-specific)

model_d = {'electricity':       # not at all seasonal
                  {'d_0': 15,   # day number of maximum demand in year (15 Jan)
                   'p': [1.0,   # dimensionless calibration coefficient
                         9.5,   # kWh/day (typical minimum) demand
                         0.0,   # kWh/day (average of seasonal part of) demand
                         0.0]}, # kWh/day (typical seasonal oart of max) demand
           'gas':               # predominantly seasonal
                  {'d_0': 15,   # day number of maximum demand in year (15 Jan)
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


def read_ovo(name="2019-12", dataset=None,
             path="./data/", verbose=False):
    "Returns information from an ovo file of smart meter data as a dictionary."
    if name[-5:] == ".json":
        name = name[:-5]
    if len(name) == 7:
        frequency = "daily"
    elif len(name) == 10:
        frequency = "half-hourly"
    else:
        raise Exception(f"Sorry, filename {name} not understood")
    minutes = np.timedelta64(1, "m")    # the "unit" of time
    hh = 30 * minutes       # "half-hourly" data have a day of 30 min intervals
    day = 48 * hh                 # "daily" data have a month of 1 day intervals
    if frequency == "daily":
        duration = day
        period = calendar.monthrange(int(name[:4]), int(name[5:7]))[1] * day
    if frequency == "half-hourly":
        duration = hh
        period = day
    if dataset == None:
        dataset = frequency
    f_name = path + dataset + "/" + name + ".json"
    if verbose:
        print(f"reading {f_name} ...")
    with open(f_name) as data:
        data_d = json.load(data)
    this_time = np.datetime64(name, "m")  # start of first interval, this period
    this_time += duration               # end of first interval, this period
    """\
ovo PLEASE NOTE: ALL DATA WILL BE KEYED BY INTERVAL END TIMES: 
METER READINGS WILL BE KEYED BY THEIR DATETIME (obviously)
"USAGE" WILL BE KEYED BY THE END OF THE PERIOD IN WHICH THE CONSUMPTION HAPPENED
"""
    next_time = this_time + period      # end of first interval, next period
    all_times = np.arange(this_time, next_time, step=duration)
    smart = {'times': all_times}        # these are all the times we need
    for supply in data_d: 
        smart_list = data_d[supply]['data'] # the smart data as a list ...
        smart[supply] = {}
        for s in smart_list:
            key = np.datetime64(s['interval']['start'][:-7],"m")
            key += duration             # this should be the interval end time
            if frequency == "half-hourly":
                key -= duration         # except ovo mislabel this dataset
            smart[supply][key] = s      # these data are all correctly keyed
    """\
ovo's error:

THE FIRST CONSUMPTION IN AN ovo HALF-HOURLY FILE HAPPENED IN THE 30 MIN INTERVAL
ENDING AT THE MIDNIGHT WHICH STARTS THE DAY - (ovo label it wrongly)

THE FIRST PAIR OF METERREADINGS IN AN ovo DAILY FILE ARE THE OPENING AND CLOSING
METER READINGS, BOTH NEAR MIDNIGHT, FOR THE FIRST DAY OF THE MONTH - (correct)

(all ovo's times are UTC, no correction for daylight savings, which is good.)
"""
    return smart


if __name__ == "__main__":
    frequencies = ["daily", "half-hourly"]
    supplies = ["electricity", "gas"]
    colors = {"electricity": "orange", "gas": "blue"}       # ovo colour scheme
    smart = {}
    axes = {}
    for p in frequencies:
        f_path = (f"./data/")
        f_all = os.listdir(f_path + p)
        f_all.sort()                                # chronological order
        smart[p] = read_ovo(f_all[0], p, f_path)    # read the first file ...
        for f in f_all[1:]:                         #... and all the other files
            s = read_ovo(f, p, f_path)
            smart[p] = extend(smart[p], s)          # must be chronological
        print(f"{len(smart[p]['times'])} records of {p} data read ...")
        all_times = smart[p]['times']
        datetimes = [dt_from_dt64(t) for t in all_times]
        axes[p] = {}
# plot the readings and "usage" in an interactive widget: zoom in as you like
    import matplotlib.pyplot as plt
    fig = plt.figure()
    iplot = 220
    for p in frequencies:
        all_times = smart[p]['times']
        datetimes = [dt_from_dt64(t) for t in all_times]
        for supply in supplies:
            iplot += 1
            if p == "daily" and supply == "electricity":
                axes[p][supply] = fig.add_subplot(iplot) # share this time axis
            else:
                axes[p][supply] = fig.add_subplot(
                                iplot, sharex = axes["daily"]["electricity"]
                                                  )      # so they zoom together
            smart_data = smart[p][supply]
            is_smart = np.array([t in smart_data for t in all_times], bool)
            if p == "daily":
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
                x, y_lo = groups(datetimes, lo_smart)
                x, y_hi = groups(datetimes, hi_smart)
                axes[p][supply].fill_between(x, y_lo, y_hi,
                                             color=colors[supply])
            else:
                usage = np.array([smart_data[t]['consumption']
                                  if t in smart_data and
                                     smart_data[t]['consumption'] < 50
                                  else 0.0
                                  for t in all_times])
                if supply == "gas":
                    usage = usage * 3.6 / 39.5 / 1.02264
                usage = usage * 48
                x, y = groups(datetimes, usage, k=48)
                axes[p][supply].fill_between(x, y, color=colors[supply])
                axes[p][supply].set_xlabel("datetime (Y-M-D h:m)")
    axes["daily"]["electricity"].set_title("electricity (units = kWh)")
    axes["half-hourly"]["electricity"].set_ylabel(
                                    "consumption (units)\na.k.a. 'usage'"
                                                  )
    axes["daily"]["electricity"].set_ylabel("meter reading (units)")
    axes["daily"]["gas"].set_title("gas (units = m^3)")
    plt.show()

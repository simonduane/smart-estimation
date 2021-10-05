"""\
                            smart_meters.py
    version 03

In this version I develop model-based estimation of smart meter readings.
In development, I found that showing half-hourly usage data hides information
(because those values vary very widely within a single day). The model has only
the longer term trend in daily variations, and even that can easily be hidden by
the random day to day variations.
I realise that looking at weekly sums is probably a smart move...
In any case, reshaping and summing is crucial.


    def model(supply, day):

Returns a prediction of usage (metered units per day) where
        supply = 'electricity'|'gas'
        0 <= day <= 366
The details of the model don't really matter, but there must be a model


    def read_cv(file="./calorific_value.csv"):

Returns a dictionary of national grid calorific values. I copy-pasted these
data from the NG website. I chose the data for the region where I live.


    def read_ovo(name="2019-12", dataset="daily",
                 path="./json/20WE/", verbose=False):

Returns information from an ovo set of smart meter data as a dictionary. I have
saved local copies of the datasets as files named
    "./json/20WE/daily/2019-12.json"
    "./json/20WE/half-hourly/2019-12-17.json"
    etc.
and the input dataset is selected by name.


    def extend(s1, s2):

Returns the smart dataset dictionary result of "merging" two existing smart
dataset dictionaries.


    def dt_from_dt64(dt64):

Convert numpy datetime64 to python datetime - numpy datetime is better for use
in dictionary keys, python datetime is better for time axis labelling in plots.


    def bars(a, b):
"Returns (2N,), (2N,) arrays, given (N+1,), (N,) arrays, for bar charts."


    if __name__ == "__main__"

Some examples of simple use...
"""
import calendar
import csv
import datetime as dt
import math
import matplotlib.pyplot as plt
import numpy as np
import json
import os

model_d = {'electricity':
                  {'d_0': 0,    # day of maximum demand (1 Jan)
                   'p': [1.0,   # fiddle factor (dimensionless)
                         7.8,   # typical minimum demand (kWh/day)
                         0.0,   # average seasonal part of demand (kWh/day)
                         0.0]}, # typical peak seasonal demand (kWh/day)
           'gas':
                  {'d_0': 25,   # day of maximum demand (25 Jan)
                   'p': [0.8,   # fiddle factor (dimensionless)
                         0.85,  # typical minimum demand (m^3/day)
                         9.7,   # average seasonal part of demand (m^3/day)
                         10]}}  # typical peak seasonal demand (m^3/day)
           
A = 2 * math.pi / 365


def model(supply, dt64):
    "Returns the expected consumption in metered units per day."

    d = (dt64 - np.datetime64("2020-01-01","D")) / np.timedelta64(1,"D")
    if not (supply in model_d.keys()):
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
    if name[-4:] != "json":
        name = name + ".json"
    f_name = path + dataset + "/" + name
    if verbose:
        print(f"reading {f_name} ...")
    with open(f_name) as data:
        data_d = json.load(data)
    minutes = np.timedelta64(1, "m")   # this should be used as a "unit" of time
    hh = 30 * minutes
    day = 48 * hh
    opening_time = np.datetime64(name[:-5], "m") # start of first interval
    if len(name) == 15:                 # eg "2019-12-17"
        duration = hh
        period = 48 * hh
    elif len(name) == 12:                # eg "2019-12"
        duration = day
        period = calendar.monthrange(int(name[:4]), int(name[5:7]))[1] * day
        opening_time += duration        # shift to end of first interval
    else:
        raise Exception(f"Sorry, filename {name} not understood")
    closing_time = opening_time + period
    all_times = np.arange(opening_time, closing_time, step=duration)
    smart = {'times': all_times}        # end times of all intervals in the day
    for supply in data_d.keys():    # list the smart data, and make a dictionary
        smart_list = data_d[supply]['data']
        smart[supply] = {}
        for s in smart_list:
            key = np.datetime64(s['interval']['start'][:-7],"m")
            smart[supply][key] = s
    return smart


def extend(s1, s2):
    "Return a copy of data dictionary s1, extended to include data from s2."
    s = s1.copy()
    s['times'] = np.append(s1['times'], s2['times'])
    for supply in ['electricity', 'gas']:
        s[supply] = {**s1[supply], **s2[supply]}
    return s


def dt_from_dt64(dt64):
    "Convert numpy datetime64 to python datetime - better for matplotlib plots."
    if type(dt64) != type(np.datetime64(0,"m")):
        raise Exception(f"{dt64} has bad type {type(dt64)}")
    s = str(dt64)
    return dt.datetime(int(s[:4]),int(s[5:7]),int(s[8:10]),
                       int(s[11:13]),int(s[14:16]))


def bars(a, b):
    "Returns (2N,), (2N,) arrays, given (N+1,), (N,) arrays, for bar charts."
    x, y = [a[0]], [0.0]
    for i,p in enumerate(b):
        x += [a[i], a[i+1]]
        y += [b[i], b[i]]
    x += [a[-1]]
    y += [0.0]
    return np.array(x), np.array(y)


if __name__ == "__main__":
# read in all my smart data:
    smart = {}
    for data in ["daily", "half-hourly"]:
        f_path = (f"./json/20WE/")
        f_all = os.listdir(f_path + data)
        f_all.sort()
        smart[data] = read_ovo(f_all[0], data, f_path)
        for f in f_all[1:]:
            s = read_ovo(f, data, f_path)
            smart[data] = extend(smart[data], s)
        print(f"{len(smart[data]['times'])} records of {data} data read ...")
# plot the half-hourly consumption data:
    data = "half-hourly"
    all_times = smart[data]['times']
    datetimes = [dt_from_dt64(t) for t in all_times]
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
        model_data = np.array([model(supply,t)
                             for t in all_times])
        estimated = np.where(is_smart, all_smart, model_data)
        error = np.where(is_smart, model_data - all_smart, 0.0)
        weeks = int(len(error)/(48*7))
        weekly_err = error[:weeks*48*7].reshape((weeks,48*7))
        estimated_read = estimated.cumsum()/48
        print((weekly_err * weekly_err).sum())
##        x, y1 = bars(datetimes, all_smart)
##        x, y2 = bars(datetimes, error)
##        fig, (ax1, ax2, ax3) = plt.subplots(1,3)
##        ax1.fill_between(x, y1)
##        ax1.set_title(f"{supply} consumption")
##        ax1.set_ylabel(f"{units}")
##        ax1.set_xlabel("date:time")
##        ax2.fill_between(x, y2)
##        ax2.set_title(f"error in modelled consumption")
##        fig, (ax3, ax4) = plt.subplots(2,1)
##        ax3.plot(weekly_err.sum(axis=1))
##        ax4.plot(estimated_read)
##        plt.show()
# plot daily meter readings where available:
    data = "daily"
    all_times = smart[data]['times']
    datetimes = [dt_from_dt64(t) for t in all_times]
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
        x, y_lo = bars(datetimes, lo_smart)
        x, y_hi = bars(datetimes, hi_smart)
        fig, ax = plt.subplots()
        ax.fill_between(x, y_lo, y_hi)
        plt.show()
        
    

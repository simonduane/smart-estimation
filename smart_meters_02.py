"""\
                            smart_meters.py
version 02

Reads smart meter data from a local copy of ovo "API" files and puts them into
Python dictionaries. This facilitates processing which is robust when some data
are missing. The first step in that processing is to populate numpy arrays.
This is illustrated here by plotting usage, and converting gas usage from energy
(in kWh) to metered units (in m^3).
Rogue values for gas usage are cleaned. It looks like ovo uses/used the value
(2^24-1)/1000, in m^3, as an indicator for bad or missing data. Not good enough.
"""
import calendar
import csv
import numpy as np
import json
import os

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

def read_ovo(name, path, verbose=False):
    "Returns information from an ovo file of smart meter data as a dictionary."
    f_name = path + name
    if verbose:
        print(f"reading {name} ...")
    with open(f_name) as data:
        data_d = json.load(data)
    minutes = np.timedelta64(1, "m")    # express all times in minutes
    hh = 30 * minutes
    day = 48 * hh
    opening_time = np.datetime64(name[:-5], "m")
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
    for supply in data_d.keys():     # list the smart data, and make a dictionary
        smart_list = data_d[supply]['data']
        smart[supply] = {}
        for s in smart_list:
            key = np.datetime64(s['interval']['start'][:-7],"m")
            smart[supply][key] = s
    return smart

def smart_extend(s1, s2):
    "Return a copy of data dictionary s1, extended to include data from s2."
    s = s1.copy()
    s['times'] = np.append(s1['times'], s2['times'])
    for supply in ['electricity', 'gas']:
        s[supply] = {**s1[supply], **s2[supply]}
    return s

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    smart = {}
    for data in ["daily", "half-hourly"]: # convert everything I have
        f_path = (f"./json/20WE/{data}/")
        f_all = os.listdir(f_path)
        f_all.sort()
        smart[data] = read_ovo(f_all[0], f_path)
        s = read_ovo(f_all[1], f_path)
        for f in f_all[2:]:
            smart[data] = smart_extend(smart[data], s)
            s = read_ovo(f, f_path)
        smart[data] = smart_extend(smart[data], s)
        print(f"{len(smart[data]['times'])} records of {data} data read ...")
# plot the half-hourly data:
    data = "half-hourly"
    all_times = smart[data]['times']
    for supply in ['electricity', 'gas']:
        smart_data = smart[data][supply]
        all_data = np.array([smart_data[t]['consumption']
                             if t in smart_data else 0.0
                             for t in all_times])
        if supply == 'gas':
            all_data *= 3.6 / 39.5 / 1.02264 # convert from kWh to m^3
            all_data = np.where(np.greater(all_data, 50), 0.0, all_data) # clean
        plt.plot(all_times, all_data)
        plt.show()

# Python module `smart_meters.py`

## A note on JSON format

This is used to specify the structure of smart meter data. The Ovo API is what forced me to learn about JSON, in which data objects are represented by strings. https://www.w3schools.com/js/js_json_intro.asp seems to be as good a resource as any, and what I learned is summarised in the table, which shows how JSON entities map onto Python objects in my code:

| JSON                         | Python                      |
| ---------------------------- | --------------------------- |
| string                       | string (use double quotes)  |
| number                       | int or float                |
| object                       | dictionary (syntax matches) |
| array                        | list (syntax matches)       |
| boolean (true\|false)        | bool (True\|False)          |
| null                         | None                        |
| (strings are used for dates) | (use datetimes)             |

## Interactive use of smart_meters

The module can be used at the interactive Python prompt as well as in scripts.

For example:

```python
>>> import numpy as np
>>> import smart_meters as sm
>>> smart = {}
>>> smart['daily'] = sm.read_ovo('2021-10', 'daily', './json/my_pet_name/')
>>> smart['daily'].keys()
dict_keys(['times', 'electricity', 'gas'])
>>> smart['daily']['times']
array(['2021-10-01T00:00', '2021-10-02T00:00', '2021-10-03T00:00',
       '2021-10-04T00:00', '2021-10-05T00:00', '2021-10-06T00:00',
       '2021-10-07T00:00', '2021-10-08T00:00', '2021-10-09T00:00',
       '2021-10-10T00:00', '2021-10-11T00:00', '2021-10-12T00:00',
       '2021-10-13T00:00', '2021-10-14T00:00', '2021-10-15T00:00',
       '2021-10-16T00:00', '2021-10-17T00:00', '2021-10-18T00:00',
       '2021-10-19T00:00', '2021-10-20T00:00', '2021-10-21T00:00',
       '2021-10-22T00:00', '2021-10-23T00:00', '2021-10-24T00:00',
       '2021-10-25T00:00', '2021-10-26T00:00', '2021-10-27T00:00',
       '2021-10-28T00:00', '2021-10-29T00:00', '2021-10-30T00:00',
       '2021-10-31T00:00'], dtype='datetime64[m]')
>>> smart['daily']['electricity'].keys()
dict_keys([numpy.datetime64('2021-10-01T00:00'), numpy.datetime64('2021-10-02T00:00'), numpy.datetime64('2021-10-03T00:00'), numpy.datetime64('2021-10-04T00:00'), numpy.datetime64('2021-10-05T00:00'), numpy.datetime64('2021-10-06T00:00'), numpy.datetime64('2021-10-07T00:00')])
>>> smart['daily']['gas'].keys() == smart['daily']['electricity'].keys()
True
>>> smart['daily']['electricity'][np.datetime64('2021-10-01T00:00')]
{'hasHhData': True, 'consumption': 9.34, 'interval': {'start': '2021-10-01T00:00:00.000', 'end': '2021-10-01T23:59:59.999'}, 'cost': {'currencyUnit': 'GBP', 'amount': '1.43'}, 'rates': {'anytime': 0.1535, 'standing': 0.274}}
>>> 
```

This transcript illustrates that the function `read_ovo` returns a dictionary with all the information from the file `2021-10.json`. This information was in turn scraped from Ovo's web API using another script in the respository, `get_ovo_data.py`, explained later in these notes.

The dictionary returned by `read_ovo` has three keys and the corresponding values are 

- `smart['daily']['times']`: an array containing a complete list of datestamps, one for each day in the month. This despite, at the time of doing this, most of those days remaining in the future.
- `smart['daily']['electricity']`: a dictionary of smart electricity meter data, keyed on datestamp
- `smart['daily']['gas']`: a dictionary of smart gas meter data, also keyed on datestamp

I find it convenient to put all my smart meter data, from multiple files, into a single dictionary. The module includes a utility function `extend` which merges smart meter data dictionaries in the way needed to achieve this.

There are some superfluous and useless values in the 'daily' files, so called interval end times, which are each 1 ms before the midnight that marks the actual end of the day. With all due respect, the presence of such a value suggests to me that whoever wrote the code behind Ovo's API doesn't really understand the structure of smart meter data and how to process it. As if to confirm this lack of understanding I found, when trying to validate Ovo's 'half-hourly' data (which also include such "end" times, all 1 ms before the actual end times), that the so-called interval "start" time marks the ***end*** of the 30 minute interval in which the reported 'consumption' energy was actually consumed (and the time is UTC, without any adjustment for daylight savings time, though Ovo don't explicitly say that, so far as I'm aware).

I shall move on from this confusion here, for now. The scripts in this repository sidestep these infelicities: interval end times are never used and half-hourly "usage" data are processed correctly according to when that energy was really consumed. (All my times are UTC, and no adjustment for daylight savings time is made, ever.)

The daily files contain valid and correctly timestamped meterReadings, provided one understands that the uncertainty in timing is a few minutes, compared to the uncertainty in timing for the half-hourly data which is, so far as I can tell, at most a second or two.

***At least, they used to contain meterReadings, until Ovo changed their API in June 2021. Since then, actual meter readings are absent from the data made available by the API (the change is retroactive: even the readings prior to June 2021 have been removed from the record).***

I am lost for polite words, but have hand crafted two additional files of meter readings (representative sample readings have yet to be put on GitHub). One file contains the readings on all my monthly statements. These meter readings have very low frequency but they are at least to full precision (since the billing system on my account was changed in June 2020. The other file contains smart meter readings as listed by the Ovo Energy Android app. These are daily, and so of the required frequency, but are subject to the effects of missing data and have been rounded to the nearest integer. This is still better than nothing.

## Web scraping

The internet is a hostile environment and, up to a point, web servers make efforts to resist automated attacks. The downloading of data from a web API, a.k.a. web scraping, could be misconstrued by the server as a hostile attack and scripts need to take this into account. However developers of the code that runs on web servers depend on automated testing and, as a result, web servers will tolerate a degree of automated interaction, provided the "user" behaves in a plausibly human-like way. It is the responsibility of the script to do this.

### `get_ovo_data.py`

The script needs to be edited (lines 21-24) to contain information relating to your Ovo account and can then be run from a shell (command) prompt. It will work if you have more than one account (as I used to) but, as provided, the list of accounts in the script has only one item, and the dictionary of account numbers has only one key/value pair. 

The Python selenium package is used to launch a web browser which the script then uses to navigate the API and capture data. Use of the script is possible once you have installed and configured selenium. More information at https://www.selenium.dev/selenium/docs/api/py/index.html.

The script checks for the existence of local data directories to which it will write its output files[^1]. The script launches a web browser which invites you to login[^2] to My Ovo, and then the script "drives"[^3] the browser to download the smart meter data. I have included random pauses (of 1-3 seconds duration) in the hope that this will make the interaction sufficiently human-like that the server doesn't blacklist me.

[^1]: It doesn't create the directories for you, but it will overwrite existing files where names match. I was bitten by this and survived, but I have left this feature in, ready to bite you too. Consider yourself warned.

[^2]: The script does not contain your login details, you have to type those in every time, and you also have to accept cookies, immediately after logging in, for the web scraping to work.

[^3]: Jargon that means: navigates the URLs in the API and parses what it receives.

Once the downloading has finished, the script reminds the user to log out from My Ovo.

The script output is described below.

### Ovo's smart meter dataset

Once per day, usually in the early hours of the morning, Ovo extends the data made available via the API. As far as the files output by my script are concerned, the new data leads to one extra item in the existing current month's "daily" file (actually the old file is overwritten by a new file), and one extra "half-hourly" file. At the start of each new month, a new current "daily" file is created and updates of the old one cease.[^4] Each file contains two lists, `"electricity"` and `"gas"` and each list item is a JSON object.

[^4]: NB: These names "daily" and "half-hourly" refer to the frequency of data within the file, not the frequency with which the files are created or updated.

The routine `smart_meters.read_ovo` reads a local file created by this web scraping - it doesn't go online to do the web scraping itself. The routine returns a dictionary containing all the information in one file, information previously scraped from the web API, as key/value pairs. The point of the routine is to convert the lists into dictionaries. This conversion is the key (pun intended) to understanding and solving Ovo's missing data problem.

#### Ovo's missing data problem

Smart meter communications is not completely reliable: some attempts to retrieve data fail. Further attempts may be made to retrieve the same data and sometimes succeed but, sometimes, the failure is because the data never existed in the first place. Repeated attempts to retrieve particular data are generally worth making but can't be relied on to solve the missing data problem. I believe that Ovo's missing data problem is made worse by their apparent choice to store their core information in lists. This is unhelpful, because missing data amounts to a list being short of one or more items. 

A complete list can be identified as such by asking how long it is (for example, there are 48 half-hour intervals per day, and there are 31 days in the current month, October) but, if a half-hourly list contains only 47 items, it takes effort to work out which item is missing. The better choice would have been to store the same information in a dictionary, keyed on the datetime of the values. A data item can be identified as missing if and only if its timestamp is ***not*** among the keys of the dictionary.[^5]

[^5]: That last sentence is a little awkward to express, and I found my code immediately became clearer when I refactored things to use a flag `is_smart` instead of `missing`: a data item is processed in one way if it is smart, and another way otherwise. The other way is where estimates of usage come into play, and the trick is only to estimate where absolutely necessary. 

#### From lists to dictionaries

Each list item includes a datetime value, and this is taken as the dictionary key. Everything else in the item makes up the dictionary value. 

Where the information is a meter reading, the timestamp is the (nominal) time at which that value was (or could have been) obtained by reading the meter. 

Where the information is "consumption", the time information is really an interval with a start and an end. It may not be immediately obvious, but the dictionary key has to be the time at the end of the interval: aside from anything else, this "consumption" only becomes fully defined, having a value, at the moment that interval ends. Of course, the interval has a duration, which is the elapsed time between the start and end of the interval. But that interval duration is a property of the whole list of smart meter consumption values, not the individual items in the list, because the individual intervals share a common duration.

It is possible to regard a list of N meter readings as defining a list of N-1 consumption values. Again, it may not be immediately obvious but, because meter readings exist on their own, independent of any other reading, they are not necessarily the start or end of any period, the durations of the intervals associated with those N-1 consumption values are not necessarily all the same. Those durations are associated with the items in that list.

### My smart meter dataset

Smart meter data are processed using two lists, one of reading values, and another of consumption values. Lists are actually fine, and to be preferred over dictionaries (which are slower to process), but they ***must*** be complete. So long as those lists might be incomplete, dictionaries have to be used instead. Therefore, smart meter data should be stored in dictionaries but processed as "completed" lists in which any gaps have been filled by inserting estimated values.

The primary estimate is of consumption - estimated meter readings are derived by totting up the consumption (whether based on smart meter data or on estimates) since the most recent prior actual reading.

The error in an estimated reading is entirely due to the errors in estimated consumption, and estimation of consumption relies on modelling. The model can be as crude as you like, but it has to respect physical constraints, such as not being negative (negative consumption would be registered on a different meter) and not exceeding the rating of the supply. For example my domestic electricity supply is rated at 100 A, and so the maximum demand is about 25 kW, and the half-hourly consumption value really can't be bigger than 12.5 kWh (otherwise a circuit breaker will trip). Similarly, I have a U6 gas meter, so the flow is unlikely to exceed 6 m^3 per hour and the half-hourly consumption value can't be much bigger than 3 m^3 (which is about 32 kWh), depending on the supply pipe size and the local supply pressure.


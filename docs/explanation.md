## JSON format

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

The routine `smart_meters.read_ovo` reads the a local file created by this web scraping - it doesn't go online to do the web scraping itself. The routine returns a dictionary containing all the information in one file, information previously scraped from the web API, as key/value pairs. The point of the routine is to convert the lists into dictionaries. This conversion is the key (pun intended) to understanding and solving Ovo's missing data problem.

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


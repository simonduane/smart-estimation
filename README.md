# smart-estimation (version 02)
My activity on this was prompted by evident shortcomings in Ovo's data.

The comments below represent a snapshot, taken at a point where I think I've made significant progress towards doing better: I have a tool to facilitate detailed investigation. As a start, I'll describe what are the problems in how Ovo stores their data, an alternative (my way to store the data), and what my solution to their missing data problem looks like.

### Two frequencies - daily and half-hourly

Smart meters register consumption continuously, and are designed to record this consumption at 30 minute intervals. That record consists of increments in the register value (a.k.a. meter reading), and they are stored locally (in the *Communications Hub*, or **Comms Hub**) and accessed remotely via a private network (to which the gatekeepers are DCC). They may be "my" data, I am only allowed access it if I'm a DCC *Authorised User*, and acquiring such a status costs money - hence the emergence of Hildebrand, Carbon, et al. who, as *Other Authorised Users* of DCC can access my data for me, and offer do that "for free", provided I let them save and use my data for their own purposes (GDPR means they have to tell me what those purposes are, but they are potentially lucrative, otherwise they wouldn't make the offer). As always, if you sign up to a "free" service, that just means that you (or your data) are a form of payment that the service provider is entirely happy to accept.

As a utility company selling me energy, Ovo are the only ones who ***must*** have access to data from "my" smart meter (the data may be mine, but the meter is theirs.) Ovo's choice (with my consent) is to ask DCC, at a time close to midnight, every 24 hours, to retrieve a daily summary of usage (48 increments in the meter reading) and one meter reading. The increments are just that: on their own, they give no information about what the meter reading is, only the amount by which it has changed. That is why it is important to retrieve the meter reading. Aside from anything else, it's one of those meter readings that appears as the closing reading on the monthly statement (and the same number appears as the opening reading on the following month's statement).

As far as I can tell (the SMETS standards are not as explicit as they need to be for me to make unambiguous sense of them), the Comms Hub doesn't necessarily save a history of meter readings. It may not have any more than access to the current register value. The history it saves (as required by the SMETS standards) is 13 months' worth of half-hourly usage data. Each 30 minute interval can be regarded as having an opening meter reading and a closing meter reading, but those readings are not explicitly saved anywhere. My own tests have convinced me that each of those readings is a value that was in the register at a time, (within a second or so of being) on the hour and half hour, UTC (Universal Coordinated Time). The value would have been shown as "the meter reading", if a button on the meter had been pressed at just the right moment, and that moment would have been within a second or so of being on the hour or half-hour. (I'm labouring the point, but I fear that there is risk of confusion if this is not properly understood at the outset.)

When Ovo ask DCC to retrieve a meter reading for them, there is simply no guarantee that the request will reach the Comms Hub exactly on the stroke of midnight. In practice, as far as I can tell, it's several minutes off, sometimes more.

The data that Ovo make available (through an "API" that is not supported for public use, but it's there and I use it) are presented in sets of "half-hourly" and of "daily" values. For whatever reason (e.g. unreliable communications) these sets are not all complete. If they were complete, the "half-hourly" data would consist of 48 values, one for each of the 30 minute intervals between one midnight and the next, with each value being an increment in the meter reading. Those values are energies, in kWh, for electricity, and what should be a volumes, in m^3 for gas. Ovo's first mistake, in my humble opinion, is to save energy in kWh instead of volume in m^3 for gas. Because what the meter registers is volume of gas in m^3, not its energy content in kWh. That's why the monthly statement says what it does.

As it happens, Ovo use a conventional calorific value, 39.5 MJ/m^3, for the half-hourly data, instead of the "true" value as published by the National Grid the following day, so this isn't really a problem. It's only a nominal value, the units deserve to be put in quotation marks, "kWh". I can apply the conversion factor and, provided I use the precise value of "kWh", I am reassured that the result is always an integer multiple of 0.001 m^3. Meters register values with 3 decimal places. No more, no fewer. It's a trivial matter, but that is another reason why storing the increment as a gas volume rather than an energy content would be better - it actually requires less space. Moving on...

That meter reading, taken around midnight, could sensibly be saved with those (up to) 48 increments. It's a pretty close approximation to the meter reading that would be most useful, i.e. the meter reading ***at*** midnight. Instead, Ovo collect the meter readings and present them in another set, of "daily" values. Each set grows, day by day, and then a new set is started at the beginning of each month. Once the month is over, there is a set of values which, if complete, will have one value for each day in the month. Months vary in length so, even if there were no missing data, the sets would vary in size. They also vary in size due to the fact that occasionally some data are missing.

Ovo's unsupported API presents these data sets in json format, labelled either by month or by day, making it trivial (hah!) to scrape them using a Python script and then insert the values obtained into a dictionary.

The second mistake, this time more serious, is that Ovo offer the important information as a list. The "half-hourly" sets of data should include lists of 48 items but, if there are any items missing, the list will be shorter - possibly even empty. The "daily" sets of data should have lists whose length might be anything from 28 to 31, depending which month it is, but a list may be shorter (and could even, in a really bad month, be empty).

The reason this is a mistake is that the question "Which items are missing?" cannot be answered simply and directly. It's obvious ***how many*** are missing, that's merely a matter of counting, but identifying ***which ones*** are missing is possible only by checking all the time-stamps of the ones that ***are*** there. It would have been much more sensible to ***save the items in a dictionary***, keyed on date and time (their combination is known as a datetime). Then that question reduces to "Is the time-stamp of item `x` among the keys of the dictionary `d`?" whose answer is immediately available as the `bool` value of the Python expression `x in d.keys()`.

The initial commit of code (version 02) includes a function, `read_ovo`, which takes one of these sets of data as input (including the important information in a list), and returns a dictionary (including that important information, and keyed on datetime). Also thrown in to the commit, because it illustrates how to do things once these dictionaries have been populated, are a few lines to put up interactive matplotlib graphs, and one line to make conversion of gas energy to gas volume. When it comes to the estimation of meter readings, the dictionaries will be used to populate numpy arrays in which missing values are made explicit and space is reserved for values (estimates) to be inserted to fill the gaps.

#### Examples - screenshots

##### Consumption (what Ovo refers to as Usage)

Electricity consumption over the whole period since the smart meter was installed (and then zooming in a couple of times): 





This the same interactive graph, all I've done is zoom in to whatever took my fancy. What starts out as a wispy, apparently variable density plot (there are over 17,000 distinct datapoints being plotted here, which is surely beyond what could be resolved when I took the screenshot: this is indistinguishable from a continuous variation) is revealed, on zooming in, to have structure, and a daily pattern.

(The period chosen to examine in the last two plots was in the middle of summer, and the atypically high electricity consumption was just abnormal use of the immersion heater during a week when the gas boiler developed a fault and stopped heating our water. In the last plot, it becomes apparent at what time of day we needed to replenish our stored supply of hot water.)

##### Missing data

The same plot, but zooming in to another period:




"It's not me, it's you" - the last plot doesn't show low consumption, it shows the zero values that my code inserted where values are missing from the smart meter data. At this stage, I offer no indication of that (and neither does Ovo in its presentation of my data). I can remedy that, and will, in the course of developing this code. Ovo would like to remedy that but, as far as I can tell, does not have the insight to know how to do that any time soon.

Well, Ovo could always look on GitHub for hints for what to do...

*To be continued.*


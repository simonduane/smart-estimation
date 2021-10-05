# smart-estimation (version 02, on its way to version 03)

My activity on this was prompted by evident shortcomings in Ovo's handling of missing data: one day they estimated my gas consumption to be negative. Don't be fooled by the positive looking bar above "28", on the right, the value listed in the table on the left is negative, rather than nearly 15 kWh. (The true value was very close to 10 kWh, the same as it had been every day since the first of the month):

![screenshot](https://github.com/simonduane/smart-estimation/blob/main/image-20211005072813219.png)
![screenshot](https://github.com/simonduane/smart-estimation/blob/main/image-20211005072716100.png)

A gas meter cannot register a negative volume, that is simply nonsense, and I could not leave it at that. Ovo's presentation to me of my data has remained unchanged in the intervening 10 weeks, so I have no hesitation in calling them out on it, having pointed it out to them as soon as it appeared. Very recently, the presentation of the same data in their smartphone app has improved:

![screenshot](https://github.com/simonduane/smart-estimation/blob/main/Screenshot_20211005-073321.jpg)

Their explanation of the negative value is in the screenshot, but the fact is there is no excuse for having made a negative estimate in the first place. The following is my attempt to explain and demonstrate how such things can be avoided. It's a work in progress, but I aim to keep this README more or less in step with the Python script as it develops.

I'll begin by describing what are the problems in how Ovo stores their data, an alternative (my way to store the data), and what my solution to their missing data problem looks like.

### Two frequencies - daily and half-hourly

Smart meters register consumption continuously, and are designed to record this consumption at 30 minute intervals. That record consists of increments in the register value (a.k.a. meter reading), and they are stored locally (in the *Communications Hub*, or **Comms Hub**) and accessed remotely via a private network (to which the gatekeeper is DCC). They may be "my" data, I am only allowed to access it if I'm a DCC *Authorised User*, and acquiring such a status costs money - hence the emergence of Hildebrand, Carbon, and others who, as *Authorised Other Users* of DCC can access my data for me. They offer to do that "for free", provided I let them save and use my data for their own purposes. GDPR means they need my permission to access my data at all, and have to tell me what those purposes are, but there must be money to be made from it, otherwise they wouldn't make the offer. As always, if you sign up to a "free" service, that just means that you (or your data) are a form of payment that the service provider is entirely happy to accept.

As the utility company selling me energy, Ovo are the only ones who ***must*** have access to data from "my" smart meter (the data may be mine, but they installed the meter and it's actually theirs.) Ovo's choice (with my consent) is to ask DCC, at a time close to midnight, every 24 hours, to retrieve a daily summary of usage, in the form of 48 increments in the meter reading, and one meter reading. The increments are just that: on their own, they give no information about what the meter reading itself is, only the amount by which it has changed. That is why it is important to retrieve the meter reading. Aside from anything else, it's one of those meter readings that appears as the closing reading on the monthly statement. The same number reappears as the opening meter reading on the following month's statement.

As far as I can tell (the SMETS standards are not as explicit as they need to be for me to make unambiguous sense of them), the Comms Hub doesn't necessarily save a history of meter readings. It may only be able to access the value currently in the meter register. The history it saves (as required by the SMETS standards) is 13 months' worth of half-hourly usage data. Each 30 minute interval could be regarded as having an opening meter reading and a closing meter reading, but those readings are not explicitly saved anywhere. My own tests have convinced me that each of those readings is a value that was in the register, at a time which is within a second or so of being on the hour or on the half hour (UTC - Universal Coordinated Time). The value would have been shown as "the meter reading", if a button on the meter had been pressed at just the right moment, and that moment would have been within a second or so of being on the hour or half-hour. I'm labouring this explanation rather, but there is a risk of confusion which I want to minimise - any reader should feel free to skip ahead if they already know and understand all this.

When Ovo ask DCC to retrieve a meter reading for them, there is simply no guarantee that the request will reach the Comms Hub exactly on the stroke of midnight. In practice, as far as I can tell, it's several minutes off, sometimes more.

The data that Ovo make available (through an "API" that is not supported for public use, but it's there and I use it) are presented in two sets: of "half-hourly" and of "daily" values. For whatever reason (e.g. unreliable communications) these sets are not all complete. If they were complete, the "half-hourly" data would consist of 48 values, one for each of the 30 minute intervals between one midnight and the next, with each value being an increment in the meter reading, and there would be one of these datasets per day. Those values are energies, in kWh, for electricity, and what I would argue should be a volumes, in m^3 for gas. Ovo's first mistake, in my opinion, is to save energy in kWh instead of volume in m^3 for gas. Because what the meter registers is volume of gas in m^3, not its energy content in kWh. That's why the monthly statement says what it does.

As it happens, Ovo use a fixed calorific value, 39.5 MJ/m^3, to arrive at the half-hourly kWh values they present, instead of the "true" value which is in any case only published by the National Grid the following day. This really isn't a problem. It's only a nominal value, the units deserve to be put in quotation marks, "kWh". I can apply the inverse conversion factor and, provided I use the precise value of "kWh", I am reassured that the result is always an integer multiple of 0.001 m^3. Meters register gas volume consumed in m^3 to 3 decimal places. No more, no fewer. So this is as it should be. Exact representation using 3 d.p. would save space too, but I doubt that matters much.

That meter reading, taken around midnight, could sensibly be saved ***with*** those (up to) 48 increments. (Those increments wouldn't exactly equal the consumption since the previous midnight reading, but Ovo know this and their web site warns of the difference. Instead, Ovo collect the meter readings and present them in another set, of "daily" values. Each set grows, day by day, and then a new set is started at the beginning of each month. Once the month is over, there is a set of values which, if complete, will have one value for each day in the month. Months vary in length so, even if there were no missing data, the sets would vary in size. But they also vary in size due to the fact that occasionally some meter readings data are missing.

Ovo's unsupported API presents these data sets in json format, labelled either by month or by day, making it straightforward to scrape them using a Python script and then insert the values obtained into a dictionary whose structure mirrors that of the json data.

The second mistake, this time more serious, is that Ovo offer the crucial information as a list. The "half-hourly" sets of data should include lists of 48 items but, if any items are missing, the list will be shorter - possibly even empty. The "daily" sets of data should have lists whose length might be anything from 28 to 31, depending which month it is, but a list may be shorter (and could even, in a really bad month, be empty).

The reason this is a mistake is that the question "Which items are missing?" cannot be answered simply and directly. It's obvious ***how many*** are missing, that's merely a matter of counting, but identifying ***which ones*** are missing is possible only by checking all the time-stamps of the ones that ***are*** there. It would have been much more sensible to ***save the items in a dictionary***, keyed on date and time (date and time can be combined to produce a single object known as a datetime). Then that question reduces to "Is the datetime-stamp `dt`of an item among the keys of the dictionary `d`?" whose answer is immediately available as the `bool` value of the Python expression `dt in d.keys()`.

The initial commit of code (version 02) includes a function, `read_ovo`, which takes one of these sets of data as input (including the important information, as items in a list), and returns a dictionary (including that important information, but now as values in a dictionary and keyed on the datetime stamp of each item). 

Also included in to the commit, because it illustrates how to do things once these dictionaries have been populated, are a few lines to put interactive matplotlib graphs on the screen, and one line to make the conversion of gas energy to gas volume. When it comes to the estimation of meter readings, the same dictionaries will be used to populate numpy arrays in which missing values are made explicit and space is reserved for the insertion of values (estimates) to fill the gaps.

#### Example screenshots - from version 02

##### Consumption (Ovo refers to this as Usage)

Here are the plots of electricity consumption, firstly over the whole period since the smart meter was installed, and then zooming in a couple of times: 

![ScreenShot](https://github.com/simonduane/smart-estimation/blob/main/image-20211004215605014.png)

![ScreenShot](https://github.com/simonduane/smart-estimation/blob/main/image-20211004215735144.png)

![ScreenShot](https://github.com/simonduane/smart-estimation/blob/main/image-20211004215836690.png)

These are screenshots taken from a single matplotlib interactive graph, put on the screen by running the python module as a script. All I've done is zoom in to whatever took my fancy. What starts out as a wispy, apparently variable density plot (there are over 17,000 distinct datapoints being plotted here, which is surely beyond what could be resolved when I took the screenshot: this is indistinguishable from a continuous variation) is revealed, on zooming in, to have structure, and a daily pattern. The plot is presented as a "bar" chart, with each item of consumption shown as a solid rectangle, 1/48 days wide and having height 48 times the energy consumed in that half-hour, in kWh. Given that the x-axis is time in days, albeit labelled by datetime, this means that the area of each rectangle is energy in kWh.

(The period chosen to examine in the last two plots was in the middle of summer, and the atypically high electricity consumption is explained by the fact that our gas boiler developed a fault and we relied on the immersion heater. In the last plot, it becomes apparent at what time of day we needed to replenish our stored supply of hot water.)

##### Missing data

The same plot, but zooming in to another period:

![ScreenShot](https://github.com/simonduane/smart-estimation/blob/main/image-20211004222612196.png)

![ScreenShot](https://github.com/simonduane/smart-estimation/blob/main/image-20211004222743085.png)

"It's not me, it's you" - the last plot doesn't show zero consumption, it shows the zero values that my code chooses to insert where values are missing from the smart meter data. Somewhat revealingly, Ovo's plot is similar (it's not possible to show more than one day at a time):

![ScreenShot](https://github.com/simonduane/smart-estimation/blob/main/image-20211005091458181.png)

... but that last consumption is shown, strangely, as happening in the first half-hour of a new day. That's also how it's labelled in the API dataset, but I know that's wrong and it's kind of obvious, here, that Ovo is just allocating that half-hour of usage to the wrong day. Something similar happens right at the start, on the first day for which there is any smart meter usage data: the data item for the very first half-hour is apparently missing. The reason is that the consumption that Ovo would show in that time interval actually happened at the end of the previous day.



*To be continued...*


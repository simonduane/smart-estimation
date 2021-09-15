# smart-estimation
Dealing with missing smart meter data

There are a few equations below. I have not tried to render them graphically here, and hope the sense of the words remains clear.
On the one hand, I intend the following as a presentation of a logically coherent way to process smart meter data, and I aim to demonstrate this by offering working code applied to real data. On the other hand, the only such data I have access to is my own, mostly via O\*o who collect it and bill me for what I use. They collect and group the data in their own way and this presentation reflects that grouping.

# The processing of smart meter data

There are two aspects: monthly statements and tracking usage. Usage tracking should generate alerts - "this smart meter has stopped sending readings", or "there has been a surprisingly large change in this customer's usage", etc. These notes focus on the task of estimating readings when smart readings are unavailable. The estimates may be needed for billing, but mostly these estimates are just part of regular feedback to customers on our energy consumption. The form of that feedback is largely settled - we have been trained to expect graphs of our usage, by the month, by the day, by the half hour (depending what frequency of smart meter data retrieval we've authorised). Customers  aren't stupid, and we have ready access to our meters. We can be expected to notice if the information we're presented with is unclear, or is clearly wrong.

## At the end of each billing month

A closing read for the old month is obtained (e.g. by retrieval of a smart meter reading), and tracking of usage in the new month starts. The billing statement for the now-completed month is drawn up and the account reconciled.

## Processing once a billing month is in progress

As each day passes, more smart meter data arrive. These data can be processed and the resulting information presented to the user, but how best to do that?

### Uncertainty

The fact is that some things are uncertain and pretending or claiming otherwise will eventually be shown to be a matter of delusion or deceit. At least one customer has objected that the presentation fails to distinguish estimates of usage from actual usage, and does not make clear when estimates have been corrected retrospectively. Among my aims in this exercise is to demonstrate one way of (I think) doing better. Overall, it reminded me (a metrologist shouldn't need such reminding) that uncertainty really does have an everyday importance.

### A mid-month snapshot: the starting point for analysing today's data

By snapshot, I mean a summary of how things are after the processing of the most recently received smart data (i.e. what arrived early yesterday) has been completed, and before the retrieval of more data early today. The state of play can be summarised as follows.

There is a history of daily meter readings, one for each day up to and including yesterday. Each one is the "opening" reading for the day, preferably one retrieved from the smart meter. If that retrieval failed for whatever reason, then the reading status, whatever it might be, is lower. It turns out to be sufficient to allow the status of a meter reading to be inferred or estimated, and it may also be, in a sense that will become clear, provisional. But it is not missing altogether. The reading value may in fact be the result of applying some correction to a provisional value, but we don't need to keep a full audit trail of such corrections - it is enough to allow each reading to have its status. Only provisional readings may be subject to correction. To be clear, the status of a reading in the history of all readings is one of actual, inferred, estimated or provisional. Most actual readings arrive as values retrieved from the smart meter, but they could be manual readings by the customer or by someone else. I shall pretend that the the only actual readings are smart readings, and that's what I'll call them.

There is also a complete history of usages, which I shall assume have half-hour resolution so each one is the consumption during a particular 30 minute interval. These usages also have a status, which is smart, inferred, estimated or provisional. 

An item of data which is smart or inferred has an uncertainty which is negligible, i.e. it is small enough to ignore for the purposes to which most estimated readings are put. Data which is estimated or provisional has a larger uncertainty that is usually not negligible.

This history of readings and usages is only "complete" with the proviso that any missing smart data have been replaced with data which is inferred or estimated or provisional. But there are no missing data. Instead, the data may have a status which is lower than the ideal. The benefit of this approach is that data can be combined to generate more data (this is the processing), and the resulting data can be assigned a status which is consistent.

#### Processing in general terms

Suppose two items of data, $d_1$ and $d_2$ are used in a calculation to obtain a third item $d_3$, and all items have their own status, respectively $s_1$, $s_2$,  and $s_3$. Then it turns out that we only need to require that $s_3\le \min(s_1,s_2)$: you really aren't allowed to rise above your station in life. I prefer not to dilute the meaning of "smart" and so, even if both $d_1$ and $d_2$ are "smart", I say that $d_3$ is "inferred". After all, it was generated by some calculation, it presumably didn't come directly from a smart meter (in this case it really doesn't depend on $d_1$ and $d_2$ at all). The hierarchy is summarised in the table below. 

For example, one reads along the row  $x$ is "inferred" as far as the column y is "estimated" to conclude that, in this case, $f(x,y)$ would be "estimated".

| status |                      |               |                 |                  |                    |
| ------ | -------------------- | ------------- | --------------- | ---------------- | ------------------ |
|        | $f(x,y)$ is          | y is "smart"  | y is "inferred" | y is "estimated" | y is "provisional" |
|        | $x$ is "smart"       | "inferred"    | "inferred"      | "estimated"      | "provisional"      |
|        | $x$ is "inferred"    | "inferred"    | "inferred"      | "estimated"      | "provisional"      |
|        | $x$ is "estimated"   | "estimated"   | "estimated"     | "estimated"      | "provisional"      |
|        | $x$ is "provisional" | "provisional" | "provisional"   | "provisional"    | "provisional"      |

Sometimes, the "same" result can be reached by different methods, and the results might differ in both value and in status. Then, whichever method leads to the result with higher status is the one to adopt. It might be that the better method only becomes feasible when more smart data becomes available. One can think of that new data as enabling the correction of what was formerly a provisional result. The new result would be "estimated" or "inferred". (Unless the new method involves repeated attempts to retrieve smart meter data - then a new result really could be "smart".)

If the methods lead to results of equivalent status, then this becomes a test of uncertainty. If both results are "inferred" then the difference between the results had better be negligible, otherwise something somewhere has got corrupted. If the two results are merely "estimated", then they will each have some uncertainty and one can reasonably require any difference to be comparable to the uncertainties. (The difference doesn't have to be strictly "within the uncertainty", because uncertainty is all about probabilities, a detail that I'm going to skate over here.)

### Five Easy Pieces, or How to analyse smart meter data (in 5 steps)

#### Step 1 - retrieval of another daily set of smart meter data

The smart meter data retrieved today consists of the opening reading for "today" and up to 48 half-hourly usage values for "yesterday". These data should be added to the history as described in the following steps. After a rather deep dive into real data, including an empirical determination of the actual time (UTC) at the start and end of one of these usage intervals, I know that the daily instalment of data inludes a meter reading somewhere "around" midnight and usage data for 48 intervals that combine to make a day-long interval that starts at 23:30 on the day before yesterday, and ends at 23:30 yesterday. To take one example, at the end of the most recent complete billing month, the closing reading for that month was taken around 00:39 UTC on the first day of the following month. The timing of the reading really is only "around" midnight. The timing of the boundaries between usage intervals is a lot more precise (good to a second or so) but they are presented on the My O\*o web-page and in their "API" datafiles as if they relate to a period stretching from one midnight to the next (UTC). They don't: the boundary between days is at 23:30. Ultimately, the particular details matter only when tying up readings and usages "within the uncertainties".

#### Step 2 - filling gap(s) in usage

Usage data received are given the status "smart" and added to the history. If the smart usage data have gap(s), then a model is used to predict usage value(s) which are inserted to fill the gap(s). The inserted usage has status "provisional".

If a smart reading is received, that is added to the history, with status "smart".

#### Step 3 - calculating a reading

Smart reading or no smart reading, the 48 usage values are added together to produce a "usage sum" which has a status inferred or provisional, depending whether any model data were involved. It is handy to keep track separately of the model contributions by forming a "model sum" for each day which is zero if there none of the 48 usages were missing, and which is the sum over all the model values if any were used. The rest of the usage sum is the sum over the smart data, so we have usage sum = smart sum + model sum (This isn't complicated - in the model, the value only depends on the week in the year, not on the time of day or even the day of the week.) By adding this usage sum to yesterday's reading we arrive at a calculated value for today's reading which is independent of any smart reading retrieved. Its status is either "inferred" (if there are no terms in the model sum) or "provisional" if there are any terms in model sum.

For avoidance of doubt, "calculated" does not indicate the status of an item of data. It refers to the process by which it was obtained. The status is only a matter of what went into the result.

#### Step 4 - comparing calculated and smart readings

If a smart reading is available, then any difference between it and the calculated value must be the error of the calculated value. Depending on the status of the calculation result, either this difference must be negligible or it will provide an indication of model uncertainty.

Every time a new smart reading is received, another example of model error is created. Over time, an analysis of the statistics of these model errors can inform a decision on whether to re-calibrate the model before further use. The re-calibrated model is not applied retrospectively - that would be cheating. Even without such re-calibration, the error can be used to correct all those provisional readings and usages in that interval, and that is done in the next step.

#### Step 5 - correcting past provisional data

If today's reading is smart, then one can look back to the most recent reading with negligible uncertainty (i.e. a smart or inferred reading) and subtract one from the other. This "reading diff" has status "inferred", and can be compared with the total of all the usage sums over the day(s) between the two readings. If there are no terms contributing to the model sums, then the total of the usage sums is purely "inferred" and this then gives us a consistency check: the reading diff and the total usage sum should be the same (i.e. any difference should be negligible). If the model sums are present, then the reading diff can be used to obtain a single correction factor. Basically, the model sums are scaled by a common factor to make the consistency check work. After making this correction, the status of all those model usages is promoted from provisional to estimated, the total of the usage sums becomes estimated, and now agrees with the reading diff. This elevation in status applies to all the intermediate usages and readings, which formerly were provisional and now are estimated.

There is one special case, if there was only one missing smart usage value between those two good readings. In that case the outcome of the rescaling is to force the usage in that one interval to be whatever is required to make the correct usage sum. Instead of starting with a prediction from the model, one can (but only once the latest smart reading becomes available) express the usage in that interval as the difference between two "inferred" readings. As such, that usage has status "inferred" too.

### Presentation to the user

Full speed ahead and damn the torpedoes!

On a Usage, Daily plot, each half-hour bar will be either blue or pink. There is no point in showing the model because it is just a horizontal line. If the day is since the last smart reading, the bars will be blue or green.

On a Usage, Monthly plot, each daily bar will be part blue (the smart contribution) and part pink (the model provisional contribution). the pink sections will change length from week to week, but usually not by much. There may also be a green part, but only on the most recent days.

A Usage, Yearly plot will be similar.

### The model used here

This is where things start to look a bit mathematical. The smart data consist of readings $r$ and usages $u$ which both depend on time. $r$ is the reading taken at the start of each day, $u(t)$ is the usage during the half hourly interval at time $t$. $p(t)$ is the model-predicted usage during the half hourly interval at time $t$
The half-hourly intervals form one sequence, numbered by $t = 0, 1, 2, ...$
but could as easily be labelled by date and time, or using a calendar where

- the intervals making up each day are numbered $i = 0, 1, ..., 47$
- the days making up each week are $d = 0, 1, ..., 6$
- the weeks making up each year are $w = 0, ..., 51$

and

- the years are numbered $y = 0, 1, 2, ...$

In this way the original integer sequence $t = 0, 1, ..., n, ...$
is replaced by a sequence of quartets of integers $(y, w, d, i)$ such that

- $0 \le i < 48$
- $0 \le d < 7$
- $0 \le w < 52$
- $0 \le y$

The rule for converting $n$ into a calendar label involves 4 different functions $i(n), d(n), w(n), y(n)$

Defining a prediction model amounts to choosing a function of $n$ or, equivalently, of $(y, w, d, i)$
and a useful model takes the special form $p(w)$ meaning that the predicted  usage only depends on the week number. It is the same for different days of the week, i.e. it is independent of the $d$ in $(y, w, d, i)$ and it's also independent of $y$ and $i$ as well.
The most general such $p(w)$ would be a list of 52 values, one for each week in the year
A more useful $p$ takes a particular functional form

$p(w) = \max(p_0,p_1\cos(2\pi (w-w_0)/52)-p_2)$

and has positive parameters

| Parameter | Interpretation                                               |
| --------- | ------------------------------------------------------------ |
| $p_0$     | the typical minimum usage (0.04 m^3 in 30 min)               |
| $p_1$     | the typical seasonal usage variation (0.8 m^3 in 30 min)     |
| $p_2$     | an offset, which controls for how much of the year the CH is on |
| $w_0$     | a week number, which controls when we need CH the most       |

# Meter readings, usage and estimates

A supply produces meter readings and a history of usage. Ideally, there will be a smart meter reading every day (at midnight) and smart usage data for every half-hour interval, but this cannot be taken for granted and, if data are missing, estimates must be made. Meter readings are obviously required for billing and, when Time of Use tariffs come in, usage data will be needed for billing too. Estimates that are used in billing must be reliable and it will be unacceptable for them to be wrong in an obvious way as, at the moment, seems to be happening regularly with the estimates that appear as part of feedback to users on their usage.

### Some terminology, and conventions

#### Meter reading

The meter on a supply has a *register*, containing a *value* which changes with time. The value at any moment is the amount *supplied* up to that moment. The value is cumulative. A meter *reading* combines a register value with the date and time at which the register contained that value. It may be that the reading for a particular date (and perhaps also time) is needed but is not known (or was not recorded) - in that case the reading must be *estimated*.

#### Consumption (a.k.a. "usage")

An increase in the amount supplied, over a period of time, means that energy has been consumed, or used. Energy *consumption*, or energy *usage*, combines the increase (in the metered quantity, i.e. the increase in the cumulative register value) with the period of time during which that energy was consumed. That period is delimited by two moments, the start and end times of the period in which the energy was used. 

#### Smart meter data

Smart meters are set up to record usage automatically, as a set of 48 values per day where each value is the amount of energy consumed in one half-hour period. The first period starts at one midnight (UTC) and the last period ends 24 hours later, at the following midnight (UTC). The usage data for each day is retrieved by DCC more or less as soon as it is available, i.e. in the early hours of each morning. A meter reading is requested at the same time.

However, smart meter data communications are not completely reliable and this is one reason why the meter reading for a particular date and time may not be available. In the same way, the usage data for a particular date may be incomplete or even missing altogether - in that case, the usage must be *modelled*. Sometimes the modelling is well-controlled (the model is "calibrated"), other times the modelling involves more significant assumptions, in particular that the pattern of usage hasn't changed. In that case, the usage must be *projected*: a model is used, and that model may have been calibrated on previous occasions but, this time the model is being used in a way that *does not include a current calibration*.

My aim in defining things carefully like this is to clarify ideas and reduce the room for misunderstanding. Estimation applies to meter readings, modelling applies to usage. Estimated readings are always based on modelled usage. Sometimes the modelling is more reliable than others, i.e. when calibration is possible. Other times calibration is not possible and the modelling only gives a projection, or forecast. Generally, the lack of calibration is a temporary state of affairs. As soon as a new actual meter reading is available, what were previously projections of usage coming from an uncalibrated model can be corrected by using the new reading to determine a calibration factor for the model. Replacing those uncalibrated projections of usage, with the predictions of a calibrated model of usage amounts to making a correction (retrospectively) to previous estimates.

## Model-based estimation

Estimates are best made using a model which can predict usage. The model must satisfy basic requirements, for instance that predicted usage must never exceed the supply rating (typically 25 kW for electricity, 6 m^3/hour for gas), and similarly must never be negative. But that's it, really, because the estimation process outlined here includes a *calibration* of the model[^(1)]. This calibration is what *can* make sure that model, i.e. all its predictions, are consistent with the customer's actual usage. In fact, the estimates can be surprisingly robust.

[^(1)]:One way of understanding calibration is that it involves using a special factor, a fiddle factor. This  factor is the ratio of what's wanted, divided by what one already has, and "calibration" involves multiplication by the calibration factor. I can't think of a more general recipe for making a correction than to multiply what you've got by what you want, and then to divide the result by what you had to start with. First you think about it, then you try it and realise it works, then you wonder: what's the trick - it can't be that simple, surely? Well, I'm here to tell you it *is* that simple. Pearls of wisdom from a professional of 30+ years experience, these, and all for free...

## Extrapolation, interpolation and calibration

Among all the actual meter readings for a supply, there will be an oldest reading and a newest reading, and many more readings in between. Some meter readings should be there but aren't, and these "missing" readings create gaps in the history - filling in these gaps amounts to a process of *interpolation*. Other readings may be "missing" from the time before the oldest available reading, or the newest reading may not be new enough to serve some purpose or other. Making estimates to replace missing readings such as these involves *extrapolation*. 

In the approach described here, all estimated meter readings are obtained by combining an earlier actual meter reading and with the cumulative sum of usage since that earlier reading. Such an estimate is prepared for every moment that one usage interval ends and the following usage interval starts. That's an awful lot of estimates and I particularly recommend doing this, even for times when a smart reading is already available.

The advantage in having both smart readings and model-based predicted readings available for the same time is that they can be compared with one another. The calibration process depends on such a comparison: whatever parameters the model has, "calibration" effectively is a way of tweaked them to improve the agreement between the model and reality. It is only estimates that amount to interpolation that can benefit from such calibration. This may be obvious but, having spent over half my life working in an upmarket "calibration laboratory", perhaps it's not as obvious as I like to think. Whether or not it's obvious doesn't alter the fact that it's true :-) . The other estimates, the ones that involve extrapolation, are more fragile - mainly because extrapolation cannot include an automatic calibration the way that interpolation does. In that case it becomes all the more important that the model, used to make the predictions that contribute to estimates, be properly validated. Calibration, where it is possible, is part of validation.

The routine production of estimates, and a systematic comparison of those estimates with reality is the best way to generate evidence of a model's validity.

## The estimation process

### Define a model

Where possible, usage values are taken from smart meter data, provided only that those data are plausible. If the usage values are implausible (I've seen a few), they should simply be ignored altogether and replaced by model-based predictions. ***A model is just a method for predicting the usage for an arbitrary 30 minute interval.*** The prediction must be ***unambiguous*** - the predicted usage might vary,it might depend on the time of day, the day of the week, or the time of year, but that's *time-dependence* which is different from *ambiguity*. In fact the model might be so trivially simple that its prediction never changes, for instance

- "the gas usage was 0.21 kWh in every half-hour interval, on every day in Aug 2021"

but the model mustn't be stupid 

- "the gas usage between 11:30am and noon on 22 Feb 2020 was 188250.98 kWh", or

- "the gas usage on 28 Sep 2021 was -50.84kWh"

The first one, perfectly constant usage, is entirely possible, however unlikely. That's fine, it's still possible. The second one is literally impossible, and that's not fine. My gas supply is rated as U6, meaning that maximum volume of gas it can deliver in any hour is 6 m^3, which is 3 m^3 in any half-hour which, given the permitted range for the calorific value of gas supplied, turns out to be at most 32 kWh. That prediction is too large by a factor of 6000 or so. It is IMPOSSIBLE, and so to present it to me as an estimate as happened quite a few times early on (not that it was even admitted to be anything other than a regular usage value) was ***stupid***. The third one is stupid as well, because the volume of gas supplied cannot be negative, and the supplier shouldn't pretend otherwise, because that makes them look stupid. Even if they're coming up with a number that "balances the books" there are other ways to do that and, as a way of balancing the books, making usage negative offends me.

Those examples are real: my web browser put them on my screen at 2 pm on 18 October 2021, when I logged into my account on the My Ovo website. It was the work of a few seconds to find them - they've been there since the day those estimates were generated and they are among the reasons I'm currently disinclined to renew my account with Ovo. Once Ovo's system software has shown itself to be untrustworthy, why ever would I want renew my Ovo account?

### Estimation: the N step program 

*What should N be? 10? 12? I could make it whatever you want*

1. Pick an actual meter reading $R_A = R(t_0)$ and, for the purpose of this explanation, it should not be the most recent one. It could even be that initial reading of zero, the one that was on the meter when it was first installed. $t_0$ is just the last time that value was in the meter's register.

2. Define a model, and stick to it. See the previous comments for an explanation of what counts as a model.[^(2)] 

3. Use the model to calculate (i.e. predict) the usage for every half-hour interval starting with that meter reading $R(t_0)$ and going forwards[^(3)]. For convenience, in this explanation, I label each interval with the time at which it starts. So, the initial interval starts at $t_0$ and ends at $t_1$, where $t_1$ is 30 minutes later than $t_0$. Given this sequence of times, $t_i$, The model generates a corresponding sequence, or list,  of values $u_p(t_i)$. These are the model-predicted usage values, i.e. $u_p(t_i)$ is the model's prediction of the energy that was (or will be) consumed between times $t_i$ and $t_{i+1}$.[^(4)] 

4. Take the smart usage data that are available, and put those data in a second list. Where the smart data item is missing, be sure to put a zero in the list, in place of the missing smart data. Where smart usage data is available, replace the corresponding entries in the list of model predictions with zeros. The aim at this stage in the programme is to have two lists of usage values. If you put the lists alongside one another, only one of the lists has an item, because the item in the other list has been replaced by zero. Zero is a potentially confusing value to insert: what if there is real smart usage data, and the value is, actually zero? All I'd say is, take care. Actual usage can really be zero but, because at some point I might need to divide by it, model-predicted usage is not allowed to be zero. Having both lists actually resolves potential ambiguity. Because the only way the list of model predictions can have a zero is if the prediction has been replaced by zero, which means there must be genuine smart data. Even if that smart value does turn out to be zero :-)[^(5)]

5. Make a third list by merging these two, taking either the smart value or the model-predicted value. Yes, if they're both zero that's fine - in that case the smart value counts and that can be zero.

6. Calculate a fourth list, in which the initial entry is $R_0$ and the later entries satisfy $R_{i+1}=R_i+u_i$.

7. Eventually, because $R_A$ was not the most recent actual reading, the intervals will reach the next actual reading, $R_B=R(t_n)$. Note the sleight of hand here: I'm assuming that the actual readings $R_A$ and $R_B$ were taken at times $t$ and $t'$ that are both among the moments that separate adjacent usage intervals. I will stick with that approximation. Come back to me when you have a method that doesn't make this approximation and doesn't also doesn't produce stupid estimates. I've no doubt that such a method exists, but let's focus on the important problems first, and implement their easy solution, shall we?

8. At this stage, we have a pair of actual readings, $R_A$ and $R_B$ and a whole series of estimated readings, $R(t_i)$, of which the last one, $R(t_n)$ should be the same as the actual reading taken at that time, $R_B$. From this information, we calculate a calibration factor for the model, one which ensures that when we use it to make the best estimate we can, the estimated meter reading agrees precisely with the actual meter reading. We do this by isolating the contribution that the model makes to this estimate, and scaling that contribution by whatever factor is needed to make the estimate come out right. It's a trivial calculation, honestly. That factor is the calibration factor for the model and, for every interval in the period under consideration, we say that the best model-based ***estimate*** is the what we had before, but in which the model-predicted contributions have all been multiplied by the same ***calibration factor***.

9. That's an awful lot of estimated readings. One for every half-hour in that period. If the period straddles more than one day, then the intermediate moment(s) of midnight are times when we were lacking a smart meter reading. We are still lacking a smart reading, but you have just read an explanation of how to make the best estimate you can.

10. The final step in this programme is to apply the programme, to translate the programme into a program.

[^(2)]:It turns out that there is a technical restriction, that if a usage could in principle be non-zero, then the model prediction had better not be zero. This is because the calibration process in step 8 below involves dividing by a sum of model-predicted usage values. If the sum is only over ones that are definitely zero, this doesn't make sense. So define the problem away by making sure that no predicted usage is precisely zero, even if that happens quite often. The division is by the prediction, not by what actually happens.

[^(3)]:Starting from a later reading, it is possible to go backwards instead. A similar logic applies, but it's potentially confusing to have both directions in your mind at the same time, especially at first, when it's all new anyway. Instead, get your head around the forwards case, completely, before asking yourself - how would this work going in the other direction...

[^(4)]:The question, is it better to label an interval by its start time or by its end time, has no right answer, and there is room for confusion. In this note, usages are labelled with the interval start time. The key thing is consistency, and that is facilitated by clarity. Otherwise one can end up in the position where usage is labelled as having such and such a start time when, as a matter of fact, I know that that time is at the end of the usage interval. In using data that comes from such a source it takes an extra special effort to be sure that mistakes are not being made...

[^(5)]:There is a huge difference between a reading being missing, and a reading happening to have the value zero. That sounds obvious, put like that, but you might be surprised how often the distinction is not maintained. I find Hildebrand are hopeless in this regard: anything more recent than the latest smart data is left blank, but if subsequent smart data is retrieved creating a gap (i.e. missing data) the Bright app just shows it as zero. In the terms of this explanation, it's as if the model they are using predicts zero. Perhaps a better way of putting it is that they just don't have (or make publicly available) a model. Belatedly, I realise that the list of model predictions can be interpreted as a flag whose meaning "smart data missing" is equivalent to "model prediction is non-zero".

## Postscript

There is room for playing here. The only constraint on the model is that it doesn't produce stupid predictions, ones which are beyond the physical limits of what's possible. What the model will never do is correctly predict the random variations in usage that happen from half-hour to half-hour and from one day to another. So, in validating a model against actual usage, don't be fooled into taking the patterns in actual usage too seriously. Some of them are just statistical noise. Taking those small random variations seriously enough to build them into the model is another kind of stupidity, and Ovo's current estimation process displays that stupidity too.

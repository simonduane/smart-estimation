# Meter readings, usage and estimates

A supply produces meter readings and a history of usage. Ideally, there will be a smart meter reading every day (at midnight) and smart usage data for every half-hour interval, but this cannot be taken for granted and, if data are missing, estimates must be made. Meter readings are obviously required for billing and, when Time of Use tariffs come in, usage data will be needed too. Estimates must be reliable and it will be unacceptable for them to be obviously wrong, as happens regularly at the moment.

## Model-based estimation

Estimates are best made using a model which can predict usage. The model must satisfy basic requirements, for instance that usage is never predicted to be negative, nor are predictions allowed to exceed the rated supply (typically 25 kW for electricity, 6 m^3/hour for gas). But that's it, really, because the estimation process outlined here includes a calibration of the model. Such calibration can make sure that the predictions from a model are consistent with the customer's actual usage. Estimates can be surprisingly robust.

## Extrapolation, interpolation and calibration

Among all the actual readings for a supply, there will be an oldest reading and a newest reading, and many more readings in between. Some of the missing readings create gaps in the history, and filling those gaps amounts to a process of interpolation. Other readings may be "missing" from the time before the oldest available reading or the newest reading may still be too old to qualify for some purpose or other. Making estimates such as these involves extrapolation. 

In the approach described here, all estimated meter readings are obtained by combining an earlier actual meter reading and with the cumulative sum of usage since that earlier reading. An estimate is prepared for every moment that one usage interval ends and the following usage interval starts. This is done even when there is a smart reading available.

The advantage in having both smart readings and model-based predicted readings at the same time is that they can be compared, and used to calibrate the model: whatever parameters the model has can be tweaked to improve the agreement between the model and reality. Estimates that amount to interpolation benefit from such calibration. This may be obvious but perhaps, having spent over half my life working in an upmarket "calibration laboratory", it's not as obvious as I think. Whether or not it's obvious doesn't alter the fact that it's true :-) . Estimates that amount to extrapolation are more fragile, and it becomes all the more important that the model, used to make the predictions that are the estimates, is properly validated. Calibration is part of validation.

The routine production of estimates, and systematic comparison of those estimates with reality is essentially the only way to evidence a model's validity.

## The estimation process

### Define a model

Where possible, usage values are taken from smart meter data, provided only that those data are plausible. If the usage values are implausible (I've seen a few), they should simply be ignored altogether and replaced by model-based predictions. ***A model is just a method for predicting the usage for an arbitrary 30 minute interval.*** It must be unambiguous - the prediction might vary,it might depend on the time of day, the day of the week, or the time of year, but that's time-dependence which is different from ambiguity. The model might be trivially simple and always make the same prediction, such as

- "the gas usage was 0.21 kWh in every half-hour interval, on every day in Aug 2021"

but it mustn't be stupid 

- "the gas usage between 11:30am and noon on 22 Feb 2020 was 188250.98 kWh", or
- "the gas usage on 28 Sep 2021 was -50.84kWh"

The first one is perfectly possible, however unlikely it seems. That's fine. The other two are literally impossible. My gas supply is rated as U6, so the maximum volume it can deliver in any hour is 6 m^3, which is 3 m^3 in any half-hour, which is at most 32 kWh. That number is too large by a factor of 6000 or so. It is IMPOSSIBLE, and so to predict it is ***stupid***. The last one is stupid because the volume of gas supplied is never negative, so just don't say that. Even if you're coming up with a number that "balances the books" there are other ways to do it and, as a way of balancing the books, it's not acceptable to me.

Those examples are real: my web browser put them on my screen at 2 pm on 18 October 2021, when I logged into my account on the My Ovo website. It was the work of a few seconds to find them - they've been there since the day those estimates were generated and they are among the reasons I'm currently disinclined to renew my account with Ovo. Once Ovo's system software has shown itself to be untrustworthy, why ever would I want renew my Ovo account?

#### Estimation: the N step program 

#### (what should N be? 10? 12? I could make it whatever you want, probably)

1. Pick an actual meter reading $R_A=R(t_0)$ and, for the purpose of this explanation, not the most recent one. It could even be that initial reading of zero that was on the meter when it was first installed. $t_0$ is just the time when that value was in the meter's register.
2. Define a model, and stick to it. See the previous comments for an explanation of what counts as a model.
3. Use the model to calculate (i.e. predict) the usage for every half-hour interval starting with that meter reading and going forwards. (You can go backwards instead. A similar logic would apply, but it's potentially confusing to have both directions in your mind at the same time, especially at first, when it's all new anyway. Instead, get your head around the forwards case, completely, before asking yourself - how would this work going in the other direction...) For convenience, label each interval with the time at which it ends. So, the first interval starts at $t_0$ and ends at $t_1$, and $t_1$ is 30 minutes later than $t_0$. The model generates a list, or sequence, of values $u_p(t_i)$, i.e. the predicted usage, the model's prediction of the energy that was (or will be) consumed between times $t_i$ and $t_{i+1}$. 
4. In those intervals where a smart usage data item is available, $u_s(t_i)$, replace the model prediction with a zero, and create a second list. The second list has all the smart usage data, and it has zeros wherever the smart meter usage value is missing. At this stage in the program, we have two lists of usage values. If you put the lists alongside one another, at any position in the list (i.e. for any interval) exactly one of the two lists has a zero.
5. Make a third list, which has the non-zero list entry, smart or model-predicted, in every slot.
6. Calculate a fourth list, in which the initial entry is $R_0$ and the later entries satisfy $R_{i+1}=R_i+u_i$. In this expression, you just have to take $u_i$ from whichever list has the value that hasn't been replaced with zero.[^(*)] 
7. Eventually, because $R_A$ was not the most recent actual reading, the intervals will reach the next actual reading, $R_B=R(t_n)$. Note the sleight of hand here: I'm assuming that the actual readings $R_A$ and $R_B$ were taken at times $t$ and $t'$ that are both among the moments that separate adjacent usage intervals. I will stick with that approximation. Come back to me when you have a method that doesn't make this approximation and but doesn't also doesn't produce stupid estimates. I've no doubt that such a method exists, but fix the important and easy problems first, eh?
8. At that point, we have a pair of actual readings, $R_A$ and $R_B$ and a whole series of estimated readings, $R(t_i)$, of which the last one, $R(t_n)$ should be the same as the actual reading taken at that time, $R_B$. From this information, we calculate a calibration factor for the model, one which ensures that when we use it to make the best estimate we can, the estimated meter reading agrees precisely with the actual meter reading. We do this by isolating the contribution that the model made to this estimate, and scaling that contribution by whatever factor is needed to make the estimate correct. It's a trivial calculation, honestly. That factor is the calibration factor for the model and, for every interval in the period under consideration, we say that the best model-based ***estimate*** is the ***prediction*** we had before, but multiplied by this ***calibration factor***.
9. That's an awful lot of estimated readings. One for every half-hour in that period. If the period straddles more than one day, then the intermediate moment(s) of midnight are times when we were lacking a smart meter reading. We are still lacking a smart reading, but you have just read an explanation of how to make the best estimate you can.
10. The final step in this programme is to apply the programme, to translate the programme into a program.

## Postscript

There is room for playing here. The only constraint on the model is that it doesn't produce stupid predictions, ones which are beyond the physical limits of what's possible. What the model will never do is correctly predict the random variations in usage that happen from half-hour to half-hour and from one day to another. So, in validating a model against actual usage, don't be fooled into the patterns in actual usage too seriously. Some of them are just statistical noise. Taking those small random variations seriously enough to build them into the model is another kind of stupidity, and Ovo's current estimation process displays that stupidity too.

# smart-estimation

Smart meters were introduced to help users reduce their consumption of energy[^1]. This would require that the utility companies inform their customers accurately and provide information in a timely way and in a form that users can act on. To put it mildly, utility companies in the UK vary in how well they meet this expectation[^2].

[^1]: The anti-capitalist cynic in me suspects that the motivation, for ensuring widespread take-up of smart meters, had a strong element of "They want to consume energy at times of peak demand? Let's make sure the bastards pay." To adapt what Marx [said](https://libquotes.com/karl-marx/quote/lbi8n2o) about Tories and their enthusiasms, capitalists' interest in solving the existential crisis of global heating is hardly more than a clear-sighted view of where future opportunities for (financial) profit lie. When profits are threatened, their interest can wane pretty fast.
[^2]: My creation of the code in this repository was as a result of frustration at the shortcomings of my utility company. I've tried to confine these feelings to footnotes and to keep the main text more neutral.

## Screenshots

The module can be imported and used in other scripts, or it can just be run, at it is. In that case, the last section of the code, which is inside an `if __name__ == "__main__":` block, runs and puts up a minimal but interactive display of meter readings and consumption, for electricity and for gas. The repository contains sample data (from a short period around the time my smart meters were installed, and more recently) which can be used to demonstrate the some features of the module.

![image-20211011092717712](/home/simon/.config/Typora/typora-user-images/image-20211011092717712.png)

and

![image-20211011092918328](/home/simon/.config/Typora/typora-user-images/image-20211011092918328.png)

The last

## Aims

- to give users better access to already-existing data on their own energy consumption
- to introduce a degree of independence from suppliers in how these data can be analysed
- to do all this using free software (free as in freedom as well as free as in beer)

## Background

[From the horse's mouth](https://www.gov.uk/guidance/smart-meters-how-they-work).

## Components

- A Python module `smart_meters.py`, and
- Some Python scripts, including `get_ovo_data.py`

## Dependencies

The data are processed using [numpy](https://numpy.org/) arrays in [Python](https://www.python.org/) and displayed using [matplotlib](https://matplotlib.org/stable/index.html). I see no reason why, if users like this kind of thing, something similar couldn't be implemented as a web-based application and offered by utility companies themselves. This would depend on details of the algorithms used here and probably on the constraints of event stream programming. To the extent that I understand my own creation (which I do) and event stream programming (not in any detail), I am reasonably certain that it could be done - it just won't be done by me anytime soon.

## Explanations

See [here](docs/explanation.md) for more information.



## Future developments

Some kind of user interface, possible integration of the web-scraping elements, support for tuning a model of household demand, etc.

Not least, FFS - just finish this alphabet joke, sooner rather than later.
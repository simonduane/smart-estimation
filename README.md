# smart-estimation

Smart meters are intended to help users reduce their consumption of energy. This requires that the utility companies inform their customers accurately and provide information in a timely way and in a form that users can act on. To put it mildly, utility companies vary in how well they meet this expectation.

The code offered here grew out of frustration at the shortcomings of my utility company.

## Aims

- to give users better access to existing data on their own energy consumption - their own data
- to introduce a level of supplier-independence in how these data can be analysed
- to do all this using free software (free as in freedom)

## Background

<link to information elsewhere about smart metering, as implemented in the UK>

## Components

- A Python module `smart_meters.py`, and
- Some Python scripts.

## Dependencies

The data are processed using numpy arrays and displayed using the matplotlib. I see no reason why, if users like this kind of thing, something similar couldn't be implemented as a web-based application and offered by utility companies themselves. This depends on details of the algorithms used and the constraints of EventStream programming but, to the extent that I understand my own creation (I do) and event stream programming (only a bit), I am reasonably certain that it could be done. Just not by me.

## Explanations

<smart meter data: its structure, the implications of missing data and how to make algorithms robust even when some data are missing>

## Future developments

Some kind of user interface, integration with the web-scraping elements, support for tuning a model of demand, etc. But, not least, FFS - Finish this alphabet joke, here and now.
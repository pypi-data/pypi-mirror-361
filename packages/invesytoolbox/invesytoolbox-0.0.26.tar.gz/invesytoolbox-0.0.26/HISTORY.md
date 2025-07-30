# History
## 0.0.26 (2025-07-13)
- **value_2datatype**: new *typ* "string". This of course also affects *metadata* of **value_2datatype**, **dict_2datatypes** and **dictlist_2datatypes**

## 0.0.25 (2025-05-21)
- **fetch_all_countries** now also works with newer versions of **pycountry** (iso3166-1 used instead of iso3166)
- replaced **setup.cfg** with **pyproject.toml**

## 0.0.24 (2024-09-29)
**timezone** can be passed as an argument to **dictlist_2datatypes** and **dict_2datatypes**

## 0.0.23 (2024-07-22)
* **adjust_spaces_on_punctuation**: inserts narrow (or normal spaces) for certain languages
* **value_2datatype**: 
  - default fmt changed to None (hopefully it doesn't break somewhere, but this is necessary)
  - 'pendulum' is now an option for the parameter 
- default for parameter **fmt** changed to None (this is necessary for the new pendulum conversion in **value_2datatype** to work) for
	- **dict_2datatypes**
	- **dictlist_2datatypes**

## 0.0.22 (2023-10-14)
* **normalize_name** and **could_be_a_name** now have the boolean parameter *lastname* that indicates that a single-word name is to be treated as a last name, not a first name.
* **get_locale**: locale can be only the language, without the country.
* if get_locale fails to get the locale from the system (because invesytoolbox may be imported from a program called from an applicatio rather than the termial), it defaults to `language: 'de'` and `country: 'AT'`.
* added support for pendulum DateTime
* **create_email_message**: fixed MIMEMultipart settings

## 0.0.21 (2023-05-21)
* New function **unravel_duration**: turns a duration string (for ex. '5T23:05:20') into a list or dictionary.

## 0.0.20 (2023-05-06)
* New function **add_time**: adds (or subtracts) time to (or from) datetime and DateTime

## 0.0.19 (2023-04-07)
* Corrected bug in **fetch_holidays** (argument *length* resulted in an error)

## 0.0.18 (2023-04-07)
* new function **change_h_tags** (in new module **itb_html**)

## 0.0.17 (2023-03-01)
* new function *compare_phonenumbers*: compares two phone numbers after normalizing them (*process_phonenumber*).

## 0.0.16
* *map_special_chars*: works now.

## 0.0.15
* *could_be_a_name*: can now handle names with multiple parts like "Robert De La Mancha". Per word, 2 capitals are allowed (i.e. "MacArthur" or "DeLa Cruz)

## 0.0.14
* *could_be_a_name* and *sort_names*: now working also with prename-only and prenames including a hyphen.

## 0.0.13
* *get_dateformat* now also processes time
* *str_to_dt* now checks for valid string
* *is_valid_datetime_string*: wrapper for checking with *str_to_dt*
* *remove_time* from datetime or DateTime

## 0.0.12
* removed documentation from the README file, instead a link to the gitlab pages
* *map_specialChars* now recognizes Unicode character U+0308 (UTF-8 cc 88 = "COMBINING DIAERESIS").
* *any_2boolean*
* *get_dateformat*: argument *checkonly*
* data functions: argument *json_data* changed to *metadata* (it's a dictionary)

## 0.0.11
* BeautifulSoup and nameparser added to requirements.txt
* Removed "Date" conversions (modified DateTime) because it's a bad idea
* *normalize_name* (using nameparser) added to *itb_text_name*
* *capitalize_name* rewritten (now quasi a wrapper for normalize_name)
* *could_be_a_name* rewritten using *normalize_name* (nameparser)

## 0.0.10
* *check_spam* for web forms
* *dictlist_2datatypes*: iterates through a list of dictionaries and applies *dict_2datatypes*
* *prettify_html*: provides *prettify* from BeautifulSoup, because it can't be used directly from restricted Python.
* *could_be_a_name*: checks if a string could be a name

## 0.0.9
* *change\_query\_string* respects Zope parameter converters (like `paramname:int`)

## 0.0.8
* New submodule www
   * *change\_query\_string*

## 0.0.7
* shorter submodule names (no _tools suffix)
* *is_holiday* works without argument
* *create\_email\_message*: new argument **encoding**
* *process_phonenumbers*: cleaned up arguments
* *DT_date*: strip a DateTime of its time (get a "naked" date)
* *could\_be\_a\_name*: check if a string could possibly be a name

## 0.0.6
* renamed *capitalize\_text* to *capitalize_name* and removed name argument
* added Sphinx documentation

## 0.0.5 (2022-06-11)
* removed **terminal_tools** (will be included in a separate package)

## 0.0.4 (2022-06-09)
* better formatted README

## 0.0.3 (2022-06-09)
* updated README (list of functions and a short description)

## 0.0.2 (2022-06-09)
* removed VERSION file

## 0.0.1 (2022-06-09)
* first version
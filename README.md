PWr-KPZ-topics-list
===================

![](https://github.com/sdatko/PWr-KPZ-topics-list/workflows/tests/badge.svg)

Topics list generator for the Konferencja Projektów Zespołowych [1] event.


Usage
-----

First modify the `config.yml` file to specify the source sheet
(with the data from the Google Form).

Then just call recent Python interpreter and run one of the included scripts.

The `generate-list-of-projects.py` produces `result.html`,
which contains a list of topics to be displayed on the event page.

The `generate-groups-for-Google-Sheets.py` produces `result.csv`,
which can be used to generate a further sheet for detailed tracking
of topics selections by students.


Form specification
------------------

This script assumes the following content
in the sheet coming from the Google Form:
- Time of submission
- Submitter e-mail
- Submitter name
- Submitter phone number
- Company name
- Project title
- Project description
- What does company offer?
- Accepted groups sizes
- How many concurrent realizations?
- Can it be conducted in English?
- Additional remarks
- Pre-reserved to a teacher?
- Shall it be displayed? (*optional*)
- How many groups still available? (*optional*)
- What language shall be used for labels? (*optional*)


Logos
-----

The first part of company name is extracted as a company ID.

If there is any file under `logos/` with name that matches the company ID
(with any extension), then this image is inserted in the table instead of
text-written name of the company.


---

[1] https://kpz.pwr.edu.pl/

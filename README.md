# Voight-Kampff Trainer

[![Build Status](https://travis-ci.org/pmourlanne/VKTrainer.svg?branch=master)](https://travis-ci.org/pmourlanne/VKTrainer)

![alt text](http://i.imgur.com/R6dTysf.gif "Let me tell you about my mother!")

This web application allows you to create training sets for feature detection on images, and do a manual tagging via your web browser.

## Installation
  - Clone this repo
  - Create a virtualenv
  - Install the requirements: `pip install -r requirements.txt`

## Demo usage
  - Bootstrap the db with test pictures: `python manage.py bootstrapdb`
  - Run the server `python manage.py runserver`
  - Go to the home (`localhost:5000` by default) and do some tagging on the `Replicants` training set
  - Extract the results from the tagging whenever you want

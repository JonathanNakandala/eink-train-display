# eink-train-display

This is an eink display that uses the National Rail API and the Open Weather API to display a dashboard on a 7.5" Waveshare e-ink Display

It runs on a Raspberry Pi

[Link to Waveshare Wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT)

## Requirements

Python 3


```
sudo apt-get install libopenjp2-7
```

## How to run

### Get API Keys

#### National Rail

Sign up and you will receive key immediately via email

https://www.nationalrail.co.uk/100296.aspx

#### Open Weather Map

Create a free account:

https://openweathermap.org/api

### Clone the repo

### Configure configuration.ini

Add your API keys and stations

### Create Python virtual environment

e.g.

```
python3 -m virtualenv env
```
```
source env/bin/activate
```

### Install requirements

```
pip install -r requirements.txt
```

### Start the script

```
python main.py
```


## Weather Icons License
Icons made by [Prosymbols](https://www.flaticon.com/authors/prosymbols)</a> from [Flaticon](www.flaticon.com)
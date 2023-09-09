# Laundry-Scraper

Python script to scrape CircuitView laundry site.

## Installation
### Desktop
1. Python 3.7+
2. Pip3
3. Google Chrome
4. WebDriver for Chrome

[Install Google Chrome](https://www.google.com/chrome/)

[Download WebDriver](https://chromedriver.chromium.org/downloads)

Choosing the appropriate WebDriver version:
1. Open Google Chrome
2. Click 3-dots in the top right corner
3. Help > About Google Chrome
4. Download the closest version to the numbers you see

Install requirements
```commandline
pip install -r requirements.txt
```
or
```commandline
pip3 install -r requirements.txt
```

### Android (Termux)
1. Termux
2. Python 3.7+
3. Pip3
4. WebDriver for Chrome

[Install Termux](https://f-droid.org/packages/com.termux/)

Open Termux

Run the following command
```commandline
termux-setup-storage
```

Reopen the Termux app
Run the following commands
```commandline
yes | pkg update -y && yes | pkg upgrade -y
pkg install python python-pip
pip install selenium==4.9.1

yes | pkg install x11-repo -y
yes | pkg install tur-repo -y
yes | pkg install chromium -y
```

Credits for Selenium installation on Termux: https://github.com/luanon404/Selenium-On-Termux-Android

## Adding more Laundry Rooms to scrape
### Get the URL to scrape
1. Go to CircuitView
2. Select your City, Accommodation Provider, Laundry Room normally
3. Click "View Laundry Room"
4. Copy the URL in the browser

### Modifying the script
Add a new ```key:value``` pair to the ```laundry_rooms``` dictionary

```
Format: Key: [List]
    Key: Numerical ID
    [List]: ["name", "target_url_to_scrape"]
```

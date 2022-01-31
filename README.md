This bot is intended to help with flight checkins, specifically Southwest.

------------------------------------------------------------------------------------
The bot is run by executing: `python3 main.py`

It will take your preferences and selections from the preferences/ directory to set up reservations.

---------------------------------------------------------------------------------------
The preferences directory currently has a couple files:

1. passengers.txt - This contains the passenger's info for the checkin, name + confirmation info

2. credentials.txt - This stores the credentials to be used to log in

4. preferences.txt - This contains the paths to the above files along with some bot settings that can be tweaked as needed

These files are txt. In hindsight, json would have been a much better choice.

---------------------------------------------------------------------------------------
If the bot fails to run because of a chromedriver error. Replace the chromedriver that is present in the topmost directory with an updated version that matches your browser version.

It is wise to run `pkill chromedrivers` from a terminal window after a few uses of the RecGovBot. When the bot reaches the booking window where you have some time before checking out, the bot detaches the browser. This allows the browser to stay open, but there will be a chromedriver process still running after closing the browser.

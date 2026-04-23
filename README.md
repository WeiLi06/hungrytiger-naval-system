## hungrytiger-naval-system
A system for resolving movement (and hopefully eventually other stuff) for Kriegsspiel.

INSTRUCTIONS /n
Clone repository
Download dependencies (to a Virtual Environment is recommended)
Move orders .csv file into the "Resources" folder
Open the supplements.py file
Enter the start time, turn duration, and game name into the respective fields
Copy the file path for the orders .csv file into the corresponding field
Run csv_fleet_test.py
Check the "Output" and "Master Files" folder for results

FOR WEATHER REPORTS:
Make sure you have a CDS (https://cds.climate.copernicus.eu/) account
Follow these instructions (https://confluence.ecmwf.int/display/CKB/How+to+install+and+use+CDS+API+on+Windows) up to step 3 (You make skip this if you have used the API before and already have a .cdsapirc credentials file)
Set "give_weather_report" in supplements.py to True
Run program as normal. This will take significantly longer as the program downloads the appropriate weather data.
IMPORTANT: DOES NOT WORK FOR DATES BEFORE 1940.

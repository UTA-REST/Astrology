import pandas as pd
import numpy as np
import os 

import astropy
from astropy.coordinates import EarthLocation

filename = "/home/pi/MultiMessenger Astrology Email Signup (Responses).xlsx"
dataframe = pd.read_excel(filename)

email_key = "Email Address"
name_key = "What is your name?"
bday_key = "What is your birthday?"
loc_key = "In which city were you born?"

new_name = "email_list.csv"
file_obj = open(new_name, 'wt')
for i in range(len(dataframe["Email Address"])):
    email = dataframe[email_key][i]
    name = dataframe[name_key][i]

    # example bday " 1991-01-21 00:00:00"
    bday = str(dataframe[bday_key][i])
    bday = (bday.split(" ")[0]).split("-")
    bday = "/".join([bday[1], bday[2], bday[0]])
     
    loc = dataframe[loc_key][i]
    try:
        gis = EarthLocation.of_address(loc)
        lat, lon = (str(gis.lat.value), str(gis.lon.value))
    except astropy.coordinates.name_resolve.NameResolveError:
        lat, lon = ("0.0" , "0.0")

    new_line = ", ".join([name, email, bday, lat, lon])
    file_obj.write( new_line+"\n")
    print(new_line)
file_obj.close()

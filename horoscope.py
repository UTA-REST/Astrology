# nothing here yet

from numpy.random import randint as rand

from classes import User, GCNEvent, get_constellation
from astropy.coordinates import get_body

options = ["a good", "an okay", "a bad"]

days =["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def make_horoscope( user_obj, event):
    if not isinstance(user_obj, User):
        raise TypeError("Expected {}, got {}".format(User, type(user_obj)))
    if not isinstance(event, GCNEvent):
        raise TypeError("Expected {}, got {}".format(GCNEvent, type(event)))

    time = event.time.datetime.isoweekday()


    
    where = "On {}, a neutrino appeared to come from {}.".format(days[time-1], get_constellation(event.coords))
    where_sun = get_constellation(get_body("sun", event.time))
    if where_sun==get_constellation(event.coords):
        where += " It appeared to fly by the sun, in the constellation {}.".format(where_sun)

    if where_sun == user_obj.sunsign:
        where += " That also happens to be your sun sign!"

    where_moon = get_constellation(get_body("moon", event.time))
    where += " Meanwhile, the moon appeared in the constellation {}".format(where_moon)
    if user_obj.moonsign == where_moon:
        where+=", which is also your moonsign!"
    else:
        where+= "."

    where += " Mars was in {}, and Venus was in {}.".format(get_constellation(get_body("mars", event.time)), get_constellation(get_body("venus", event.time)))

    return where+" Since your sign is {}, you will have {} day".format( user_obj.sunsign, options[rand(len(options))])

    

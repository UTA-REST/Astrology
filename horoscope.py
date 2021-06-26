# nothing here yet

from numpy.random import randint as rand

from classes import User, GCNEvent

options = ["Good", "Okay", "Bad"]

def make_horoscope( user_obj, event):
    if not isinstance(user_obj, User):
        raise TypeError("Expected {}, got {}".format(User, type(user_obj)))
    if not isinstance(event, GCNEvent):
        raise TypeError("Expected {}, got {}".format(GCNEvent, type(event)))

    return "You will have a {} day".format(options[rand(len(options))])


# nothing here yet

import random
from numpy.random import randint as rand

from classes import User, GCNEvent, get_constellation
from astropy.coordinates import get_body
from astropy.coordinates import solar_system_ephemeris
solar_system_ephemeris.set('de432s')

from conjunction import get_user_neutrino_sign
import os 

options = ["a good", "an okay", "a bad"]

days =["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

import json
corpus_f = open(os.path.join(os.path.dirname(__file__), "corpus.json"), 'r')
corpus_json = json.load(corpus_f)
corpus_f.close()


def make_horoscope( user_obj, event):
    if not isinstance(user_obj, User):
        raise TypeError("Expected {}, got {}".format(User, type(user_obj)))
    if not isinstance(event, GCNEvent):
        raise TypeError("Expected {}, got {}".format(GCNEvent, type(event)))

    time = event.time.datetime.isoweekday()

    special, constellation = get_user_neutrino_sign(user_obj, event)

    note = ""
    if special!="":
        note += "This event came from your {}-sign, {}, ".format(special[0].upper() + special[1:], constellation)

        mastery = corpus_json["planet_houses"][special]
        main_thing = random.choice(corpus_json["planet_assoc"][special])
        if len(mastery)==1:
            note += "which is the master of the {} house. ".format(mastery[0])

            first = random.choice(corpus_json["house_nouns"][mastery[0]])
            second = first
            while second==first:
                second = random.choice(corpus_json["house_nouns"][mastery[0]])

            note += "The neutrino carries with it an influence on your {} with your {} and {}.".format(main_thing, first, second)
        else:
            note += "which is the master of the {} and {} houses. ".format(mastery[0], mastery[1])

            first = random.choice(corpus_json["house_nouns"][mastery[0]])
            second = random.choice(corpus_json["house_nouns"][mastery[1]])

            note += "The neutrino carries an influence on your {} with regards to your {} and {}. ".format(main_thing, first, second)
            note += random.choice(corpus_json["confusion"])


    


    # We make three lists of statements:
    # 1. DefiniteStatements: A list of statements we will definitely make, 
    # 2. OptionalStatements: A list we can randomly pick from to fill out the horoscope
    OptionalStatements=[]
    DefiniteStatements=[]


    Zodiacs=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

    ZodiacSign=Zodiacs[int(event.lon/30)]


    # Make a statement based on event type
    if ('HESE' in event.r_dict['NOTICE_TYPE'].upper()):
        EventTypeStr='high energy starting event'
        EventTypeStatement=random.choice([
            "High energy starting events (HESE) are special events which deposit all their energy within the IceCube detector.  This allows the IceCube collaboration to measure their charge with great precision. Consider drawing inspiration from this HESE event and engaging in some inner introspection today.",
            "High energy starting events (HESE) are events that start inside the IceCube detector. This allows the scientists at IceCube to be sure they were not caused by external noise, but by neutrinos interacting in the ice. Consider drawing inspiration from this HESE event and shutting out external influences for a while to find inner peace.",
            "High energy starting events (HESE) were the first discovered astrophysical neutrino events, observed by IceCube in 2013. Consider taking some time to discover something new about yourself today."])
    elif ('EHE' in event.r_dict['NOTICE_TYPE'].upper()):
        EventTypeStr='extremely high energy event'
        EventTypeStatement=random.choice([
            "Extreme high energy (EHE) events are the highest energy events observed by IceCube.  Take inspiration from this EHE event and drive toward your goals this week.",
            "Extreme high energy (EHE) events deposit their energy inside IceCube but often have so much that it spills outside the array and into the glacier beyond.  Take inspiration from this EHE event and break through a barrier today.",
            "Extreme high energy (EHE) events are produced by the most energetic neutrinos observed by IceCube. Many have have escaped from the pull of black holes in distant active galactic nuclei. If these neutrinos can escape from the extreme gravity that tried to hold them back, you can free yourself from your difficulties today."])
    elif ('TRACK' in event.r_dict['NOTICE_TYPE'].upper()):
        EventTypeStatement=random.choice([
            "Astrotrack events are caused by muons created by neutrino interactions in the South Pole ice. They point back to their sources with great precision.  Take inspiration from this astrotrack event and seek to understand where you came from and where you are going, today.",
            "Astrotrack events are the most precisely localized neutrino events and allow scientists at IceCube to observe distant point sources of neutrinos that are billions of light years away.  Take inspiration from this astrotrack event and use the tools you have in hand to find your direction today. ",
            "Astrotrack events are caused by muons that draw a straight line of light through the antarctic glacial ice, pointing back to their distant astrophysical sources.  Consider seeking a lit path to follow toward your destination, however distant it may feel."])
        EventTypeStr='neutrino track event'

    DefiniteStatements.append("On {}, the IceCube Neutrino Observatory detected a ".format(days[time-1])+EventTypeStr+ " that was likely induced by a high energy astrophysical neutrino produced in a distant galaxy, interacting in the glacial ice of the South Pole.")
    DefiniteStatements.append(note)
    DefiniteStatements.append("\n")
    DefiniteStatements.append(ZodiacSign+" occupies a range of ecliptic longitudes "+ str(int(event.lon/30)*30) + " to " + str(int(event.lon/30)*30+30)+ " degrees. The neutrino detected by IceCube came from ecliptic longitude and latitude " +str(event.lon)+", " +str(event.lat)+".")
    DefiniteStatements.append("\n")
    DefiniteStatements.append(EventTypeStatement)
    DefiniteStatements.append("\n")

    SunDist=float(event.r_dict['SUN_DIST'].split('[')[0])
    MoonDist=float(event.r_dict['MOON_DIST'].split('[')[0])
    
    if(SunDist<30):
        DefiniteStatements.append("This neutrino event came from very close to the Sun (only " + str(SunDist) +" degrees away!). Sometimes flying close to the Sun is worth the risk - step outside your comfort zone today.\n")

    if(MoonDist<30):
        DefiniteStatements.append("This neutrino event came from very close to the Moon (only " + str(MoonDist) +" degrees away!). The moon may look like it waxes and wanes, but for neutrinos and cosmic rays the moon is always full.  Even at your lowest points, you are a unique and full being.\n")
    


    OptionalStatements=["Neutrinos travel as a quantum superposition of particle types, and only take on a definite type when observed.  Like the neutrino, you may sometimes be uncertain about who you are; friends can help you to observe yourself and collapse your wave function.", 
        "Neutrinos are extremely weakly interacting particles; more than 50 billion pass through your thumbnail every second.  Nevertheless, they are critical to the structure of the standard model of particle physcics. Even those who have the smallest of influences may create profound effects.", 
        "Neutrinos are unique among the particles of nature, in that they may be their own antiparticles: a yin and yang together in one circle.  Like the neutrino, sometimes we may be our own worst enemies and our own greatest allies; which we emphasize is a matter of perspective", 
        "Neutrinos are fundamental particles that oscillate as they travel.  Like neutrinos, as we move through time we evolve and change, and are not the same person at any given moment as we were in the last."]
    # Make a statement based on event type:




    
    # consider something like get_body("name", event.time, location=user.location) --> sky coordinatfrom astropy import Time e
    # then get_constellation( sky coordinate )
         
    # Now glue it all together
    OutString=""
    for d in DefiniteStatements:
        OutString=OutString+d+"\n"
    OutString=OutString+random.choice(OptionalStatements)
    return OutString

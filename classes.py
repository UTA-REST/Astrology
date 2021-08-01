from time import time as unix_time
from astropy.time import Time 
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.coordinates import  get_body

from datetime import datetime

from math import sqrt
from itertools import count, islice

def is_prime(n):
    # duh
    return n > 1 and all(n % i for i in islice(count(2), int(sqrt(n)-1)))

_constellations=["Aries", "Taurus", "Gemni", "Cancer", "Leo", 
                 "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
                 "Aquarius", "Pisces"]
assert(len(_constellations)==12)

def get_constellation(sk):
    """
    Takes a sky coordinate and returns the constellation (a string) in which this location is
    """
    if not isinstance(sk, SkyCoord):
        raise TypeError("Expected {}, got {}".format(SkyCoord, type(sk)))

    # the skycoord class is really *really* dumb, and has inconsistent class attributes depending on how it was instantiated
    # like, this is monumentally stupid design. 
    # I cannot fathom *why* anyone would ever do this 
    # this is so frustratingly stupid. 
    #   I thought the WHOLE point of a coordinate class was to do away with the ambiguities of how we define a direction?? But instead you just keep all the ambiguities?? 
    if hasattr(sk, "ra"):
        lon = sk.ra.value
    else:
        lon = sk.icrs.ra.value

    coord = int(lon/30.)
    return _constellations[coord]
    

def parse_request(request):
    """
    Make a little dictionary for each of the entries in the GCN. Doesn't really work with the SRC_RA and SRC_DEC though
    """
    r_dict = {}
    for line in request:
        split = line.split(":")
        if len(split)==1:
            continue

        key = split[0]
        val = ":".join(split[1:])
        r_dict[key] = val
    return r_dict


# For later, we can get an user's Earth Location using the 
#       EarthLocation.of_address("1234 Evergreen Terrace")
# syntax. It uses Google Maps to query their home address, and find where on Earth it is!
class User:
    """
    This class is used to hold and access information about an user on the email list. 
    
    It maintains an approximation of their latitude and longitude, their birthday, their email, their name, and has functions for accessing the various celestial bodies' locations during their birth. 
    """
    def __init__(self, row):
        row = row.split(",")
        self._name = str(row[0])
        self._email = str(row[1])
    
        bday_row = row[2].split("/")
        self._bday = Time(val=datetime(year=int(bday_row[2]), month = int(bday_row[0]), day=int(bday_row[1])), format='datetime')

        self._location = EarthLocation(lat=float(row[3]), lon=float(row[4]))

    @property
    def name(self):
        """
        Returns the user's name as a string
        """
        return self._name
    @property 
    def email(self):
        """
        returns the user's email as a string
        """
        return self._email
    @property
    def birthday(self):
        """
        Returns the user's birthday as an astropy Time location
        """
        return self._bday
    @property 
    def location(self):
        """
        Returns the user's EarthLocation, an astropy coordinate 
        """
        return self._location
    
    def _sign(self, name):
        return get_constellation(get_body(name, self.birthday, location=self.location))

    @property
    def moonsign(self):
        """
        macro for accessing the user's moonsign
        """
        return self._sign("moon")
    @property 
    def sunsign(self):
        """
        macro for acessing the user's sunsing (the normal one)
        """
        return self._sign("sun")
    def sign(self, which):
        """
        Called with a string representing a celestial body, returns a string representing in which zodiac constellationthe given body was. 

        Supports:
            sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune
        """
        return self._sign(which)

# skycoord.icrs.ra / .icrs.dec
class GCNEvent:
    """
    Class to store the raw data for a GCN event
    It uses astropy units for the time and sky coordinates

    This will then be used to make a RawFortune object necessary for writing the horoscopes 
    """
    def __init__(self, request):
        self.r_dict = parse_request(request)

        self._coords = self.parse_coords() #astropy Sky Coordinates 
        self._is_prime_runno = is_prime(int(self.r_dict["RUN_NUM"])) 

        self._energy = self.parse_energy()
        self._charge = self.parse_charge()
        self._is_track = "track" in self.r_dict["NOTICE_TYPE"].lower()
        self._time = self.parse_time() #astropy Time object! 

    @property
    def coords(self):
        return self._coords

    @property
    def lat(self):
        return self._coords.lat.value
    @property
    def lon(self):
        return self._coords.lon.value

    @property
    def energy(self):
        return self._energy
    
    @property
    def time(self):
        return self._time

    @property 
    def prime(self):
        return self._prime

    def parse_energy(self):
        if 'ENERGY' in self.r_dict.keys():
            unit_str = self.r_dict["ENERGY"].split("[")[1].split("]")[0]
            unit_scale = 1.0
            if unit_str=="GeV":
                pass
            elif unit_str=="TeV":
                unit_scale = 1e3
            elif unit_str=="PeV":
                unit_scale = 1e6

            return unit_scale*float(self.r_dict["ENERGY"].split("[")[0])
        else:
            return 0

    def parse_charge(self):
        if 'CHARGE' in self.r_dict.keys():
            return float(self.r_dict["CHARGE"].split("[")[0])
        else:
            return 0

    def parse_coords(self):
        coord = self.r_dict['ECL_COORDS'].split(",")
        lon = float(coord[0])
        lat = float(coord[1].split("[")[0])
        return SkyCoord(lon,lat,unit='deg',frame='geocentrictrueecliptic')


    def parse_time(self):
        parsed = self.r_dict["DISCOVERY_DATE"].split(';')[-1].split("/")
        year = int(parsed[0]) + 2000
        month= int(parsed[1])
        day = int(parsed[2].split("(")[0])

        parsed = self.r_dict["DISCOVERY_TIME"].split("{")[1].split("}")[0].split(":")
        hour = int(parsed[0])
        minute = int(parsed[1])
        second = int(float(parsed[2]))

        microsecond = int((float(parsed[2]) - second)*(1e6))

        return Time(val=datetime( year=year, month=month, day=day, hour=hour, 
                minute=minute, second=second, microsecond=microsecond), format="datetime")


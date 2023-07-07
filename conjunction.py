"""
Function for determining all conjunctions of planets given an astropy time coordinate
"""

from astropy.time import Time 
from astropy.coordinates import solar_system_ephemeris, EarthLocation
from astropy.coordinates import  get_body

from classes import User, GCNEvent, get_constellation

solar_system_ephemeris.set('de432s')

BODIES = solar_system_ephemeris.bodies #tuple 
SKIP_KEY = ["earth-moon-barycenter", "earth"]
CONJ_DEG = {
    "conjunction": 0, 
    "sextile":60, 
    "square":90,
    "trine":120,
    "injunction":150,
    "opposition":180
}
CONJ_ERR = {
    "conjunction": 10, 
    "sextile":6, 
    "square":5,
    "trine":10,
    "injunction":2,
    "opposition":10
}


def get_user_neutrino_sign(user:User, event:GCNEvent)->str:
    """
        Each planet was in a constellation at the User's birth. 
        This returns the first planet that was in event's constellationat the time of the user's birth. 

        Returns an empty string if no such planet was there. 
    """
    event_cons = get_constellation(event.coords) # string

    chosen = ""
    for body in BODIES:
        if body in SKIP_KEY:
            continue

        body_loc = get_body(body, user.birthday)
        body_cons = get_constellation(body_loc)

        if event_cons == body_cons:
            chosen = body
            break
    
    return chosen , body_cons

def get_conjunctions(time: Time, location:EarthLocation)->dict:
    """
        takes astropy Time, returns dict 
    """

    lines_found = {key:[] for key in CONJ_ERR.keys()}

    # these are SO SLOW to look up... 
    ras = {body_name:get_body(body_name, time).ra.value for body_name in BODIES}

    for i in range(len(BODIES)):
        if BODIES[i] in SKIP_KEY:
            continue
        
        ra1 = ras[BODIES[i]]

        # some index logic so we don't check everything twice (and so we don't get self-conjunctions)
        for j in range(len(BODIES)-i):
            if BODIES[len(BODIES)-j-1] in SKIP_KEY:
                continue
            if i==(len(BODIES)-j-1):
                continue
        
            ra2 = ras[BODIES[len(BODIES)-j-1]]
            diff = abs(ra2 - ra1)

            print("Checking {}-{}".format(BODIES[i], BODIES[len(BODIES)-j-1]))
            # check for each type of line 
            for key in CONJ_DEG.keys():
                if abs(CONJ_DEG[key] - diff) < CONJ_ERR[key]:
                    # found one! 
                    lines_found[key].append(( BODIES[i], BODIES[len(BODIES)-j-1] ))
    
    print(lines_found)
    return lines_found

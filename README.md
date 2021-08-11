# Multimessenger Astrology 

We need that SEO 

Overall structure
    1. Get events through GCN alerts, build object with all relevant information
    2. Get user's locations, birthday, name, etc
    3. Collect locations of relevant celestial bodies, find their sky-locations (constellations) relative to user. 
    4. Determine if bodies are rising/falling, etc.
    5. Construct horoscope for each user from (3) and (4)
    6. Send uniquely constructed horoscope to each user  

# What's here

We've written two datatypes (`classes.py`),
    - User: constructed from the email list. Way of accessing all the information about an user needed to write a horoscope 
    - GCNEvent construced from the GCN events that we parse from the alerts. Keeps the neutrino event data relevant to constructing a horoscope 

# To-Do

## Cron Jobs
Use crontab to regularly call a python script checking email. 
This function will support the actions below 

```
*/5 * * * * /usr/bin/python3.8 /path/to/emailing.py
```

### Actions

- neutrino event email. It checks the sender and verifies it's from the gcn people. Then it parses the email, and writes a horoscope for everyone on the email list 

- subscribe. Add a new person to the email list. The person should specify their latitiude, longitude, and birthday. If no birthday is given, then the an email is sent in responce specifying the error. Subscriptions will be held in a csv file 

- unsubscribe. The email address entry is removed from the subscription csv file

### Emailing 

See `emailing.py`.

Right now this provides a function for sending a mass email out to everyone on an email list. You send it a GCNEvent object, and it writes a unique horoscope for everyone.

I set up a gmail account `multimessengerastrology` for this purpose. The email list and password are not, and never will be, stored on the git repository. I keep those local.

## Horoscope Writing  

See `horoscope.py`.

Develop function that returns a horoscope from an User object, and a GCNEvent object.
This horoscope should return a string

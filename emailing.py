import smtplib, ssl
import os
import numpy as np
from classes import User, GCNEvent
from horoscope import make_horoscope

from datetime import datetime
import requests

port = 465

astrodir = os.path.join(os.path.expandvars("$HOME"), ".local","mmAstro")

pfile = os.path.join(astrodir, "astropass.dat")
f = open(pfile)
password = f.readline().split("\n")[0]
f.close()

sender_email = "multimessengerastrology@gmail.com"

def email_all(event):
    if not isinstance(event, GCNEvent):
        raise TypeError("Need {} to email list, not {}".format(GCNEvent, type(event)))

    email_file = "email_list.csv"
    fname = os.path.join(astrodir, email_file)
    data = np.loadtxt(fname, dtype="str", delimiter=",")

    if type(data[0])==np.str_: # if there's only one email, it's loaded in as a 1D array of strings, not a 2D array 
        # I hate this workaround 
        data = [list(data)]
    for row in data:
        row = ",".join(row)
        context = ssl.create_default_context()

        this_user = User(row)
        horoscope = "" 

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            
            dest_email = this_user.email
            this_horoscope = make_horoscope(this_user, event)

            message = """\
            From: Multi-Messenger Astrology Specialists at UTA\n
            Subject: Your Neutrinoly Horoscope

            """
            message += "Dear {},\n".format(this_user.name)
            message += this_horoscope
            
            print(message)
            server.sendmail(sender_email, dest_email, message)

        print("Sent email to {}".format(this_user.name))

# Importing libraries
import imaplib, email

imap_url = 'imap.gmail.com'

# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

# Function to search for a key value pair
def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data

# Function to get the list of emails under this label
def get_emails(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)

    return msgs

def getthem():
    
    # this is done to make SSL connnection with GMAIL
    con = imaplib.IMAP4_SSL(imap_url)

    # logging the sender_email in
    con.login(sender_email, password)

    # calling function to check for email under this label
    con.select('Inbox')

    # fetching emails from this sender_email "tu**h*****1@gmail.com"
    msgs = get_emails(search('FROM', '*', con))

    # Uncomment this to see what actually comes as data
    # print(msgs)


    # Finding the required content from our msgs
    # User can make custom changes in this part to
    # fetch the required content he / she needs

    # printing them by the order they are displayed in your gmail

    results = []
    for msg in msgs[::-1]:
        for sent in msg:
            if type(sent) is tuple:

                # encoding set as utf-8
                content = str(sent[1], 'utf-8')
                data = str(content)
                
                print(data)
                # Handling errors related to unicodenecode
                try:
                    indexstart = data.find("ltr")
                    data2 = data[indexstart + 5: len(data)]
                    indexend = data2.find("</div>")

                    # printtng the required content which we need
                    # to extract from our email i.e our body
                    results.append(data2[0: indexend])

                except UnicodeEncodeError as e:
                    print(e)
                    pass
            else:
                print(type(sent))

    return results

def is_datelike(segment):
    return len(segment.split("/"))==3
def is_timelike(segment):
    return len(segment.split(":"))==3

def get_since_day(date):
    if not isinstance(date, datetime):
        raise TypeError()

    r = requests.get("https://gcn.gsfc.nasa.gov/amon_icecube_gold_bronze_events.html",allow_redirects=True)
    r = r.text.split("\n")

    last_date = datetime(1970, 1, 1)
    addy = ""

    urls = []
    for line in r:
        if line =="":
            continue

        parsed = line.split("<td><a href=")
        if len(parsed)!=1:
            parsed = parsed[1].split("</a></td>")[0]
            addy = parsed.split(">")[0]

        parsed = line.split("<td align=left>")
        if len(parsed)!=1:
            parsed = parsed[1].split("</td>")[0]
            if is_datelike(parsed):
                split = parsed.split("/")
                this_date = datetime(int(split[0])+2000, int(split[1]), int(split[2]))
                if this_date==last_date:
                    continue
                else:
                    last_date = this_date 

                    if this_date < date:
                        break
                    else:
                        urls.append("https://gcn.gsfc.nasa.gov/"+addy)
            if is_timelike(parsed):
                continue
    print(urls[::-1])
    return urls[::-1]

def update():
    # check for sub/unsub

    # check for new alerts
    f=open(os.path.join(astrodir, "last_sent.dat"), 'r')
    line = f.readline().split("/")
    f.close()
    last_sent_date = datetime(int(line[0]), int(line[1]), int(line[2]))

    today_dt = datetime.today()
    today = datetime(today_dt.year, today_dt.month, today_dt.day)
    if last_sent_date==today:
        # max one email per day!
        return
    
    # check if anything new has come in! 
    urls = get_since_day(last_sent_date)
    if len(urls)==0:
        return # nothing new 
    else: 
        print("Found something new")
        # AAAAAHH! 
        for url in urls:
            # get the event for each url (should only ever be one...) 
            r = str(requests.get(url, allow_redirects=True).content)
            r = r.split("\\n")
            event = GCNEvent(r)
            email_all(event)
        
        f = open(os.path.join(astrodir, "last_sent.dat"), 'wt')
        f.write("{}/{}/{}\n".format(today.year, today.month, today.day))
        f.close()
        

if __name__=="__main__":
    update()

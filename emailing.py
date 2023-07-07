import smtplib, ssl
import os
import numpy as np
from classes import User, GCNEvent
from horoscope import make_horoscope
from email.message import EmailMessage

from datetime import datetime
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


port = 465

astrodir = os.path.join(os.path.expandvars("$HOME"), ".local","mmAstro")

pfile = os.path.join(astrodir, "astropass.dat")
f = open(pfile)
password = f.readline().split("\n")[0]
f.close()

sender_email = "multimessengerastrology@gmail.com"

SCOPES = ['https://mail.google.com/']


def email_all(event):
    if not isinstance(event, GCNEvent):
        raise TypeError("Need {} to email list, not {}".format(GCNEvent, type(event)))

    email_file = "email_list.csv"
    #email_file = "test_list.csv"
    fname = os.path.join(astrodir, email_file)
    #fname = "./"+email_file
    data = np.loadtxt(fname, dtype="str", delimiter=",")

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    if type(data[0])==np.str_: # if there's only one email, it's loaded in as a 1D array of strings, not a 2D array 
        # I hate this workaround 
        data = [list(data)]

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    for row in data:
        row = ",".join(row)
        context = ssl.create_default_context()

        this_user = User(row)
        horoscope = "" 

        print("Sending email to {}".format(this_user.name))

            
        msg = EmailMessage()

        split = (this_user.name).split(" ")
        i_use = 0
        while split[i_use]=="":
            i_use+=1 
            if i_use==len(split):
                break
        if i_use==len(split):
            # no non-empty name found This is a bad entry! 
            print("Bad name? {}".format(this_user.name))
            break


        this_horoscope = make_horoscope(this_user, event) 
        msg_text = "Dear {},\n".format(split[i_use])
        msg_text += this_horoscope

        msg.set_content( msg_text )
        
        msg["To"]       = this_user.email
        msg["From"]     = "The Multi-Messenger Astrology Specialists"
        msg["Subject"]  = "Your Neutrinoly Horoscope"

        encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        create_message = {
                    'raw': encoded_message
            }
        
        print("Sent email to {}".format(this_user.name))
        
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        
        

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

                    if this_date <= date:
                        continue
                    else:
                        urls.append("https://gcn.gsfc.nasa.gov/"+addy)
            if is_timelike(parsed):
                continue
#    print(urls[::-1])
    return urls[::-1]

def update():
    # check for sub/unsub

    # check for new alerts
    f=open(os.path.join(astrodir, "last_sent.dat"), 'r')
    line = f.readline().split("/")
    f.close()
    last_sent_date = datetime(int(line[0]), int(line[1]), int(line[2]))

    today_dt = datetime.utcnow()
    today = datetime(today_dt.year, today_dt.month, today_dt.day)
    if last_sent_date==today:
        # max one email per day!
        return
    
    # check if anything new has come in! 
    urls = get_since_day(last_sent_date)
    if len(urls)==0:
        print("Nothing to update")
        return # nothing new 
    else: 
        print("Found something new")
        # AAAAAHH! 
        for url in urls:
            print("Grabbing from {}".format(url))
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

import smtplib, ssl
import os
import numpy as np
from classes import User, GCNEvent
from horoscope import make_horoscope

port = 465

astrodir = os.path.join(os.path.expandvars("$HOME"), ".local","mmAstro")

pfile = os.path.join(astrodir, "astropass.dat")
f = open(pfile)
password = f.readline().split("\n")[0]
f.close()

sender_email = "multimessengerastrology@gmail.com"

def email_all(event):
    if not isinstance(GCNEvent):
        raise TypeError("Need {} to email list, not {}".format(GCNEvent, type(event)))

    email_file = "email_list.csv"
    fname = os.path.join(astrodir, email_file)
    data = np.loadtxt(email_file, dtype="str", delimiter=",")
    for row in data:
        context = ssl.create_default_context()

        this_user = User(row)
        horoscope = 

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            
            dest_email = this_user.email
            this_horoscope = make_horoscope(this_user, event)

            message = """
            Subject: Your Neutrinoly Horoscope

            """
            message += "Dear, {}\n".format(this_user.name)
            message += this_horoscope

            server.sendmail(sender_email, dest_email, message)

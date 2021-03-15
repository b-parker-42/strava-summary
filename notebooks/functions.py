from datetime import datetime, date
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

# secrets
from secrets import *

def get_strava_range():
    today = date.today()
    # Get datetime for first day of current month
    first_of_month = datetime(today.year, today.month, 1)

    # Get datetime for first day of previous month
    if today.month == 1:
        fopm_month = 12
        fopm_year = today.year - 1
    else:
        fopm_month = today.month - 1 
        fopm_year = today.year
    first_of_prev_month = datetime(fopm_year, fopm_month, 1)

    # Calc and return epochs for each
    fom_epoch = first_of_month.timestamp()
    fopm_epoch = first_of_prev_month.timestamp()

    return first_of_month, first_of_prev_month


def send_email(receiver_address, date_str, monthly_data):
    # Email details
    email = MIMEMultipart("alternative")
    email["Subject"] = "Strava - " + date_str
    email["From"] = sender_address
    email["To"] = receiver_address

    # Add email content
    pre_text = """\
    <html>
      <body>
        <p>Hola Speedy Gonzales,<br>
           <br>
           Here's what you got up to last month....
        </p>
      </body>
    </html>
    """

    post_text = """\
    <html>
      <body>
        <p>
           <a href="https://www.strava.com/dashboard#_=_">Strava</a>
           
        </p>
      </body>
    </html>
    """

    html_str = pre_text + monthly_data + post_text
    html = MIMEText(html_str, "html")
    email.attach(html)

    #Create SMTP session for sending the mail
    try:
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pword)
        session.sendmail(sender_address, receiver_address, email.as_string())
        print('Email sent to: ', receiver_address)
        # save_sent_html(date_str, html_str)
    except Exception as e:
        print(e)
        raise
    finally:
        session.quit()
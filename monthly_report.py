from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os, datetime
import psycopg2
import pandas as pd
from dateutil.relativedelta import relativedelta

load_dotenv('.env')

hostname = 'localhost'
database = 'infosys'
username = 'postgres'
pwd = os.getenv('pwd')
port_id = 5432

def SendMonthlyReport():

    msg = MIMEMultipart()
    msg['Subject'] = 'Monthly Attendance Report'
    msg['From'] = os.getenv('email')
    msg['To'] = os.getenv('gmail')

    message = 'Please find attached the attendance data for the month.'
    text = MIMEText(message)
    msg.attach(text)

    con = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = con.cursor()
    today = datetime.datetime.today()
    lastm = today - relativedelta(months=1)
    print(f'Collecting data from {lastm} till today...')
    today, lastm = today.strftime('%Y-%m-%d'), lastm.strftime('%Y-%m-%d')
    total_classes = 30
    cur.execute(f'''SELECT s.name AS student_name, sub.name AS subject_name, 
    {total_classes} AS total_classes,
    COUNT(*) AS days_present,
    {total_classes} - COUNT(*) AS days_absent,
    (COUNT(*) * 100.0) / {total_classes} AS attendance_percentage
    FROM attendence a
    JOIN student s ON a.student_id = s.id
    JOIN subject sub ON a.subject_id = sub.id
    WHERE a.date >= \'{lastm}\' AND a.date <= \'{today}\'
    GROUP BY s.name, sub.name;''')
    df = pd.DataFrame(cur.fetchall(), columns=['student_name', 'subject_name', 'total_classes', 'days_present', 'days_absent', 'attendance_percentage'])
    print(df.head())

    # Reset the index to make the DataFrame easier to read
    df.reset_index(drop=True, inplace=True)
    df.to_csv('monthly.csv')
    cur.close()
    con.close()

    with open('monthly.csv','rb') as file:
    # Attach the file with filename to the email
        msg.attach(MIMEApplication(file.read(), Name='monthly.csv'))

    s = smtplib.SMTP('smtp.office365.com', 587) #'smtp.gmail.com', 587)  
    s.starttls()
    s.login(os.getenv('email'), os.getenv('epw'))
    s.sendmail(os.getenv('email'), os.getenv('gmail'), msg.as_string())
    s.quit()

SendMonthlyReport()
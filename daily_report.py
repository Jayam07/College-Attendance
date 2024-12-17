from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os, datetime
import psycopg2
import pandas as pd
import cv2

load_dotenv('.env')

hostname = 'localhost'
database = 'infosys'
username = 'postgres'
pwd = os.getenv('pwd')
port_id = 5432

def SendDailyReport():

    msg = MIMEMultipart()
    msg['Subject'] = 'Daily Attendance Report'
    msg['From'] = os.getenv('email')
    msg['To'] = os.getenv('gmail')

    message = 'Please find attached the attendance data for today - the .csv file & student images.'
    text = MIMEText(message)
    msg.attach(text)

    con = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = con.cursor()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    cur.execute(f'''SELECT s.name AS student_name, sub.name AS subject_name
                FROM attendence a JOIN student s ON a.student_id = s.id 
                JOIN subject sub ON a.subject_id = sub.id 
                where date = \'{today}\';''')
    df = pd.DataFrame(cur.fetchall(), columns=['student_name', 'subject_name'])
    print(df.head())

    # img_b = cv2.imread(img_path)
    # # Encode the image as a JPEG or PNG
    # _, img_encoded = cv2.imencode('.jpg', img_b)
    # # Convert the encoded image to bytes
    # image_bytes = img_encoded.tobytes()
    cur.execute(f'select * from group_image where date = \'{today}\';')
    df_imgs = pd.DataFrame(cur.fetchall())
    for index, row in df_imgs.iterrows():
        [id, date_, image_bytes, sub_id] = row
        cur.execute(f'select name from subject where id = {sub_id};')
        sub_name = cur.fetchone()[0]
        image = MIMEImage(bytes(image_bytes), name=os.path.basename(f'{sub_name}_{date_}'))
        msg.attach(image)

    # Pivot the DataFrame to get the desired format
    pivot_df = df.pivot(columns='subject_name', values='student_name')
    print(pivot_df.head())
    # Reset the index to make the DataFrame easier to read
    pivot_df.reset_index(drop=True, inplace=True)
    pivot_df.to_csv('daily.csv')
    cur.close()
    con.close()

    with open('daily.csv','rb') as file:
    # Attach the file with filename to the email
        msg.attach(MIMEApplication(file.read(), Name='daily.csv'))

    s = smtplib.SMTP('smtp.office365.com', 587) #'smtp.gmail.com', 587)  
    s.starttls()
    s.login(os.getenv('email'), os.getenv('epw'))
    s.sendmail(os.getenv('email'), os.getenv('gmail'), msg.as_string())
    s.quit()

img_path = r'C:\Users\anush\OneDrive\Desktop\Work\Infosys-attendance\dataset\test\group\04072024080553.jpeg'
SendDailyReport()
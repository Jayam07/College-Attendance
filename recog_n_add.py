from deepface import DeepFace
from retinaface import RetinaFace
import os
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import psycopg2
from datetime import datetime
from dotenv import load_dotenv 

def recognize_single(img):

    # img_loaded = cv2.imread(img)
    # img_loaded = cv2.cvtColor(img_loaded, cv2.COLOR_BGR2RGB)
    dataset_path = r'C:\Users\anush\OneDrive\Desktop\Work\Infosys-attendance\dataset'
    training_data = os.path.join(dataset_path, 'train')

    results = {}
    for person in os.listdir(training_data): 
        train_img = os.listdir(os.path.join(training_data, person))[0]
        train_img = os.path.join(training_data, person, train_img)
        # train_loaded = cv2.imread(train_img)
        # train_loaded = cv2.cvtColor(train_loaded, cv2.COLOR_BGR2RGB)
        result = DeepFace.verify(img1_path=img, img2_path=train_img, model_name='Facenet')#, enforce_detection=False)
        results[person] = [result['verified'], 1 - result['distance']]
        # print(results[person])
        # # Display the test image on the left
        # plt.subplot(1, 2, 1)
        # plt.imshow(img_loaded)
        # plt.title("Test Image")
        # plt.axis('off')  # Hide axes

        # # Display the training image on the right
        # plt.subplot(1, 2, 2)
        # plt.imshow(train_loaded)
        # plt.title(f"Training Image: {person}")
        # plt.axis('off')  # Hide axes

        # # Show the plot
        # plt.show()
        # print('---------------------------------')

    max_sim = max([x[1] for x in results.values()])
    for key, value in results.items():
        if value[1] == max_sim:
            target_person = key
            break
    print(f'Student ID {target_person} detected')

    return target_person 

def process_grp(img_path):
    results = []
    faces = RetinaFace.extract_faces(img_path)
    print(f'{len(faces)} faces detected')
    print('Analyzing...')
    # img_loaded = cv2.imread(img_path)
    # img_laoded = cv2.cvtColor(img_loaded, cv2.COLOR_BGR2RGB)
    for face in faces:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        cv2.imwrite('face.jpg', face)
        with open('face.jpg', 'rb') as file:
            img_b = file.read()
        result = [recognize_single('face.jpg'), img_b]
        results.append(result)
    return results

def get_subject(time_):
    con = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = con.cursor()
    query = f"select id from subject where '{time_}' > from_time and '{time_}' < to_time;"
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    con.close()
    print(f'Subject ID {result} attended')
    return result

def mark(date_, subject_id, student_id, img_b):
    con = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = con.cursor()
    cur.execute('select max(id) from attendence;')
    max_id = cur.fetchone()[0]
    if max_id is None:
        id = 1
    else:
        id = max_id + 1
    query = "INSERT INTO attendence (id, date, subject_id, student_id, image) VALUES (%s, %s, %s, %s, %s);"
    cur.execute(query, (id, date_, subject_id, student_id, img_b))
    con.commit()
    cur.close()
    con.close()
    print(f'Attendance marked for Student ID {student_id} for Subject ID {subject_id}')

def save_grp(date_, img_path, subject_id):
    con = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    cur = con.cursor()
    cur.execute('select max(id) from group_image;')
    max_id = cur.fetchone()[0]
    if max_id is None:
        id = 1
    else:
        id = max_id + 1
    query = "INSERT INTO group_image VALUES ( %s, %s, %s, %s);"
    with open(img_path, 'rb') as file:
        img_b = file.read()
    cur.execute(query, (id, date_, img_b, subject_id))
    con.commit()
    cur.close()
    con.close()
    print(f'Group image stored')

# test_img = r'C:\Users\anush\OneDrive\Desktop\Work\Infosys-attendance\dataset\test\single\122.jpg'
# print(recognize_single(test_img))

load_dotenv('.env')

hostname = 'localhost'
database = 'infosys'
username = 'postgres'
pwd = os.getenv('pwd')
port_id = 5432

def take_attendance(img_path):
    results = process_grp(img_path)
    time_str = img_path.split('\\')[-1].split('.')[0]
    parsed_time = datetime.strptime(time_str, '%d%m%Y_%H%M%S')
    formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
    [date_, time_] = formatted_time.split(' ')
    subject_id = get_subject(time_)
    save_grp(date_, img_path, subject_id)
    for [student_id, img_b] in results:
        mark(date_, subject_id, student_id, img_b)
    return subject_id, date_, img_path

img_path = r'C:\Users\anush\OneDrive\Desktop\Work\Infosys-attendance\dataset\test\group\09072024_120233.jpg'
take_attendance(img_path)

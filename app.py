from flask_mysqldb import MySQL
import pygame
import os
from flask import Flask, request, render_template, redirect, url_for, jsonify
from collections import deque
from threading import Thread, Event
import time
import pyttsx3
import threading

app = Flask(__name__, static_folder='assets')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'littlekiddos'

mysql = MySQL(app)

@app.route('/index')
def index():
    return render_template('index2.html')

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user(username)
        password = get_pass(password)

        # Perform validation based on the obtained images
        if user and not password:
            # Handle the case where password is wrong
            play_audio('assets/music/error.mp3')
            error_message = 'Wrong Password.'
            return render_template('login.html', error_message=error_message)
        elif password and not user:
            # Handle the case where username is not found
            play_audio('assets/music/error.mp3')
            error_message = 'Username not found.'
            return render_template('login.html', error_message=error_message)
        elif user and password:
            # Handle the case where username and password are correct
            return render_template('index2.html', user=user)

def get_user(username):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query to fetch the student image based on the student ID
    cur.execute("SELECT username FROM userlist WHERE username = %s", (username,))
    result = cur.fetchone()

    # Close the database connection
    cur.close()

    if result:
        # Return the student image filename if found in the database
        return result[0]

    # Return None if no matching record found
    return None

def get_pass(password):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query to fetch the student image based on the student ID
    cur.execute("SELECT password FROM userlist WHERE password = %s", (password,))
    result = cur.fetchone()

    # Close the database connection
    cur.close()

    if result:
        # Return the student image filename if found in the database
        return result[0]

    # Return None if no matching record found
    return None

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        secretcode = request.form.get('clientid')

        clientid = get_clientid(secretcode)

        if not clientid:
            # Handle the case where clientid is not found
            play_audio('assets/music/error.mp3')
            error_message = 'Client ID is not valid.'
            return render_template('register.html', error_message=error_message)
        else:
            # Insert the student data into the database
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO userlist (username,password,clientid)
                        VALUES (%s, %s, %s)''', (username, password, secretcode))
            mysql.connection.commit()
            cur.close()

            return redirect('/')

def get_clientid(secretcode):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query to fetch the student image based on the student ID
    cur.execute("SELECT clientcode FROM clientlist WHERE clientcode = %s", (secretcode,))
    result = cur.fetchone()

    # Close the database connection
    cur.close()

    if result:
        # Return the student image filename if found in the database
        return result[0]

    # Return None if no matching record found
    return None

@app.route('/studentlist')
def studentlist():   
    # Fetch all the student data from the mysql database
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM studentlist''')
    students = cur.fetchall()
    cur.close()

    return render_template('studentlist.html', students=students)

@app.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    if request.method == 'GET':
        return render_template('addstudent.html')
    
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        nickname = request.form.get('nickname')
        student_image = request.files['student_image']
        parent_image = request.files['parent_image']

        # Save the uploaded files
        student_image_path = os.path.join('assets/pics', student_image.filename)
        parent_image_path = os.path.join('assets/pics', parent_image.filename)
        student_image.save(student_image_path)
        parent_image.save(parent_image_path)

        # Insert the student data into the database
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO studentlist (fullname, nickname, simage, pimage)
                    VALUES (%s, %s, %s, %s)''', (fullname, nickname, student_image_path, parent_image_path))
        mysql.connection.commit()
        cur.close()

        return redirect('/studentlist')
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if request.method == 'POST':
        # Retrieve the updated student data from the form
        fullname = request.form['fullname']
        nickname = request.form['nickname']

        # Update the student data in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE studentlist SET fullname = %s, nickname = %s WHERE id = %s", (fullname, nickname, id))
        mysql.connection.commit()
        cur.close()

        # Redirect to the student list page
        return redirect('/studentlist')

    # Retrieve the student data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM studentlist WHERE id = %s", (id,))
    student = cur.fetchone()
    cur.close()

    if student:
        return render_template('updatestudent.html', student=student)
    else:
        return "Student not found"

@app.route('/delete/<int:id>')
def delete_student(id):
    # Delete the student from the database
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM studentlist WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    # Redirect to the student list page
    return redirect('/studentlist')

@app.route('/result', methods=['POST'])
def result():
    input_text = request.form['nickname']
    image_kid = get_image_kid(input_text)
    image_parent = get_image_parent(input_text)
    name_kid = get_name_kid(input_text)

    # Perform validation based on the obtained images
    if image_kid and image_parent:
        # Both images are found, perform further processing
        # Play the alert sound here
        play_audio('assets/music/doorbell.mp3')
        return render_template('result.html', image_kid=image_kid, image_parent=image_parent, name_kid=name_kid)
    else:
        # Handle the case where images are not found
        play_audio('assets/music/error.mp3')
        error_message = 'No data found'
        return render_template('index2.html', error_message=error_message)

def get_name_kid(input_text):
    #fetch the student name from the database

    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query to fetch the id based on the nickname
    cur.execute("SELECT fullname FROM studentlist WHERE nickname = %s", (input_text,))
    result = cur.fetchone()

    # Execute the query to fetch the student name based on the student ID
    # cur.execute("SELECT fullname FROM studentlist WHERE id = %s", (input_text,))
    # result = cur.fetchone()

    # Close the database connection
    cur.close()

    if result:
        # Return the student name if found in the database
        return result[0]

    # Return None if no matching record found
    return None

def get_image_kid(input_text):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query to fetch the student image based on the student ID
    cur.execute("SELECT simage FROM studentlist WHERE nickname = %s", (input_text,))
    result = cur.fetchone()

    # Close the database connection
    cur.close()

    if result:
        # Return the student image filename if found in the database
        return result[0]

    # Return None if no matching record found
    return None

def get_image_parent(input_text):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the query to fetch the parent image based on the student ID
    cur.execute("SELECT pimage FROM studentlist WHERE nickname = %s", (input_text,))
    result = cur.fetchone()

    # Close the database connection
    cur.close()

    if result:
        # Return the parent image filename if found in the database
        return result[0]

    # Return None if no matching record found
    return None

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Usage example
# play_audio('path/to/your/audio.mp3')

if __name__ == '__main__':
    app.run()

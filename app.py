from flask import Flask, render_template,request, redirect, url_for, session
import pymysql
import requests
import html
import random

app=Flask("__name__")

app.secret_key= "super secret key"

# Making connections with MYSQL database
server="localhost"
user="root"
password=""

db=pymysql.connections.Connection(
    host=server,
    user=user,
    password=password
)

cursor=db.cursor()

# Creating database and tables
cursor.execute("CREATE DATABASE IF NOT EXISTS quiz_register")
cursor.execute("USE quiz_register")
cursor.execute("CREATE TABLE IF NOT EXISTS user_data(srno int AUTO_INCREMENT UNIQUE,user_name VARCHAR(50) NOT NULL PRIMARY KEY, password VARCHAR(20) NOT NULL);")
cursor.execute("CREATE TABLE IF NOT EXISTS user_score(user_name VARCHAR(50), gk INT(10), sports INT(10), computer INT(10), science INT(10), history INT(10), FOREIGN KEY(user_name) REFERENCES user_data(user_name));")


# List of quiz
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", username=session['username'])


# previous scores in different tests
@app.route('/previous_results')
def previous_results():
    username=session["username"]
    cursor.execute("SELECT * FROM user_score WHERE BINARY user_name=%s",(username,))
    score=cursor.fetchone()
    if score:
        session['gk']=score[1]
        session['sports']=score[2]
        session['computer']=score[3]
        session['science']=score[4]
        session['history']=score[5]
    else:
        return "do quiz first"
    
    return render_template('previous_results.html', username=session["username"], gk=session['gk'], sports=session['sports'], computer=session["computer"], science=session['science'], history=session['history'])


# Registering new users
@app.route('/',methods=['GET', 'POST'])
def register():
    msg=''
    if request.method=='POST':
        name=request.form.get("uname")
        user_password=request.form.get("password")

        # Checking if user exists or not 
        cursor.execute('SELECT * FROM user_data WHERE BINARY user_name=%s',(name,))
        data=cursor.fetchone()
        if not data:
            cursor.execute("INSERT INTO `user_data` (`user_name`, `password`) VALUES (%s, %s)",(name,user_password))
            cursor.execute("INSERT INTO user_score (user_name) VALUES (%s)",(name,))
            db.commit()
            return redirect(url_for('login'))
        else:
            msg="username already exists"
    return render_template("register.html", msg=msg)


# login page 
@app.route('/login', methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST':
        userId=request.form.get('user')
        userPassword=request.form.get('password')

        # checking user name and password in database
        cursor.execute('SELECT * FROM user_data WHERE BINARY user_name=%s AND BINARY password=%s',(userId,userPassword))
        data=cursor.fetchone()
        if data:
            session['loggedin']=True
            session['username']=data[1]
            return redirect(url_for('dashboard'))
        else:
            msg= 'Invalid user id or password, Try again!'
    return render_template("login.html",msg=msg)


# logout button
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop("username", None)
    return redirect(url_for('login'))


# code for quiz
q_list=[]
decoded_question=[]
correct=[]
incorrect=[]
options=[]
decoded_options=[]


# getting links from html form
@app.route('/link', methods=['POST','GET'])
def link():
    session['url']=request.form['value']
    url=session['url']
    global req
    req=requests.get(url)
    global response
    response=str(req.status_code)

        # checking connection

    if response=="200":
        data=req.json()["results"]
        global length
        length=len(data)

        # Appending data like questions and answers in empty lists
        for i in range(0,length):
            q_list.append(data[i]["question"])
            correct.append(data[i]["correct_answer"])
            incorrect.append(data[i]["incorrect_answers"])

        if not decoded_question:            # for preventing repeation of option after reload

            # decoding the questions
            for q in q_list:
                edited=html.unescape(q)
                decoded_question.append(edited)

            # merging correct and incorrect options
            for i in range(0,len(correct)):
                incorrect[i].insert(0,correct[i])

            # decoding the options
            for answer in incorrect:
                for i in answer:
                    edited=html.unescape(i)
                    options.append(edited)
                            
            # making pair of all options according to the nummber of options i.e 4          
            for i in range(0,len(options),4):
                decoded_options.append(options[i:i+4])

            # shuffling options  
            for mcq in decoded_options:
                random.shuffle(mcq)
        return redirect(url_for('quiz'))
    
     
# code for quiz home page (questions and answers)
@app.route('/quix_index', methods=["POST","GET"])
def quiz():
    
    if response=="200":           
        return render_template("index.html", length=length, decoded_question=decoded_question, decoded_options=decoded_options)
    else:
        error=str(response)+" error, data not found"
        return error


# code for checking results and storing new scores 
@app.route('/result', methods=['GET','POST'])
def result():
    if response=="200":
        data=req.json()["results"]
        correct_answer=0
        selected_options=[]
        if str(req.status_code)=="200": 

            # pprogram for counting the correct no. of questions
            for i in range(0,len(data)):
                select=str("option"+str(i)) # name of the input tag
                selected_options.append(select) 
                selection=request.form.get(selected_options[i]) # getting the selected value

                # counting correct answers and decoding correct answers for accuracy
                if selection==html.unescape(data[i]["correct_answer"]):
                    correct_answer=correct_answer+1
            correctAnswers=str(correct_answer)
            username=session.get('username')
            url=session.get('url')
            # storing scores according to the links of quizzes
            if url=="https://opentdb.com/api.php?amount=50&category=9&type=multiple":
                cursor.execute("UPDATE user_score SET gk=%s WHERE user_name=%s", (correctAnswers,username))
                db.commit()
                    
            elif url=="https://opentdb.com/api.php?amount=50&category=21&type=multiple":
                cursor.execute("UPDATE user_score SET sports=%s WHERE user_name=%s", (correctAnswers,username))
                db.commit()

            elif url=="https://opentdb.com/api.php?amount=50&category=18&type=multiple":
                cursor.execute("UPDATE user_score SET computer=%s WHERE user_name=%s", (correctAnswers,username))
                db.commit()
                    
            elif url=="https://opentdb.com/api.php?amount=50&category=17&type=multiple":
                cursor.execute("UPDATE user_score SET science=%s WHERE user_name=%s", (correctAnswers,username))
                db.commit()
                    
            elif url=="https://opentdb.com/api.php?amount=50&category=23&type=multiple":
                cursor.execute("UPDATE user_score SET history=%s WHERE user_name=%s", (correctAnswers,username))
                db.commit()
        return render_template("result.html", correctAnswers=correctAnswers, length=length)
        

# code for checking correct answers
@app.route('/correct', methods=['GET','POST'])
def api():
    if str(req.status_code)=="200": 
        c_ans=[]
        for ans in correct:
                edited=html.unescape(ans)
                c_ans.append(edited)
        
    return render_template("correct.html", c_ans=c_ans, decoded_question=decoded_question, length=length)

if __name__=="__main__":
    app.run(debug=True)
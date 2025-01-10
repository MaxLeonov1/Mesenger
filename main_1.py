import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_session import Session
from cachelib import FileSystemCache
from datetime import timedelta
from wierd_functions import *


con = sqlite3.connect("users_info.db", check_same_thread=False)
cursor = con.cursor()
app = Flask(__name__)
app.secret_key = '1111'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)

@app.route("/login/")
def login():
    return render_template('login.html')

@app.route("/authorization/",methods=['POST','GET'])
def authorization():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT username, password FROM users_info WHERE username=(?) and password=(?)",(login,password))
        info_check = cursor.fetchall()
        if len(info_check)>0:
            flash('Вы авторизованы', 'succsess')
            session['login'] = True
            session['username'] = login
            session.permanent = False
            app.permanent_session_lifetime = timedelta(minutes=1000)
            session.modified = True
            return redirect(url_for('view_all_posts'))
        else:
            flash('Неверный логин или пароль', 'danger')
            return redirect(url_for('login'))
    return redirect(url_for('view_all_posts'))

@app.route("/register/")
def register():

    return render_template('register.html')


@app.route("/save_register/", methods=['POST','GET'])
def save_register():
    cursor.execute("SELECT * FROM users_info")
    check_data = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        patronymic = request.form['patronymic']
        gender = request.form['gender']
        email_ = request.form['email']
        login = request.form['username']
        password = request.form['password']
        for user in check_data:
            print(user)
            if user[5] == email_:
                flash("такой параметр email уже существует","danger")
                return redirect(url_for('register'))
            if user[6] == login:
                flash("такой параметр login уже существует","danger")
                return redirect(url_for('register'))
            if user[7] == password:
                flash("такой параметр password уже существует","danger")
                return redirect(url_for('register'))

        cursor.execute("INSERT INTO users_info (last_name, name, patronymic, gender, email, username, password) VALUES (?,?,?,?,?,?,?)",
                       (last_name,name,patronymic,gender,email_,login,password))
        con.commit()
        return redirect(url_for('view_all_posts'))

@app.route("/add/")
def add_file():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('login'))
    return render_template('add.html')

@app.route("/upload/", methods=['POST'])
def save_post():
    image = request.files.get('image')
    title = request.form['title']
    description = request.form['description']
    cursor.execute("SELECT id FROM users_info WHERE username=(?)",
                   (session['username'],))
    user_id = cursor.fetchall()
    cursor.execute("INSERT INTO posts_info (title, file_name, description, user_id) VALUES (?,?,?,?)",
                   (title,image.filename,description,user_id[0][0]))
    con.commit()
    image.save(f'static/upload/{image.filename}')
    return redirect(url_for('view_all_posts'))

@app.route("/")
def view_all_posts():
    cursor.execute(" SELECT * FROM posts_info")
    posts_data = cursor.fetchall()
    return render_template('index.html', posts=posts_data)

########ОБРАБОТЧИК ПРОФИЛЯ

@app.route("/user_profile/")
def profile():
    return render_template('profile.html')

@app.route("/user_profile_change/")
def profile_change():
    return render_template('profile_change.html')

@app.route("/save_user_profile/", methods=["POST"])
def profile_save():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('login'))
    profile_image = request.files.get('profile-photo')
    info_about = request.form['about']
    cursor.execute("SELECT id FROM users_info WHERE username=(?)",
                   (session['username'],))
    user_id = cursor.fetchall()
    cursor.execute("INSERT INTO user_info (info_about,profile_image) VALUES (?,?) WHERE id=(?)",
                   (info_about,profile_image.filename,user_id[0][0]))
    con.commit()
    profile_image.save(f'static/user_profile_photo/{profile_image.filename}')
    return redirect(url_for('profile'))



@app.route("/logout/")
def logout():
    session.clear()
    flash('Вы вышли из профиля','danger')
    return redirect(url_for('view_all_posts'))

@app.route("/find_posts/<int:id>")
def post_search(id):
    cursor.execute(" SELECT * FROM posts_info WHERE user_id=(?)",(id,))
    posts_data = cursor.fetchall()
    print(posts_data)
    return render_template('index.html', posts=posts_data)

app.run(debug=True)

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "123456"
bootstrap = Bootstrap(app)


def buildingDB():
    conn = sqlite3.connect('db/users.db')
    cur = conn.cursor()
    cur.execute("""
        create table users (
            username varchar(100) NOT NULL,
            password varchar(100) NOT NULL,
            email varchar(100) NOT NULL
        );
        """)
    cur.close()


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if username  and password and email :

            with sqlite3.connect("db/users.db") as conn:
                c = conn.cursor()
                c.execute("""INSERT INTO users(username,password,email) VALUES (:username,:password,:email)""",
                      {"username":username,"password":password,"email":email})
                conn.commit()
            
        return render_template('register.html')


if __name__ == '__main__':
    if not os.path.exists('db/users.db'):
        buildingDB() #建数据库
    app.run(host='0.0.0.0',debug=True, port=8080,threaded=True,processes=1)
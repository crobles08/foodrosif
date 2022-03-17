from flask import Flask, flash, render_template, request, redirect, url_for, session
#render_template=>es para ver lo de las plantillas y esta busca siempre la carpeta template
import mysql.connector
import re

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port=3306,
    database="foodrosif"
)
db.autocommit = True

app=Flask(__name__)

app.secret_key = '##91!IyAj#FqkZ2C'

@app.get("/")
def inicio():
    
    return render_template("index.html")





#=======================================================================================================================================

@app.route('/login/', methods=['GET', 'POST'])
def login():

    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s', (username, password,))
        

        usuario = cursor.fetchone()
        cursor.close()

        if usuario:

            session['login'] = True
            session['id_usuario'] = usuario[0] 
            session['usuario'] = (usuario[1] or usuario[3])

            return 'Logged in successfully!'
        else:
            
            msg = 'Incorrect username/password!'
            

    return render_template('index.html', msg=msg)

#================================================================================================================================

@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = db.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', (username,))
        account = cursor.fetchone()
        cursor.close()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO usuarios VALUES (NULL, %s, %s, %s, NULL)', (username, password, email,))
            
            msg = 'You have successfully registered!'

    elif request.method == 'POST':

        msg = 'Please fill out the form!'

    return render_template('Registo-cuenta.html', msg=msg)

#================================================================================================================================

@app.route('/login/logout')
def logout():
   session.pop('login', None)
   session.pop('id_usuario', None)
   session.pop('usuario', None)
   return redirect(url_for('login'))

app.run(debug=True)
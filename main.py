from flask import Flask, flash, render_template, request, redirect, url_for, session
import mysql.connector
import re
from hashlib import sha256
from email.message import EmailMessage
from smtplib import SMTP

db = mysql.connector.connect(
    host="localhost", user="root", password="", port=3306, database="foodrosif"
)
db.autocommit = True

app = Flask(__name__)

app.secret_key = "##91!IyAj#FqkZ2C"


@app.get("/")
def inicio():

    return render_template("index.html")


# =======================================================================================================================================


@app.route("/login", methods=["GET", "POST"])
def login():
    if (
        request.method == "POST"
        and "usuario" in request.form
        and "contraseña" in request.form
    ):

        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        contraseña=sha256(contraseña.encode("utf-8")).hexdigest()

        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s", (usuario, contraseña,),)

        cuenta = cursor.fetchone()
        cursor.close()

        if cuenta:

            session["login"] = True
            session["id_usuario"] = cuenta[0]
            session["usuario"] = cuenta[1]

            return "¡Has iniciado sesión con éxito!"
        else:

            flash("¡Nombre de usuario/contraseña incorrectos!")

    return render_template("inicio_sesion.html")


# ================================================================================================================================


@app.route("/register", methods=["GET", "POST"])
def register():
    if (
        request.method == "POST"
        and "usuario" in request.form
        and "contraseña" in request.form
        and "email" in request.form
    ):

        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        contraseña=sha256(contraseña.encode("utf-8")).hexdigest()
        email = request.form["email"]

        msg= EmailMessage()
        msg.set_content('Te haz registrado exitosamente <a href="http://localhost:5000/register">verifica aquí</a>')

        msg['Subject']='Registro en Foodrosif'
        msg['From']='shaydruano2020@itp.edu.co'
        msg['To']= email

        username = 'shaydruano2020@itp.edu.co'
        password = '100666' #==================================================================

        server = SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)

        server.send_message(msg)
        server.quit()


        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        cuenta = cursor.fetchone()
        

        if cuenta:
            flash("¡La cuenta ya existe!")
            
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("¡Dirección de correo electrónico no válida!")
           
        elif not re.match(r"[A-Za-z0-9]+", usuario):
            flash("¡El usuario debe contener solo caracteres y números!")
            
        elif not usuario or not contraseña or not email:
            flash("¡Por favor llene el formulario!")
            
        else:
            cursor.execute(
                "INSERT INTO usuarios VALUES (NULL, %s, %s, %s, NULL)",
                (
                    usuario,
                    contraseña,
                    email,
                ),
            )
            cursor.close()
            flash("¡Te has registrado con éxito!")
            

    elif request.method == "POST":

        flash("¡Por favor llene el formulario!")

    return render_template("Registo-cuenta.html")


# ================================================================================================================================


@app.route("/login/cerrar_Sesion")
def cerrarSesion():
    session.pop("login", None)
    session.pop("id_usuario", None)
    session.pop("usuario", None)
    return redirect(url_for("login"))


app.run(debug=True)

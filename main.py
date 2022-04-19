
from flask import Flask, flash, render_template, request, redirect, url_for, session
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
import mysql.connector
import re
from hashlib import sha256
from email.message import EmailMessage
from smtplib import SMTP
from flask_mail import Mail, Message

db = mysql.connector.connect(
    host="localhost", user="root", password="", port=3306, database="foodrosif"
)
db.autocommit = True

app = Flask(__name__)
#app.config.from_pyfile('config.cfg')
app.secret_key = "##91!IyAj#FqkZ2C"
mail=Mail(app)
s=URLSafeTimedSerializer('Thisisasecret')

@app.get("/")
def inicio():
    return render_template("index.html")


# =======================================================================================================================================


@app.route("/login", methods=["GET", "POST"])
def login():
    if (
        request.method == "POST"
        and "email" in request.form
        and "password" in request.form
    ):

        email = request.form["email"]
        password = request.form["password"]
        passwordencriptada = sha256(password.encode("utf-8")).hexdigest()

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s AND contraseña = %s AND confirmacion='1'",
            (
                email,
                passwordencriptada,
            ),
        )

        cuenta = cursor.fetchone()
        cursor.close()

        if cuenta:
            session["login"] = True
            session["id_usuario"] = cuenta["id_usuario"]
            session["email"] = cuenta["email"]
            return "¡Has iniciado sesión con éxito!"
        else:
            flash("¡Nombre de usuario/contraseña incorrectos!")
            return render_template(
                "inicioSesion.html",
                email=email,
                password=password,
            )    
            

    return render_template("inicioSesion.html")


# ===============================================================================================================================


# ================================================================================================================================


@app.route("/registerEmpresa", methods=["GET", "POST"])
def registerEmpresa():
    print("aa")
    if (
        request.method == "POST"
        and "nombre" in request.form
        and "descripcion" in request.form
        and "imagen" in request.files
        and "celular" in request.form
        and "direccion" in request.form
        and "email" in request.form
        and "password" in request.form
    ):

        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        print("0")
        imagen = request.files['imagen']
        print("1 "+nombre+" "+str(imagen))
        celular = request.form.get("celular")
        direccion = request.form.get("direccion")
        email = request.form.get("email")
        password = request.form.get("password")

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM empresas WHERE email = %s", (email,))
        cuenta = cursor.fetchone()
        print("2")
        token=s.dumps(email, salt='email-confirm')
        link= url_for('confirmarEmail', token=token, _external=True)
        caracterspecial = ["$", "@", "#", "%"]
        is_valid = True

        if cuenta:
            flash("Ya hay una empresa registrada con este correo!")
            is_valid = False

        if nombre == "":
            flash("El nombre es requerido")
            is_valid = False

        if descripcion == "":
            flash("La descripcion es requerida")
            is_valid = False

        if not (len(celular) == 10):
            flash("Ingresar bien el número de celular!")
            is_valid = False

        if direccion == "":
            flash("La direccion es requerida")
            is_valid = False

        if not (len(password) >= 8 and len(password) <= 20):
            flash("La contraseña debe tener min 8 y max 20 caracteres")
            is_valid = False

        if not any(char.isdigit() for char in password):
            flash("La contraseña debe tener al menos un número")
            is_valid = False

        if not any(char.isupper() for char in password):
            flash("La contraseña debe tener al menos una letra mayúscula")
            is_valid = False

        if not any(char.islower() for char in password):
            flash("La contraseña debe tener al menos una letra minúscula")
            is_valid = False

        if not any(char in caracterspecial for char in password):
            flash("La contraseña debe tener al menos uno de los símbolos $,@,%,#")
            is_valid = False

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("¡Dirección de correo electrónico no válida!")
            is_valid = False
        print("3")
        if (
            not nombre
            or not descripcion
            or not imagen
            or not celular
            or not direccion
            or not email
            or not password
        ):
            flash("¡Por favor llene el formulario!")
            print("4")
            is_valid = False
            # if is_valid:
            #   return is_valid

        if is_valid == False:
            print("5")
            return render_template(
                "registroEmpresa.html",
                nombre=nombre,
                descripcion=descripcion,
                imagen=imagen,
                celular=celular,
                direccion=direccion,
                email=email,
                password=password,
            )            
        print("6")
        nombre_imagen = imagen.filename
        imagen.save('./static/imagen'+ nombre_imagen)
        imagen='/static/imagen' + nombre_imagen
        
        password = sha256(password.encode("utf-8")).hexdigest()
        cursor.execute(
            "INSERT INTO empresas(nombre, descripcion, imagen, celular, direccion) VALUES (%s, %s, %s, %s, %s)",
            (
                nombre,
                descripcion,
                imagen,
                celular,
                direccion,
            ),
        )
        print("7")
        cursor.execute("SELECT * FROM empresas ORDER BY id_empresa DESC LIMIT 1 " )
        row=cursor.fetchone()
        if row is not None:
            row = row["id_empresa"]
        print(row)
        cursor.execute(
            "INSERT INTO usuarios(email, contraseña, id_empresa) VALUES (%s, %s, %s)",
            (
                email,
                password,
                row,
            ),
        )
        print("8")
        #cursor.commit()
        cursor.close()
        msg = EmailMessage()
        msg.set_content("Confirmar tu correo aqui: {} ".format(link))
        msg["Subject"] = "Registro en Foodrosif"
        msg["From"] = "shaydruano2020@itp.edu.co"
        msg["To"] = email
        username = "shaydruano2020@itp.edu.co"
        password = "1006663258"  # ==================================================================
        server = SMTP("smtp.gmail.com:587")
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        flash("¡Te has registrado con éxito!")

    elif request.method == "POST":

        flash("¡Por favor llene el formulario!")

    return render_template("registroEmpresa.html")


# ===========================================================================================================================================
@app.route("/login/confirmarEmail/<token>")
def confirmarEmail(token):
    try:
        email=s.loads(token, salt='email-confirm', max_age=60)
        cursor = db.cursor()
        cursor.execute("UPDATE usuarios SET confirmacion='1' WHERE email='"+email+"'")
        cursor.close()
    except SignatureExpired:
        cursor = db.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email='"+email+"' AND confirmacion='0'")
        cursor.close()
        return "<h1>paila nea</h1>"
    return "<h1>"+email+" R nea</h1>"
# ===========================================================================================================================================
@app.get("/login/cerrar_Sesion")
def cerrarSesion():
    """session.pop("login", None)
    session.pop("id_usuario", None)
    session.pop("email", None)"""
    session.clear()


    return redirect(url_for("login"))


app.run(debug=True)

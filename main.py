#from crypt import methods
from config.database import db
from flask import Flask, flash, render_template, request, redirect, url_for, session
import re
from hashlib import sha256
from models import userModel
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = "##91!IyAj#FqkZ2C"

s=URLSafeTimedSerializer('Thisisasecret')

@app.get("/")
def inicio():
    return render_template("index.html")

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
            return redirect(url_for("muro"))
        else:
            flash("¡Nombre de usuario/contraseña incorrectos!")
            return render_template(
                "inicioSesion.html",
                email=email,
                password=password,
            )    
    return render_template("inicioSesion.html")

@app.route("/login/muro", methods=["GET", "POST"])
def  muro():
    id_sesion=session['id_usuario']
    productos=userModel.listarProductos(id_sesion=id_sesion)
    return render_template("muro.html", productos=productos)

@app.route("/registerEmpresa", methods=["GET", "POST"])
def registerEmpresa():
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
        imagen = request.files['imagen']
        celular = request.form.get("celular")
        direccion = request.form.get("direccion")
        email = request.form.get("email")
        password = request.form.get("password")

        cuenta = userModel.correoExistente(email)
        
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
        token=s.dumps(email, salt='email-confirm')
        link= url_for('confirmarEmail', token=token, _external=True)  

        imagen = userModel.nombreImagen(imagen)

        password = sha256(password.encode("utf-8")).hexdigest()

        userModel.resgistrarEmpresa(nombre=nombre, descripcion=descripcion, imagen=imagen, celular=celular, direccion=direccion, email=email, password=password)    
        
        userModel.correoVerificacion(email=email, link=link)
        flash("¡Te has registrado con éxito!")

    elif request.method == "POST":

        flash("¡Por favor llene el formulario!")

    return render_template("registroEmpresa.html")

@app.route("/login/confirmarEmail/<token>")
def confirmarEmail(token):
    try:
        email=s.loads(token, salt='email-confirm', max_age=60)
        cursor = db.cursor()
        cursor.execute("UPDATE usuarios SET confirmacion='1' WHERE email='"+email+"'")
        cursor.close()
    except SignatureExpired:
        """cursor = db.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email='"+email+"' AND confirmacion='0'")
        cursor.close()"""
        return "<h1>paila nea</h1>"
    return "<h1>"+email+" R nea</h1>"

@app.get("/login/cerrar_Sesion")
def cerrarSesion():
    """session.pop("login", None)
    session.pop("id_usuario", None)
    session.pop("email", None)"""
    session.clear()
    return redirect(url_for("login"))

@app.route("/restablecerPassword", methods=["GET", "POST"])
def restablecerPassword():
    if (
        request.method == "POST"
        and "email" in request.form
    ):
        email = request.form.get("email")
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s AND confirmacion='1'",
            (
                email,
            ),
        )
        cuenta = cursor.fetchone()
        cursor.close()
        print("uno")
        if not(cuenta):
            flash('¡Esta cuenta no existe!')
            return render_template('Index.html')

        token_password=s.dumps(email, salt='restablecer-password')
        link_password= url_for('cambiarPassword_a', token_password=token_password, _external=True)  

        userModel.correoRestablecerPassword(email=email, link_password=link_password)
        flash("Revisar el correo")

    return render_template("correoRestablecerContraseña.html")
        
@app.route("/restablecerPassword_a/<token_password>")
def cambiarPassword_a(token_password):
    try:
        email=s.loads(token_password, salt='restablecer-password', max_age=60)
    except SignatureExpired:
        return render_template("correoRestablecerContraseña.html")
    return redirect(url_for('cambiarContra', email=email, _external=True))

@app.route("/restablecerPass/<email>", methods=["GET", "POST"])
def cambiarContra(email):
    if request.method == "GET":
        return render_template("restablecerPassword.html")
    else:   
        password = request.form.get("password")
        password_verificacion= request.form.get("password_verificacion")
        if password==password_verificacion:
                caracterspecial = ["$", "@", "#", "%"]
                is_valid = True
                print(password)
                print(len(password))
                if not (int(len(password)) >= 8 and int(len(password)) <= 20):
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

                if is_valid == False:
                    return render_template(
                        "restablecerPassword.html",
                        password=password,
                        password_verificacion=password_verificacion,
                    )   

                passwordencriptada = sha256(password.encode("utf-8")).hexdigest()
                userModel.cambioPassword(email=email, passwordencriptada=passwordencriptada)
                flash("Contraseña corregida")
                return render_template("inicioSesion.html")
        else:
            flash("Comprobar de que las contraseñas sean iguales!")
            return render_template(
                    "restablecerPassword.html",
                    password=password,
                    password_verificacion=password_verificacion,
            )




@app.route('/login/muro/crearProducto', methods=['GET', 'POST'])
def crearProducto():
    if request.method == 'GET':
        return render_template('muro.html')
    id_sesion= session['id_usuario']
    imagen = request.files['imagen']
    descripcion= request.form['descripcion'].upper()
    precio = request.form['precio']
    estado= request.form['estado']
     
    img = userModel.nombreImagen(imagen)
    userModel.crearProducto(id_sesion=id_sesion, descripcion=descripcion, precio=precio,imagen=img, estado=estado)
    

    imagen.save('./static/imagenesProductos/'+str(img))
    flash('Se ha creado el producto correctamente', 'success')
    return redirect(url_for('muro'))

@app.route('/login/muro/editarProducto/<string:id>', methods=['GET','POST'])
def editarProducto(id):
    if request.method == "GET":
        return render_template("editarProducto.html")
    else:
        descripcion= request.form['descripcion'].upper()
        precio = request.form['precio']
        imagen = request.files['imagen']
        estado = request.form['estado'] 
        if imagen:
                nombreImagen = userModel.nombreImagen(imagen)
                imagenn=nombreImagen
                imagen.save('./static/imagenesProductos/'+nombreImagen)
        else:
            imagenn = None  
        userModel.editarProducto(descripcion=descripcion, precio=precio, imagenn=imagenn, id=id, estado=estado)
        flash('Se ha editado el producto correctamente')  
        return redirect(url_for('muro'))

@app.route('/login/muro/eliminar_producto/<string:id>')
def eliminarProducto(id):
    userModel.eliminarProducto(id)
    return redirect(url_for('muro'))

        

app.run(debug=True)

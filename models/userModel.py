from config.database import db
from datetime import date, datetime
from config import settings
from email.message import EmailMessage
from smtplib import SMTP

from flask import url_for

def correoExistente(email):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    cuenta = cursor.fetchone()
    cursor.close()
    return cuenta

def resgistrarEmpresa(nombre, descripcion, imagen, celular, direccion, email, password):
    cursor = db.cursor(dictionary=True)
    print(nombre)
    cursor.execute("INSERT INTO empresas (nombre, descripcion, imagen, celular, direccion) VALUES (%s, %s, %s, %s, %s)", (
        nombre,
        descripcion,
        imagen,
        celular,
        direccion,
    ))
    cursor.execute("SELECT * FROM empresas ORDER BY id_empresa DESC LIMIT 1 " )
    row=cursor.fetchone()
    if row is not None:
        row = row["id_empresa"]
    cursor.execute("INSERT INTO usuarios(email, contraseña, id_empresa) VALUES (%s, %s, %s)",
        (
            email,
            password,
            row,
        ),
    )       
    cursor.close()

def nombreImagen(imagen):
    today = date.today()
    now = datetime.now()
    fecha= str(today)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
    nombreImagen = imagen.filename
    return str(fecha) + nombreImagen

def correoVerificacion(email, link):
    msg = EmailMessage()
    msg.set_content("Confirmar tu correo aqui: {} ".format(link))
    msg["Subject"] = "Registro en Foodrosif"
    msg["From"] = "shaydruano2020@itp.edu.co"
    msg["To"] = email
    username = "shaydruano2020@itp.edu.co"
    password = "1006663258"  
    server = SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()

def correoRestablecerPassword(email, link_password):
    msg = EmailMessage()
    msg.set_content("Para restablecer tu contraseña ingresa al siguiente link (Tiempo limite 2 min) : {} ".format(link_password))
    msg["Subject"] = "Recuperar contraseña"
    msg["From"] = "shaydruano2020@itp.edu.co"
    msg["To"] = email
    username = "shaydruano2020@itp.edu.co"
    password = "1006663258"  
    server = SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()

def cambioPassword(email, passwordencriptada):
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE usuarios SET contraseña=%s WHERE email=%s",
    (
        passwordencriptada,
        email,
    ))
    cursor.close()

def listarProductos():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    return productos

def crearProducto(id_sesion, descripcion, precio,imagen, estado):
    cursor = db.cursor()
    cursor.execute("SELECT id_empresa FROM usuarios WHERE id_usuario=%s",(id_sesion,))
    id_empresa= cursor.fetchone()
    cursor.execute("""insert into productos(
                imagen,
                descripcion,
                precio,
                id_empresa,
                id_estado,
                id_usuario
            )values (%s, %s, %s, %s, %s, %s)
        """, (imagen, descripcion, precio, id_empresa[0], estado, id_sesion,))
    db.commit()

def eliminarProducto(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
    db.commit()

def editarProducto(id, descripcion, precio, imagenn, estado):
    imagen_sql=''
    if imagenn:
        imagen_sql=", imagen= '"+imagenn+"'"
        sql = " descripcion= '"+descripcion+"', precio = '"+precio+"'" + imagen_sql + ", id_estado="+estado+" WHERE id_producto = '"+id+"'"
    elif imagenn is None:
        sql = " descripcion= '"+descripcion+"', precio = '"+precio+"'" + imagen_sql + ", id_estado="+estado+" WHERE id_producto = '"+id+"'"
    cursor = db.cursor()    
    cursor.execute("UPDATE productos SET " + sql)
    db.commit()



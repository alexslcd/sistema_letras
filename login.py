from flask import Blueprint, render_template, request, session, redirect, url_for
from conexion import obtener_conexion_cursor 
login_bp = Blueprint('login', __name__)


def credenciales_validas(username, password, connection):
    try:
        with connection.cursor() as cursor:
           
            query = "SELECT COUNT(*) FROM usuario WHERE user = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
           
            return result[0] == 1
    except Exception as e:
        print(f"Error al verificar las credenciales: {e}")
        return False


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
     
        connection, cursor = obtener_conexion_cursor()
        try:
            if credenciales_validas(username, password, connection):
            
                session['logged_in'] = True
                return redirect(url_for('index'))  # Redirigir al usuario después del inicio de sesión exitoso
            else:
                error = "Credenciales inválidas. Por favor, inténtalo de nuevo."
                return render_template('login.html', error=error)
        finally:
           
            cursor.close()
            connection.close()
    return render_template('login.html')

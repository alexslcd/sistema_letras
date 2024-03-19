from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager
import pymysql
import xlsxwriter              #descarga excel
from flask import send_file    #descarga excel
app = Flask(__name__)
from conexion import obtener_conexion_cursor
from login import login_bp
app = Flask(__name__)
app.secret_key = '@lexito'

app.register_blueprint(login_bp)


@app.route('/index')
def index():
    
    if not session.get('logged_in'):
        print("Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for('login.login'))  
   
    print("Usuario autenticado. Mostrando página principal.")
    return render_template('index.html')


@app.route('/')
def home():
    return redirect(url_for('login.login'))

@app.route('/logout', methods=['POST'])
def logout():
 
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

# Ruta para guardar la fecha en la base de datos

@app.route('/guardar_fecha_eronald', methods=['POST'])
def guardar_fecha_eronald():
    # Obtener la fecha de entrega de la solicitud
    fecha_eronald = request.json.get('fechaEronald')
    numero_letra = request.json.get('numeroLetra')  # Obtener el número de la letra seleccionada

    try:
        # Conectar a la base de datos y ejecutar la consulta para actualizar la fecha_Eronald
        db, cursor = obtener_conexion_cursor()
        query = "UPDATE letras SET fecha_Eronald = %s WHERE numero_boleta = %s"
        cursor.execute(query, (fecha_eronald, numero_letra))
        db.commit()
        
        # Devolver una respuesta al cliente
        response = {'message': 'La fecha de entrega a notificador se guardó correctamente en la base de datos.'}
        return jsonify(response), 200

    except Exception as e:
        # En caso de error, devolver un mensaje de error
        print(f"Error: {e}")
        response = {'message': 'Error al guardar la fecha en la base de datos.'}
        return jsonify(response), 500

    finally:
        # Cerrar la conexión a la base de datos
        db.close()


@app.route('/guardar_fechas_notificador', methods=['POST'])
def guardar_fechas_notificador():
    # Obtener las fechas del formulario del notificador
    fecha_Rcliente = request.json.get('fechaRcliente')
    fecha_Acliente = request.json.get('fechaAcliente')
    numero_letra = request.json.get('numeroLetra')

    try:
        # Aquí debes agregar la lógica para conectarte a la base de datos y ejecutar la consulta SQL
        db, cursor = obtener_conexion_cursor()  # Suponiendo que esta función establece la conexión y devuelve el cursor

        # Actualizar las fechas en la base de datos
        query = "UPDATE letras SET fecha_Rcliente = %s, fecha_Acliente = %s WHERE numero_boleta = %s"
        cursor.execute(query, (fecha_Rcliente, fecha_Acliente, numero_letra))
        db.commit()

        # Ejemplo de respuesta exitosa
        response = {'message': 'Las fechas se guardaron correctamente en la base de datos.'}
        return jsonify(response), 200

    except Exception as e:
        # En caso de error, devolver un mensaje de error
        print(f"Error: {e}")
        response = {'message': 'Error al guardar las fechas en la base de datos.'}
        return jsonify(response), 500

    finally:
        # Cerrar la conexión a la base de datos
        db.close()


# Ruta para guardar el estado y el banco de la letra
@app.route('/guardar_estado_banco', methods=['POST'])
def guardar_estado_banco():
    # Obtener el estado y el banco seleccionados del formulario
    estado_letra = request.json.get('estadoLetra')
    banco_cobro = request.json.get('bancoCobro')
    numero_letra = request.json.get('numeroLetra')

    try:
        # Conectar a la base de datos y ejecutar la consulta para actualizar el estado y el banco
        db, cursor = obtener_conexion_cursor()
        query = "UPDATE letras SET estado = %s, banco = %s WHERE numero_boleta = %s"
        cursor.execute(query, (estado_letra, banco_cobro, numero_letra))
        db.commit()
        
        # Devolver una respuesta al cliente
        response = {'message': 'El estado y el banco se guardaron correctamente en la base de datos.'}
        return jsonify(response), 200

    except Exception as e:
        # En caso de error, devolver un mensaje de error
        print(f"Error: {e}")
        response = {'message': 'Error al guardar el estado y el banco en la base de datos.'}
        return jsonify(response), 500

    finally:
        # Cerrar la conexión a la base de datos
        db.close()




# Ruta para guardar la fecha en la base de datos


@app.route('/buscar_letras', methods=['POST'])
def buscar_letras():
    try:
       
        db, cursor = obtener_conexion_cursor()

        letra = request.form['numeroBoleta']
        ruc = request.form['ruc']
        razon_social = request.form['razonSocial']  # Nuevo campo
        fecha_desde = request.form['fechaDesde']
        fecha_hasta = request.form['fechaHasta']
        
        query = "SELECT numero_boleta, ref_giro, fecha_giro, fecha_vence, importe, cod_cliente, razon_social, moneda, tipo_producto, cliente_vendedor, id_usuario, estado, banco, fecha_Eronald, fecha_Rcliente, fecha_Acliente FROM letras WHERE "

        params = []

        
        if letra:
            query += "numero_boleta LIKE %s"
            params.append('%' + letra + '%')

        if ruc:
            if letra:
                 query += " OR "  
            query += "cod_cliente LIKE %s"
            params.append('%' + ruc + '%')

        if razon_social:
            if letra or ruc:
                 query += " OR "
            query += "razon_social LIKE %s"
            params.append('%' + razon_social + '%')

        if fecha_desde and fecha_hasta:
            if letra or ruc or razon_social:
              query += " AND "  
            query += "fecha_giro BETWEEN %s AND %s"
            params.extend([fecha_desde, fecha_hasta])
        else:
             query += " AND TRUE"

      
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()

        
        resultados_json = []
        for resultado in resultados:
            resultados_json.append({
                'numero_boleta': resultado[0],
                'ref_giro': resultado[1],
                'fecha_giro': str(resultado[2]),
                'fecha_vence': str(resultado[3]),
                'importe': resultado[4],
                'cod_cliente': resultado[5],
                'razon_social': resultado[6],
                'moneda': resultado[7],
                'tipo_producto': resultado[8],
                'cliente_vendedor': resultado[9],
                'id_usuario': resultado[10],
                'estado': resultado[11],
                'banco': resultado[12],
                'fecha_Eronald': str(resultado[13]),
                'fecha_Rcliente': str(resultado[14]),
                'fecha_Acliente': str(resultado[15])
            })

    except Exception as e:
        print(f"Error: {e}")
        resultados_json = []

    finally:
        
        db.close()

    return jsonify(resultados_json)




# Ruta para obtener los datos de la tabla "letras"
# Ruta para la nueva funcionalidad que selecciona todos los datos de la tabla "letra"



# Ruta para obtener los datos de la tabla "letras"
    

    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

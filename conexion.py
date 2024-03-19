
import pymysql

def obtener_conexion_cursor():
    nueva_db = pymysql.connect(host='127.0.0.1', user='alexito', password='salcedo1A', database='letras_db')
    nuevo_cursor = nueva_db.cursor()
    return nueva_db, nuevo_cursor

from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import sqlite3
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# 1. REQUISITO SQL: Crear base de datos y tabla (Se ejecuta al iniciar)
def inicializar_sql():
    conn = sqlite3.connect('calidad_aire.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lecturas (
            estacion TEXT, lat REAL, lng REAL, pm25 INTEGER, o3 INTEGER, temp INTEGER
        )
    ''')
    cursor.execute('DELETE FROM lecturas') # Limpiar datos anteriores
    
    # 15 estaciones con variaciones de calidad del aire para nutrir las gráficas
    datos = [
        ("Ecatepec Centro", 19.6097, -99.0600, 45, 110, 22),
        ("Las Américas", 19.5985, -99.0150, 25, 85, 24),
        ("Ciudad Azteca", 19.5400, -99.0280, 65, 125, 21),
        ("Xalostoc", 19.5273, -99.0880, 85, 135, 23),
        ("Coacalco", 19.6333, -99.0980, 35, 95, 20),
        ("Tlalnepantla", 19.5400, -99.1900, 55, 115, 22),
        ("San Agustín", 19.5300, -99.0400, 40, 100, 21),
        ("Gustavo A. Madero", 19.4827, -99.1102, 60, 130, 24),
        ("Lindavista", 19.4900, -99.1300, 30, 90, 23),
        ("Azcapotzalco", 19.4869, -99.1859, 75, 140, 22),
        ("Naucalpan", 19.4736, -99.2393, 42, 105, 21),
        ("Tecámac", 19.7128, -98.9692, 20, 80, 19),
        ("Texcoco", 19.5117, -98.8828, 15, 75, 20),
        ("Nezahualcóyotl", 19.4000, -99.0300, 90, 150, 25),
        ("Chimalhuacán", 19.4350, -98.9500, 80, 145, 24)
    ]
    cursor.executemany('INSERT INTO lecturas VALUES (?,?,?,?,?,?)', datos)
    conn.commit()
    conn.close()

# 2. REQUISITO NoSQL: Objeto de conexión a MongoDB (Local para evitar errores DNS)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/aire")
mongo_client = MongoClient(MONGO_URI)

@app.route('/api/datos')
def obtener_datos():
    # 3. REQUISITO ETL CON PANDAS: Extraer de SQL
    conn = sqlite3.connect('calidad_aire.db')
    df = pd.read_sql_query("SELECT * FROM lecturas", conn)
    conn.close()

    # Transformación: Calcular Índice de Calidad del Aire (KPI)
    df['ICA'] = df['pm25'] * 1.5 
    
    # Validar y agregar categoría
    df['categoria'] = df['ICA'].apply(lambda x: 'Mala' if x > 100 else ('Regular' if x > 50 else 'Buena'))
    
    # Exportar datos limpios como JSON
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    inicializar_sql()
    app.run(debug=True, host='0.0.0.0', port=5000)
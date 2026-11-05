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
    
    # Ingesta simulada de fuente pública
    datos = [
        ("Ecatepec Centro", 19.6097, -99.0600, 45, 110, 22),
        ("Las Américas", 19.5985, -99.0150, 25, 85, 24),
        ("Ciudad Azteca", 19.5400, -99.0280, 65, 125, 21)
    ]
    cursor.executemany('INSERT INTO lecturas VALUES (?,?,?,?,?,?)', datos)
    conn.commit()
    conn.close()

# 2. REQUISITO NoSQL: Objeto de conexión a MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:password@cluster0.mongodb.net/aire")
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
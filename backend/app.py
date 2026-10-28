from flask import Flask, jsonify
from flask_cors import CORS  # <-- NUEVA LÍNEA

app = Flask(__name__)
CORS(app)  # <-- NUEVA LÍNEA

@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    return jsonify({"mensaje": "¡Hola! El backend está funcionando perfectamente desde un contenedor Docker."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
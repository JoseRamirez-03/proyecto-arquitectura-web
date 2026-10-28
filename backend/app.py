from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Esto permite que nuestro frontend se comunique con este backend

@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    # Esta es la información que enviaremos a la página web
    informacion = {
        "mensaje": "¡Hola! El backend está funcionando perfectamente.",
        "tecnologia": "API REST con Flask"
    }
    return jsonify(informacion)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
from flask import Flask #me importa la libreria flask

app = Flask(__name__)

@app.route('/')         #se crea una ruta
def inicio(): #se crea una funcion
    return  #se retorna un mensaje

if __name__ == '__main__': #se ejecuta la aplicacion
    app.run(debug=True) #se ejecuta la aplicacion en modo debug
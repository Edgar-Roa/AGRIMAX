from flask import Flask, psycopg2 #me importa la libreria flask y psycopg2
from flask import render_template #me importa la libreria render_template

app = Flask(__name__)

@app.route('/')         #se crea una ruta
def inicio(): #se crea una funcion
    return  #se retorna un mensaje

if __name__ == '__main__': #se ejecuta la aplicacion
    app.run(debug=True) #se ejecuta la aplicacion en modo debug
    # source ven/Scripts/activate   para activar el entorno virtual
    # python app.py para ejecutar el archivo
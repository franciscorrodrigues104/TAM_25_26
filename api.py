from flask import Flask, request, jsonify
import psycopg2
import traceback
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app) #cors para o browser não bloquear a resposta


app.secret_key = os.getenv('SECRET_KEY')  
SECRET_KEY = os.getenv('SECRET_KEY')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


#Conexão bd
def conectar_bd():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Conexão com a base de dados bem-sucedida.")
        return conn
    except Exception as e:
        print(f"Erro na conexão com a base de dados: {e}")
        raise Exception(f"Erro ao conectar à base de dados: {e}")


@app.route('/alertas', methods=['GET'])
def get_alertas():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mensagem, timestamp
            FROM tam_25_26.alertas
            ORDER BY timestamp DESC
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        alertas = [
            {"mensagem": r[0], "timestamp": r[1].isoformat()} 
            for r in resultados
        ]

        return jsonify(alertas), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    
@app.route('/dados', methods=['GET'])
def get_dados():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT movimento, fumo
            FROM tam_25_26.acoes 
            WHERE movimento IS NOT NULL AND fumo IS NOT NULL
            ORDER BY data DESC
            LIMIT 10
        """)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        dados = [
            {"movimento": r[0], "fumo": r[1]} 
            for r in resultados
        ]

        return jsonify(dados), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

#endpoint ligar alarme
@app.route('/ligar_alarme', methods=['GET'])
def ligar_alarme():
    try:
    
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tam_25_26.acoes (evento, data)
            VALUES (%s, NOW())
        """, ("Alarme ligado",))

        conn.commit()
        cursor.close()
        conn.close()

        return "Alarme ligado com sucesso", 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


#endpoint para desligar o alarme
@app.route('/desligar_alarme', methods=['GET'])
def desligar_alarme():
    try:
        
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tam_25_26.acoes (evento, data)
            VALUES (%s, NOW())
        """, ("Alarme desligado",))

        conn.commit()
        cursor.close()
        conn.close()
      

        return "Alarme desligado com sucesso", 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

#endpiont para receber os dados do Arduino
@app.route('/receber_dados', methods=['POST'])
def receber_dados():
    try:
        dados = request.data.decode("utf-8")
        movimento_str, fumo_str = dados.split(",")
        movimento = int(movimento_str)
        fumo = int(fumo_str)

        if movimento is None or fumo is None:
            return jsonify({"erro": "Dados incompletos"}), 400

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tam_25_26.acoes (evento, data, movimento, fumo)
            VALUES (%s, NOW(), %s, %s)
        """, ("Dados recebidos com sucesso!", movimento, fumo))
        conn.commit()
        cursor.close()
        conn.close()


        return "Dados obtidos com sucesso!", 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500


@app.route('/estado_alarme', methods=['GET'])
def get_estado_alarme():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT estado 
            FROM tam_25_26.estado_alarme 
            WHERE id = 1
        """)

        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        if resultado:
            return resultado[0], 200
        else:
            return jsonify({"erro": "Estado não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    conectar_bd() #verificar logo se a conexão entre a bd está ok
    app.run(debug=True, host='0.0.0.0', port=5000)

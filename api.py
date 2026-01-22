from flask import Flask, jsonify, request
import logging, time, psycopg2, jwt, json
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS
import os


load_dotenv(".env.local")
app = Flask(__name__)


CORS(app)


NOT_FOUND_CODE = 400
OK_CODE = 200
SUCCESS_CODE = 201
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
NOT_FOUND = 404
SERVER_ERROR = 500



app.secret_key = os.getenv('SECRET_KEY')  
SECRET_KEY = os.getenv('SECRET_KEY')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

@app.route('/')
def home():
    return "API DE TAM, ESTÁ A FUNCIONAR"

@app.route('/add_quiz', methods=['POST'])
def add_quiz():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        campos_obrigatorios = ["titulo", "descricao", "duracao"]
        
        if not all(campo in data and data[campo] for campo in campos_obrigatorios):
            return jsonify({"Code": BAD_REQUEST_CODE, "Erro": "Parâmetros obrigatórios em falta"}), 400

        titulo = data["titulo"]
        descricao = data["descricao"]
        duracao = data["duracao"]

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.add_quiz(%s, %s, %s)",
            (titulo, descricao, duracao)
        )
        conn.commit()

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/add_questao', methods=['POST'])
def add_questao():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        
       
        campos_obrigatorios = ["pergunta", "numero_respostas", "resposta_correta", "respostas"]
        
        if not all(campo in data and data[campo] for campo in campos_obrigatorios):
            return jsonify({"Code": BAD_REQUEST_CODE, "Erro": "Parâmetros obrigatórios em falta"}), 400

        pergunta = data["pergunta"]
        num_respostas = data["numero_respostas"]
        respostas = data["respostas"]
        resposta_correta = data["resposta_correta"]
        url_imagem = data["url_imagem"]


        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.add_questao(%s, %s, %s, %s, %s, %s)",
            (pergunta, num_respostas, resposta_correta, None, url_imagem, respostas)
        )
        conn.commit() 

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/get_all_questions', methods=['GET'])
def get_all_questions():

    conn = None
    cursor = None
    try:
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tam.get_all_questions();"
        )

        rows = cursor.fetchall()

        questions = []
        for row in rows:
            questions.append({
                "id_questao": row[0],
                "pergunta": row[1],
                "numero_respostas": row[2],
                "respostas": row[3],         
                "resposta_correta": row[4],
                "id_quiz": row[5]
            })

        return jsonify({
            "Code": OK_CODE,
            "questions": questions
        })

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "Code": SERVER_ERROR,
            "Erro": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/delete_questao', methods=['POST'])
def delete_questao():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        
        id_questao = data["id_question"]
        
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.delete_questao(%s)",
            (id_questao,)
        )
        conn.commit()

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/atualiza_questao', methods=['POST'])
def atualiza_questao():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        
       
        id_questao = data["id_questao"]
        pergunta = data["pergunta"]
        num_respostas = data["numero_respostas"]
        respostas = data["respostas"]
        resposta_correta = data["resposta_correta"]
        url_imagem = data["url_imagem"]
        

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.update_questao(%s, %s, %s, %s, %s, %s)",
            (id_questao, pergunta, num_respostas, respostas, resposta_correta, url_imagem)
        )
        conn.commit() 

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/get_questao_by_id', methods=['POST'])
def get_questao_by_id():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        id_questao = data.get("id_questao")

       

        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tam.get_questao_by_id(%s)", (id_questao,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"Code": 404, "Erro": "Questão não encontrada"}), 404

        question = {
            "id_questao": row[0],
            "pergunta": row[1],
            "numero_respostas": row[2],
            "respostas": row[3], 
            "resposta_correta": row[4],
            "id_quiz": row[5],
            "url_imagem": row[6]
        }

        return jsonify({"Code": 200, "question": question})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": 500, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/get_all_quizzes', methods=['GET'])
def get_all_quizzes():

    conn = None
    cursor = None
    try:
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tam.get_all_queizzes();"
        )

        rows = cursor.fetchall()

        quizzes = []
        for row in rows:
            quizzes.append({
                "id_quiz": row[0],
                "titulo": row[1],
                "descricao": row[2],
            
            })

        return jsonify({
            "Code": OK_CODE,
            "quizzes": quizzes
        })

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "Code": SERVER_ERROR,
            "Erro": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/delete_quiz', methods=['POST'])
def delete_quiz():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        
        id_quiz = data["id_quiz"]
        
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.delete_quiz(%s)",
            (id_quiz,)
        )
        conn.commit()

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@app.route('/get_quiz_by_id', methods=['POST'])
def get_quiz_by_id():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        id_quiz = data.get("id_quiz")

       

        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tam.get_quiz_by_id(%s)", (id_quiz,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"Code": 404, "Erro": "Quiz não encontrada"}), 404

        quiz = {
            "id_quiz": row[0],
            "titulo": row[1],
            "descricao": row[2],
            "duracao": row[3], 
            
        }

        return jsonify({"Code": 200, "quiz": quiz})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": 500, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/atualiza_quiz', methods=['POST'])
def atualiza_quiz():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        
       
        id_quiz = data["id_quiz"]
        titulo = data["titulo"]
        descricao = data["descricao"]
        duracao = data["duracao"]
      
        

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.update_quiz(%s, %s, %s, %s)",
            (id_quiz, titulo, descricao, duracao)
        )
        conn.commit() 

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/associa_questao', methods=['POST'])
def associa_questao():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        
       
        id_quiz = data["id_quiz"]
        id_questao = data["id_questao"]
       
      
        

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * from tam.associa_questao(%s, %s)",
            (id_quiz, id_questao)
        )
        conn.commit() 

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/get_questoes_livres', methods=['GET'])
def get_questoes_livres():
    conn = None
    cursor = None
    try:
    

   

        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tam.get_questoes_livres()")
        rows = cursor.fetchall() 

        if not rows:
            return jsonify({"Code": 404, "Erro": "Quiz não encontrada"}), 404

        questions = []
        for row in rows:
            question = {
                "id_questao": row[0],
                "pergunta": row[1],
                "numero_respostas": row[2],
                "respostas": row[3] if row[3] else [],  # Se for array PostgreSQL
                "resposta_correta": row[4],
                "id_quiz": row[5]
            }
            questions.append(question)

        return jsonify({"Code": 200, "question": questions})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": 500, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/get_question_ids_by_quiz', methods=['POST'])
def get_question_ids_by_quiz():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        id_quiz = data.get("id_quiz")

       

        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tam.get_question_ids_by_quiz(%s)", (id_quiz,))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"Code": 404, "Erro": "Quiz não encontrada"}), 404

        questions = []
        for row in rows:
            question = {
            "id_questao": row[0],
            "pergunta": row[1],
            "numero_respostas": row[2],
            "respostas": row[3], 
            "resposta_correta": row[4],
            "id_quiz": row[5],
            "url_imagem": row[6],
            "duracao": row[7]
            }
            questions.append(question)

        return jsonify({"Code": 200, "question": questions})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": 500, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/dessasocia_questao', methods=['POST'])
def dessasocia_questao():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        id_questao = data.get("id_questao")
        
        if not id_questao:
            return jsonify({"Code": 400, "Erro": "id_questao é obrigatório"}), 400
        
        conn = db_connection()
        cursor = conn.cursor()
        
        
        cursor.execute("CALL tam.dessasocia_questao(%s)", (id_questao,))
        conn.commit()
        
        return jsonify({
            "Code": 200,
            "Mensagem": f"Questão {id_questao} desassociada com sucesso"
        })
   
    except Exception as error:
        if conn:
            conn.rollback()
        return jsonify({"Code": 500, "Erro": str(error)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/add_user', methods=['POST'])
def add_user():

    conn = None
    cursor = None
    try:
        
        data = request.get_json()
        campos_obrigatorios = ["username", "password"]
        
        if not all(campo in data and data[campo] for campo in campos_obrigatorios):
            return jsonify({"Code": BAD_REQUEST_CODE, "Erro": "Parâmetros obrigatórios em falta"}), 400

        username = data["username"]
        password = data["password"]

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "CALL tam.add_user(%s, %s)",
            (username, password)
        )
        conn.commit()

        return jsonify({"Code": OK_CODE})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/login', methods=['POST'])
def login():
    conn = None
    cursor = None

    try:
        data = request.get_json()
        campos_obrigatorios = ["username", "password"]

        if not all(campo in data and data[campo] for campo in campos_obrigatorios):
            return jsonify({"Code": 400, "Erro": "Parâmetros obrigatórios em falta"}), 400

        username = data["username"]
        password = data["password"]

        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("CALL tam.login(%s, %s)", (username, password))
        conn.commit()

        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.utcnow() + timedelta(minutes=5)},
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"Code": 200, "Message": "Login efetuado com sucesso", "token": token})

    except psycopg2.Error as e:
        if 'Login inválido' in str(e):
            return jsonify({"Code": 401, "Message": "Username ou password incorretos"}), 401
        else:
            return jsonify({"Code": 500, "Erro": f"Erro ao logar: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    old_token = data.get("token")

    if not old_token:
        return jsonify({"Code": 400, "Erro": "Token ausente"}), 400

    try:
        payload = jwt.decode(old_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        username = payload.get("username")

        new_token = jwt.encode(
            {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"Code": 200, "token": new_token})

    except jwt.InvalidTokenError:
        return jsonify({"Code": 401, "Erro": "Token inválido"}), 401



@app.route('/marcar_execucao', methods=['POST'])
def marcar_execucao():
    conn = None
    cursor = None

    try:
        data = request.get_json()
      
        id_quiz = data["id_quiz"]

        
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("CALL tam.marcar_execucao(%s)", (id_quiz,))
        conn.commit()

       

        return jsonify({"Code": 200, "Message": "Estado atualiza!"})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/desmarcar_execucao', methods=['POST'])
def desmarcar_execucao():
    conn = None
    cursor = None

    try:
        data = request.get_json()
      
        id_quiz = data["id_quiz"]

        
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("CALL tam.desmarcar_execucao(%s)", (id_quiz,))
        conn.commit()

       

        return jsonify({"Code": 200, "Message": "Estado atualiza!"})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": SERVER_ERROR, "Erro": str(error)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/get_estado_by_id', methods=['POST'])
def get_estado_by_id():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        id_quiz = data.get("id_quiz")

        if not id_quiz:
            return jsonify({"Code": 400, "Erro": "id_quiz é obrigatório"}), 400

        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT tam.verificar_execucao(%s)", (id_quiz,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({"Code": 404, "Erro": "Quiz não encontrada"}), 404

        return jsonify({"Code": 200, "execucao": row[0]})

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({"Code": 500, "Erro": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)




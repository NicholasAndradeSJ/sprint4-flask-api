import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


@app.route('/')
def index():
    return "<h1>API de Pontos de Interesse</h1><p>Bem-vindo!</p>"

@app.route('/AdicionarUsuario/', methods=['POST'])
def adicionar_usuario():
    email = request.form.get('email')
    nome = request.form.get('nome')

    if not email or not nome:
        return jsonify({'status': 'erro', 'mensagem': 'Email e nome são obrigatórios.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nome, email) VALUES (%s, %s)",
            (nome, email)
        )
        conn.commit()
        status = {'status': 'sucesso',
                  'mensagem': f'Usuário {nome} adicionado.'}
    except psycopg2.IntegrityError:
        conn.rollback()
        status = {'status': 'erro', 'mensagem': f'Email {email} já existe.'}
    except Exception as e:
        conn.rollback()
        status = {'status': 'erro', 'mensagem': str(e)}
    finally:
        cur.close()
        conn.close()

    return jsonify(status)


@app.route('/RemoverUsuario/', methods=['DELETE'])
def remover_usuario():
    email = request.form.get('email')
    if not email:
        return jsonify({'status': 'erro', 'mensagem': 'Email é obrigatório.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE email = %s", (email,))

    if cur.rowcount == 0:
        status = {'status': 'erro', 'mensagem': 'Usuário não encontrado.'}
    else:
        conn.commit()
        status = {'status': 'sucesso',
                  'mensagem': 'Usuário removido com sucesso.'}

    cur.close()
    conn.close()
    return jsonify(status)


@app.route('/ListarUsuarios/', methods=['GET'])
def listar_usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email FROM usuarios ORDER BY nome")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()

    lista_usuarios = []
    for usuario in usuarios:
        lista_usuarios.append({
            'id': usuario[0],
            'nome': usuario[1],
            'email': usuario[2]
        })

    return jsonify(lista_usuarios)


@app.route('/AtualizarUsuario/', methods=['PUT'])
def atualizar_usuario():
    email = request.form.get('email')
    novo_nome = request.form.get('novo_nome')

    if not email or not novo_nome:
        return jsonify({'status': 'erro', 'mensagem': 'Email e novo_nome são obrigatórios.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET nome = %s WHERE email = %s",
                (novo_nome, email))

    if cur.rowcount == 0:
        status = {'status': 'erro',
                  'mensagem': 'Usuário com este email não foi encontrado.'}
    else:
        conn.commit()
        status = {'status': 'sucesso',
                  'mensagem': f'Nome do usuário atualizado para {novo_nome}.'}

    cur.close()
    conn.close()
    return jsonify(status)

@app.route('/AdicionarPonto/', methods=['POST'])
def adicionar_ponto():
    try:
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        descricao = request.form.get('descricao')
        email_usuario = request.form.get('email')
    except (TypeError, ValueError):
        return jsonify({'status': 'erro', 'mensagem': 'Parâmetros latitude, longitude, descricao e email são obrigatórios e devem ser válidos.'}), 400

    if not all([latitude, longitude, descricao, email_usuario]):
        return jsonify({'status': 'erro', 'mensagem': 'Todos os parâmetros são obrigatórios: latitude, longitude, descricao, email.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM usuarios WHERE email = %s",
                    (email_usuario,))
        user_result = cur.fetchone()
        if not user_result:
            return jsonify({'status': 'erro', 'mensagem': 'Usuário não encontrado.'}), 404
        usuario_id = user_result[0]

        sql = """
            INSERT INTO pontos_interesse (descricao, geom, usuario_id)
            VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        """
        cur.execute(sql, (descricao, longitude, latitude, usuario_id))
        conn.commit()
        status = {'status': 'sucesso',
                  'mensagem': 'Ponto de interesse adicionado.'}

    except Exception as e:
        conn.rollback()
        status = {'status': 'erro', 'mensagem': str(e)}
    finally:
        cur.close()
        conn.close()

    return jsonify(status)


@app.route('/RemoverPonto/<int:ponto_id>', methods=['DELETE'])
def remover_ponto(ponto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM pontos_interesse WHERE id = %s", (ponto_id,))

    if cur.rowcount == 0:
        status = {'status': 'erro',
                  'mensagem': 'Ponto de interesse não encontrado.'}
    else:
        conn.commit()
        status = {'status': 'sucesso',
                  'mensagem': 'Ponto de interesse removido com sucesso.'}

    cur.close()
    conn.close()
    return jsonify(status)


@app.route('/ListarPontos/', methods=['GET'])
def listar_pontos():
    email_usuario = request.args.get('email')
    if not email_usuario:
        return jsonify({'status': 'erro', 'mensagem': 'Email do usuário é obrigatório.'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.descricao, ST_AsText(p.geom)
        FROM pontos_interesse p
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE u.email = %s
    """, (email_usuario,))

    pontos = cur.fetchall()
    cur.close()
    conn.close()

    lista_pontos = []
    for ponto in pontos:
        coords_text = ponto[2].replace('POINT(', '').replace(')', '')
        lon, lat = map(float, coords_text.split())
        lista_pontos.append({
            'id': ponto[0],
            'descricao': ponto[1],
            'latitude': lat,
            'longitude': lon
        })

    return jsonify(lista_pontos)

@app.route('/AtualizarPonto/<int:ponto_id>', methods=['PUT'])
def atualizar_ponto(ponto_id):
    nova_descricao = request.form.get('descricao')
    nova_latitude = request.form.get('latitude')
    nova_longitude = request.form.get('longitude')

    if not any([nova_descricao, nova_latitude, nova_longitude]):
        return jsonify({'status': 'erro', 'mensagem': 'Pelo menos um campo (descricao, latitude, longitude) deve ser fornecido para atualização.'}), 400

    update_fields = []
    params = []

    if nova_descricao:
        update_fields.append("descricao = %s")
        params.append(nova_descricao)

    if nova_latitude and nova_longitude:
        try:
            lat = float(nova_latitude)
            lon = float(nova_longitude)
            update_fields.append(
                "geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326)")
            params.extend([lon, lat])
        except (TypeError, ValueError):
            return jsonify({'status': 'erro', 'mensagem': 'Valores de latitude e longitude devem ser números válidos.'}), 400
    elif nova_latitude or nova_longitude:
        return jsonify({'status': 'erro', 'mensagem': 'Para atualizar a localização, ambos latitude e longitude devem ser fornecidos.'}), 400

    if not update_fields:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum dado válido fornecido para atualização.'}), 400

    params.append(ponto_id)

    sql = f"UPDATE pontos_interesse SET {', '.join(update_fields)} WHERE id = %s"

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, tuple(params))

        if cur.rowcount == 0:
            status = {'status': 'erro',
                      'mensagem': 'Ponto de interesse não encontrado.'}
        else:
            conn.commit()
            status = {'status': 'sucesso',
                      'mensagem': 'Ponto de interesse atualizado com sucesso.'}

    except Exception as e:
        conn.rollback()
        status = {'status': 'erro', 'mensagem': str(e)}
    finally:
        cur.close()
        conn.close()

    return jsonify(status)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

import pytest
from app import app, get_db_connection

@pytest.fixture
def client():
    """Cria um cliente de teste para a aplicação e limpa o banco de dados."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "TRUNCATE TABLE usuarios, pontos_interesse RESTART IDENTITY CASCADE")
                conn.commit()
        yield client

def test_adicionar_usuario_sucesso(client):
    """Testa a adição bem-sucedida de um novo usuário via POST."""
    response = client.post('/AdicionarUsuario/', data={
        'email': 'teste@exemplo.com',
        'nome': 'Usuario Teste'
    })
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'sucesso'


def test_adicionar_usuario_email_duplicado(client):
    """Testa a falha ao tentar adicionar um usuário com um email que já existe."""
    client.post('/AdicionarUsuario/',
                data={'email': 'duplicado@exemplo.com', 'nome': 'Usuario Um'})
    response = client.post(
        '/AdicionarUsuario/', data={'email': 'duplicado@exemplo.com', 'nome': 'Usuario Dois'})
    json_data = response.get_json()
    assert response.status_code == 200  # A rota em si retorna 200
    assert json_data['status'] == 'erro'
    assert 'já existe' in json_data['mensagem']


def test_listar_usuarios(client):
    """Testa se a listagem de usuários retorna os usuários cadastrados."""
    client.post('/AdicionarUsuario/',
                data={'email': 'user1@exemplo.com', 'nome': 'Usuario Um'})
    client.post('/AdicionarUsuario/',
                data={'email': 'user2@exemplo.com', 'nome': 'Usuario Dois'})

    response = client.get('/ListarUsuarios/')
    json_data = response.get_json()
    assert response.status_code == 200
    assert len(json_data) == 2
    assert json_data[0]['nome'] == 'Usuario Dois'
    assert json_data[1]['nome'] == 'Usuario Um'


def test_atualizar_usuario_sucesso(client):
    """Testa a atualização bem-sucedida do nome de um usuário."""
    client.post('/AdicionarUsuario/',
                data={'email': 'att@exemplo.com', 'nome': 'Nome Antigo'})

    response = client.put('/AtualizarUsuario/', data={
        'email': 'att@exemplo.com',
        'novo_nome': 'Nome Novo'
    })
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'sucesso'

    response_lista = client.get('/ListarUsuarios/')
    assert 'Nome Novo' in str(response_lista.data)
    assert 'Nome Antigo' not in str(response_lista.data)


def test_remover_usuario(client):
    """Testa a remoção de um usuário."""
    client.post('/AdicionarUsuario/',
                data={'email': 'remover@exemplo.com', 'nome': 'Para Remover'})
    response = client.delete(
        '/RemoverUsuario/', data={'email': 'remover@exemplo.com'})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'sucesso'

    response_lista = client.get('/ListarUsuarios/')
    assert 'remover@exemplo.com' not in str(response_lista.data)

def test_adicionar_ponto_sucesso(client):
    """Testa a adição bem-sucedida de um ponto de interesse."""
    client.post('/AdicionarUsuario/',
                data={'email': 'ponto_user@exemplo.com', 'nome': 'Usuario Ponto'})

    response = client.post('/AdicionarPonto/', data={
        'latitude': -20.5,
        'longitude': -40.5,
        'descricao': 'Praia',
        'email': 'ponto_user@exemplo.com'
    })
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'sucesso'


def test_adicionar_ponto_usuario_inexistente(client):
    """Testa a falha ao adicionar um ponto para um usuário que não existe."""
    response = client.post('/AdicionarPonto/', data={
        'latitude': -20.5, 'longitude': -40.5, 'descricao': 'Praia', 'email': 'fantasma@exemplo.com'
    })
    assert response.status_code == 404

def test_listar_pontos_de_usuario(client):
    """Testa a listagem de pontos de um usuário específico."""
    client.post('/AdicionarUsuario/',
                data={'email': 'user_com_pontos@exemplo.com', 'nome': 'Usuario Ponto'})
    client.post('/AdicionarPonto/', data={
        'latitude': 10, 'longitude': 10, 'descricao': 'Ponto A', 'email': 'user_com_pontos@exemplo.com'
    })
    client.post('/AdicionarPonto/', data={
        'latitude': 20, 'longitude': 20, 'descricao': 'Ponto B', 'email': 'user_com_pontos@exemplo.com'
    })

    response = client.get('/ListarPontos/?email=user_com_pontos@exemplo.com')
    json_data = response.get_json()
    assert response.status_code == 200
    assert len(json_data) == 2
    assert json_data[0]['descricao'] == 'Ponto A'


def test_atualizar_ponto_sucesso(client):
    """Testa a atualização da descrição de um ponto."""
    client.post('/AdicionarUsuario/',
                data={'email': 'user_att_ponto@exemplo.com', 'nome': 'Usuario Att Ponto'})
    client.post('/AdicionarPonto/', data={
        'latitude': 1, 'longitude': 1, 'descricao': 'Descricao Antiga', 'email': 'user_att_ponto@exemplo.com'
    })

    response_lista = client.get(
        '/ListarPontos/?email=user_att_ponto@exemplo.com')
    ponto_id = response_lista.get_json()[0]['id']

    response_put = client.put(
        f'/AtualizarPonto/{ponto_id}', data={'descricao': 'Descricao Nova'})
    assert response_put.status_code == 200
    assert response_put.get_json()['status'] == 'sucesso'

    response_lista_final = client.get(
        '/ListarPontos/?email=user_att_ponto@exemplo.com')
    assert 'Descricao Nova' in str(response_lista_final.data)
    assert 'Descricao Antiga' not in str(response_lista_final.data)


def test_remover_ponto_sucesso(client):
    """Testa a remoção de um ponto de interesse."""
    client.post('/AdicionarUsuario/',
                data={'email': 'user_rem_ponto@exemplo.com', 'nome': 'Usuario Rem Ponto'})
    client.post('/AdicionarPonto/', data={
        'latitude': 1, 'longitude': 1, 'descricao': 'Para Remover', 'email': 'user_rem_ponto@exemplo.com'
    })
    response_lista = client.get(
        '/ListarPontos/?email=user_rem_ponto@exemplo.com')
    ponto_id = response_lista.get_json()[0]['id']

    response_delete = client.delete(f'/RemoverPonto/{ponto_id}')
    assert response_delete.status_code == 200
    assert response_delete.get_json()['status'] == 'sucesso'

    response_lista_final = client.get(
        '/ListarPontos/?email=user_rem_ponto@exemplo.com')
    assert len(response_lista_final.get_json()) == 0


def test_remover_usuario_deleta_pontos_em_cascata(client):
    """Testa se ao remover um usuário, seus pontos também são removidos (ON DELETE CASCADE)."""
    client.post('/AdicionarUsuario/',
                data={'email': 'user_cascade@exemplo.com', 'nome': 'Usuario Cascade'})
    client.post('/AdicionarPonto/', data={
        'latitude': 1, 'longitude': 1, 'descricao': 'Ponto do Cascade', 'email': 'user_cascade@exemplo.com'
    })

    client.delete('/RemoverUsuario/',
                  data={'email': 'user_cascade@exemplo.com'})
    
    response_lista_pontos = client.get(
        '/ListarPontos/?email=user_cascade@exemplo.com')
    assert len(response_lista_pontos.get_json()) == 0

<img width="300" height="59" alt="terraLabLogo-Horizontal-300x59" src="https://github.com/user-attachments/assets/59bf3de6-c366-4874-8bdb-ee7e405ab4ce" />

# 4º Sprint - Nicholas Andrade 🐉

# API Geoespacial com Flask e PostGIS

![Status do Projeto](https://img.shields.io/badge/status-conclu%C3%ADdo-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0-orange)
![PostgreSQL](https://img.shields.io/badge/postgresql-14-blue)
![Pytest](https://img.shields.io/badge/pytest-11/11%20passed-brightgreen)

## 📖 Índice

- [1. Introdução](#1-introdução)
- [2. Funcionalidades](#2-funcionalidades)
- [3. Ferramentas e Tecnologias](#3-ferramentas-e-tecnologias)
- [4. Arquitetura do Sistema](#4-arquitetura-do-sistema)
- [5. Estrutura de Pastas](#5-estrutura-de-pastas)
- [6. Configuração do Ambiente e Instalação](#6-configuração-do-ambiente-e-instalação)
- [7. Endpoints da API](#7-endpoints-da-api)
- [8. Executando os Testes](#8-executando-os-testes)
- [9. Melhorias Futuras](#9-melhorias-futuras)
- [10. Autor](#10-autor)

## 1. Introdução

Este projeto consiste no desenvolvimento de um backend em Python para uma aplicação de nicho, que necessita armazenar e gerenciar pontos de interesse geográficos. A API permite o cadastro, visualização, alteração e remoção de usuários e dos pontos geográficos associados a eles, utilizando uma base de dados com capacidades geoespaciais.

## 2. Funcionalidades

✔️ **Gerenciamento de Usuários:**
  - `C`reate: Cadastrar novos usuários.
  - `R`ead: Listar todos os usuários.
  - `U`pdate: Atualizar o nome de um usuário existente.
  - `D`elete: Remover um usuário e todos os seus pontos associados (em cascata).

✔️ **Gerenciamento de Pontos de Interesse:**
  - `C`reate: Adicionar novos pontos geográficos (latitude, longitude e descrição) para um usuário.
  - `R`ead: Listar todos os pontos de um usuário específico.
  - `U`pdate: Atualizar a descrição e/ou coordenadas de um ponto existente.
  - `D`elete: Remover um ponto de interesse.

## 3. Ferramentas e Tecnologias

| Ferramenta | Descrição |
| --- | --- |
| **Python 3** | Linguagem de programação principal. |
| **Flask** | Micro-framework web para a construção da API. |
| **PostgreSQL** | Sistema de gerenciamento de banco de dados relacional. |
| **PostGIS** | Extensão geoespacial para o PostgreSQL, para armazenar e consultar dados geográficos. |
| **Psycopg2** | Driver para conectar a aplicação Python ao PostgreSQL. |
| **Pytest** | Framework para a execução dos testes unitários automatizados. |
| **Dotenv** | Módulo para gerenciar variáveis de ambiente a partir de um arquivo `.env`. |
| **Insomnia** | Ferramenta utilizada para os testes manuais dos endpoints. |

## 4. Arquitetura do Sistema

O sistema segue uma arquitetura cliente-servidor simples, onde o fluxo de uma requisição ocorre da seguinte forma:

```mermaid
graph TD
    A[Cliente <br> (ex: Insomnia, Frontend)] -- 1. Requisição HTTP --> B{Servidor Flask <br> (app.py)};
    B -- 2. Consulta SQL <br> (psycopg2) --> C[(Banco de Dados <br> PostgreSQL + PostGIS)];
    C -- 3. Retorna Dados --> B;
    B -- 4. Resposta JSON --> A;
```
1.  **Requisição HTTP**: O cliente (neste caso, o Insomnia, mas poderia ser um site ou aplicativo) envia uma requisição para um dos endpoints da API (ex: `POST /AdicionarUsuario/`).
2.  **Consulta SQL**: O servidor Flask recebe a requisição, processa os dados e se comunica com o banco de dados PostgreSQL através do driver `psycopg2`, executando uma instrução SQL para inserir, consultar, atualizar ou deletar dados. A extensão PostGIS é utilizada para manipular os dados geoespaciais.
3.  **Retorno de Dados**: O banco de dados processa a consulta e retorna o resultado para o servidor Flask.
4.  **Resposta JSON**: O servidor Flask formata a resposta no padrão JSON e a envia de volta para o cliente, que então exibe o resultado para o usuário.


## 5. Estrutura de Pastas

```
sprint4/
|-- .venv/
|-- tests/
|   |-- __init__.py
|   |-- test_app.py
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- README.md
|-- requirements.txt
|-- setup_database.py
```

## 6. Configuração do Ambiente e Instalação

Siga os passos abaixo para executar o projeto localmente.

### Pré-requisitos
- Python 3.9 ou superior.
- PostgreSQL com a extensão PostGIS instalada.

### Passos

**1. Crie e ative o ambiente virtual:**
```bash
# Navegue até a pasta do projeto e execute:
# Cria o ambiente
python -m venv .venv

# Ativa no Windows
.venv\Scripts\activate

# Ativa no Linux/macOS
source .venv/bin/activate
```

**2. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente:**
Crie uma cópia do arquivo `.env.example` (que deve estar no repositório) e renomeie-a para `.env`. Em seguida, preencha com suas credenciais do PostgreSQL.
```
DB_NAME=coordenadas_bd
DB_USER=postgres
DB_PASSWORD=sua_senha_secreta
DB_HOST=localhost
DB_PORT=5432
```

**4. Crie o banco de dados e as tabelas:**
- Crie um banco de dados no PostgreSQL com o mesmo nome que você definiu em `DB_NAME`.
- Ative a extensão PostGIS nele: `CREATE EXTENSION postgis;`
- Execute o script de setup para criar as tabelas:
```bash
python setup_database.py
```

**5. Execute a aplicação:**
```bash
flask run --port=8080
```
A API estará disponível em `http://localhost:8080`.

## 7. Endpoints da API

A seguir, a documentação de todos os endpoints disponíveis, divididos por recurso.

### Endpoints de Usuários

| Funcionalidade | Método | Endpoint | Parâmetros (Corpo) |
| :--- | :--- | :--- | :--- |
| **Adicionar Usuário** | ![POST](https://img.shields.io/badge/-%20POST-green) | `/AdicionarUsuario/` | `email`, `nome` |
| **Listar Usuários** | ![GET](https://img.shields.io/badge/-%20GET-blue) | `/ListarUsuarios/` | (Nenhum) |
| **Atualizar Usuário**| ![PUT](https://img.shields.io/badge/-%20PUT-orange) | `/AtualizarUsuario/` | `email`, `novo_nome` |
| **Remover Usuário** | ![DELETE](https://img.shields.io/badge/-%20DELETE-red) | `/RemoverUsuario/` | `email` |

<br>

### Endpoints de Pontos de Interesse

| Funcionalidade | Método | Endpoint | Parâmetros |
| :--- | :--- | :--- | :--- |
| **Adicionar Ponto** | ![POST](https://img.shields.io/badge/-%20POST-green) | `/AdicionarPonto/` | **Corpo:** `latitude`, `longitude`, `descricao`, `email` |
| **Listar Pontos** | ![GET](https://img.shields.io/badge/-%20GET-blue) | `/ListarPontos/` | **Query:** `email` |
| **Atualizar Ponto** | ![PUT](https://img.shields.io/badge/-%20PUT-orange) | `/AtualizarPonto/<id>` | **Corpo:** `descricao`, `latitude`, `longitude` (todos opcionais) |
| **Remover Ponto** | ![DELETE](https://img.shields.io/badge/-%20DELETE-red) | `/RemoverPonto/<id>` | (Nenhum) |


## 8. Executando os Testes

Para garantir a integridade e o funcionamento da API, foram criados testes unitários para todos os endpoints.

**Como executar:**
Com o ambiente virtual ativado, rode o seguinte comando na raiz do projeto:
```bash
pytest -v
```

**Resultado dos Testes:**
Todos os 11 testes foram executados e passaram com sucesso, cobrindo as principais funcionalidades e casos de erro da aplicação.


![pyTest](https://github.com/user-attachments/assets/f1df0c7d-f896-427b-87cf-7663f3409c80)


## 10. Autor

**Nicholas Andrade**

- LinkedIn: `[Seu Perfil no LinkedIn]`
- GitHub: `[Seu Perfil no GitHub]`
`

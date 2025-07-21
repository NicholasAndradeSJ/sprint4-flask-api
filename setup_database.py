import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

commands = (
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pontos_interesse (
        id SERIAL PRIMARY KEY,
        descricao VARCHAR(255) NOT NULL,
        geom GEOMETRY(Point, 4326) NOT NULL,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id)
            REFERENCES usuarios (id)
            ON DELETE CASCADE
    )
    """
)

conn = None
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cur = conn.cursor()
    for command in commands:
        cur.execute(command)

    cur.close()
    conn.commit()
    print("Tabelas criadas com sucesso!")

except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()

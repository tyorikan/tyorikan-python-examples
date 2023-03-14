import os

from fastapi import FastAPI
import sqlalchemy

from app.connect_connector import connect_with_connector
from app.connect_connector_auto_iam_authn import connect_with_connector_auto_iam_authn
from app.connect_tcp import connect_tcp_socket
from app.connect_unix import connect_unix_socket

app = FastAPI()


def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    if os.environ.get("INSTANCE_HOST"):
        return connect_tcp_socket()

    if os.environ.get("INSTANCE_UNIX_SOCKET"):
        return connect_unix_socket()

    if os.environ.get("INSTANCE_CONNECTION_NAME"):
        return connect_with_connector_auto_iam_authn() if os.environ.get("DB_IAM_USER") else connect_with_connector()

    raise ValueError(
        "Missing database connection type. Please define one of INSTANCE_HOST, INSTANCE_UNIX_SOCKET, or INSTANCE_CONNECTION_NAME"
    )


def migrate_db(db: sqlalchemy.engine.base.Engine) -> None:
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            position VARCHAR(255) NOT NULL,
            status TINYINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=INNODB;
    """
    sql2 = 'INSERT IGNORE INTO users VALUES (12345, "店長", 0, now());'
    with db.connect() as conn:
        conn.execute(sqlalchemy.text(sql))
        conn.execute(sqlalchemy.text(sql2))
        conn.commit()


db = None


@app.on_event("startup")
def init_db() -> sqlalchemy.engine.base.Engine:
    global db
    db = init_connection_pool()
    migrate_db(db)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items")
def read_item():
    users = []
    with db.connect() as conn:
        sql = """
            SELECT id, position FROM users LIMIT 5;
        """
        recent_users = conn.execute(sqlalchemy.text(sql)).fetchall()
        for row in recent_users:
            users.append({"id": row[0], "position": row[1]})
    return {"users": users}

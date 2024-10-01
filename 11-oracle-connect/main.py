import os

from fastapi import FastAPI
import oracledb

app = FastAPI()

user = os.environ.get("ORACLE_USER")
password = os.environ.get("ORACLE_PASSWORD")
host = os.environ.get("ORACLE_HOST", "localhost")
service_name = os.environ.get("ORACLE_SERVICE_NAME")
port = os.environ.get("ORACLE_PORT", 1521)

if os.environ.get("LD_LIBRARY_PATH"):
    oracledb.init_oracle_client(lib_dir=os.environ.get("LD_LIBRARY_PATH"))

conn = oracledb.connect(
    dsn="{}/{}".format(host, service_name),
    user=user,
    password=password,
    port=port,
    params=oracledb.ConnectParams(),
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items")
def read_item(skip: int = 0, limit: int = 10):
    with conn.cursor() as cursor:
        sql = """
            SELECT * FROM SampleQueryTab
            OFFSET {} ROWS FETCH FIRST {} ROWS ONLY
        """.format(skip, limit)
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor]
        return results

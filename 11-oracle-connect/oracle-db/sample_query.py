import oracledb

connection = oracledb.connect(
    user="pythondemo",
    password="a_secret",
    dsn="localhost/freepdb1",
)

sql = """select * from SampleQueryTab
         where id < 6
         order by id"""

with connection.cursor() as cursor:
    print("Get all rows via an iterator")
    for result in cursor.execute(sql):
        print(result)
    print()

    print("Query one row at a time")
    cursor.execute(sql)
    row = cursor.fetchone()
    print(row)
    row = cursor.fetchone()
    print(row)
    print()

    print("Fetch many rows")
    cursor.execute(sql)
    res = cursor.fetchmany(3)
    print(res)
    print()

    print("Fetch all rows")
    cursor.execute(sql)
    res = cursor.fetchall()
    print(res)
    print()

    print("Fetch each row as a Dictionary")
    cursor.execute(sql)
    columns = [col.name for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    for row in cursor:
        print(row)
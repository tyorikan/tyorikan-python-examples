from google.cloud import spanner


def run(instance_id, database_id):
    spanner_client = spanner.Client()

    instance = spanner_client.instance(instance_id)

    database = instance.database(database_id)

    with database.snapshot() as snapshot:
        results = snapshot.execute_sql("SELECT 1")

        for row in results:
            print(row)


if __name__ == "__main__":
    run(instance_id="demo", database_id="demo")

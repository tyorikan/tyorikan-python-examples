from google.cloud import spanner

class BaseRepository:
    def __init__(self, database):
        self.database = database

    # Helper for executing queries
    def execute_sql(self, sql: str, params: dict = None, param_types: dict = None, transaction=None):
        if transaction:
            return transaction.execute_sql(sql, params=params, param_types=param_types)
        else:
            with self.database.snapshot() as snapshot:
                return list(snapshot.execute_sql(sql, params=params, param_types=param_types))
    
    # Helper for simple inserts (using mutations)
    def insert(self, table: str, columns: list, values: list, transaction=None):
        if transaction:
            transaction.insert(table, columns=columns, values=values)
        else:
            def callback(transaction):
                transaction.insert(table, columns=columns, values=values)
            self.database.run_in_transaction(callback)

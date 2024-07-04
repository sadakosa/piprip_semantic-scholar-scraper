import psycopg2


class DBClient:
    def __init__(self, db_name, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def execute(self, query, params=None):
        self.cur.execute(query, params)
        return self.cur

    def commit(self):
        # print("Committing transaction")
        self.conn.commit()
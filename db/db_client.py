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
        if self.cur.description:  # Check if the query returns rows
            return self.cur.fetchall()

    def commit(self):
        self.conn.commit()
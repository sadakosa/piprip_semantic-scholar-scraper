import psycopg2


class DBClient:
    def __init__(self, db_name, user, password, host, port):
        config = load_yaml_config('config/config.yaml')

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

    def execute(self, query):
        self.cur.execute(query)
        self.commit() # to save any changes you make to the database
        return self.cur.fetchall()
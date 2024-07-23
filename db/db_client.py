# import psycopg2


# # class DBClient:
# #     def __init__(self, db_name, user, password, host, port):
# #         self.conn = psycopg2.connect(
# #             dbname=db_name,
# #             user=user,
# #             password=password,
# #             host=host,
# #             port=port
# #         )
# #         self.cur = self.conn.cursor()

# #     def __del__(self):
# #         self.cur.close()
# #         self.conn.close()

# #     def execute(self, query, params=None):
# #         self.cur.execute(query, params)
# #         return self.cur
    
# #     def rollback(self):
# #         self.conn.rollback()

# #     def commit(self):
# #         # print("Committing transaction")
# #         self.conn.commit()
    

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

    def __del__(self):
        if self.conn:
            self.conn.close()

    def cursor(self):
        return self.conn.cursor()

    def execute(self, query, params=None):
        with self.cursor() as cur:
            cur.execute(query, params)
            return cur

    def rollback(self):
        self.conn.rollback()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

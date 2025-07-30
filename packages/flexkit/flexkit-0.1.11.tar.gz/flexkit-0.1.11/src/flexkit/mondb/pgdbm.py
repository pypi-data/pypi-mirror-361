import psycopg2
from psycopg2.extras import RealDictCursor


class PgRecords:
    def __init__(
        self, db_url: str = "postgresql://postgres:123456@localhost:5432/postgres",
        dict_cursor: bool = True,
    ) -> None:
        self.conn = psycopg2.connect(db_url)
        if dict_cursor:
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        else:
            self.cur = self.conn.cursor()

    @property
    def rowcount(self):
        return self.cur.rowcount

    def query(self, sql: str, params: dict = None):
        if params:
            self.cur.execute(sql, params)
        else:
            self.cur.execute(sql)
        return self

    def bulk_query(self, sql: str, params: list):
        self.cur.executemany(sql, params)
        return self

    def all(self):
        return self.cur.fetchall()

    def first(self):
        return self.cur.fetchone()

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        if exc_type:
            self.conn.rollback()

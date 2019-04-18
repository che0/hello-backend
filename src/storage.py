import os
import MySQLdb
from contextlib import closing


class NumberStorage:
    def _env(self, key):
        """ Requires MYSQL_* env value """
        value = os.getenv('MYSQL_' + key)
        if value is None:
            raise ValueError('Missing env MYSQL_' + key)
        return value

    def __init__(self):
        self.db = MySQLdb.connect(
            host=self._env('HOST'),
            user=self._env('USER'),
            passwd=self._env('PASSWORD'),
            db=self._env('DATABASE'),
            use_unicode=True)
        self._initialize_db()

    def __del__(self):
        self.close()

    def close(self):
        if self.db:
            self.db.close()
        self.db = None

    def _initialize_db(self):
        with closing(self.db.cursor()) as c:
            c.execute("CREATE TABLE IF NOT EXISTS numbers (name VARCHAR(10) PRIMARY KEY, value INT UNSIGNED)")
            c.execute("CREATE TABLE IF NOT EXISTS reset_log (reset_time DATETIME PRIMARY KEY)")
            c.execute("INSERT IGNORE INTO numbers (name, value) VALUES ('the_number', 0)")
            c.execute("INSERT IGNORE INTO numbers (name, value) VALUES ('reset_cnt', 0)")

    def increment_and_get_number(self):
        with closing(self.db.cursor()) as c:
            try:
                c.execute('START TRANSACTION')
                c.execute("UPDATE numbers SET value = value + 1 WHERE name = 'the_number'")
                c.execute("SELECT value FROM numbers WHERE name = 'the_number'")
                new_value = c.fetchone()[0]
                c.execute('COMMIT')
                return new_value
            except Exception:
                c.execute('ROLLBACK')
                raise

    def reset_counter(self):
        with closing(self.db.cursor()) as c:
            try:
                c.execute('START TRANSACTION')
                c.execute("UPDATE numbers SET value = 0 WHERE name = 'the_number'")
                c.execute("UPDATE numbers SET value = value + 1 WHERE name = 'reset_cnt'")
                c.execute("INSERT INTO reset_log (reset_time) VALUES (NOW())")
                c.execute('COMMIT')
            except Exception:
                c.execute('ROLLBACK')
                raise

    def reset_info(self):
        with closing(self.db.cursor()) as c:
            try:
                c.execute('START TRANSACTION')
                c.execute("SELECT value FROM numbers WHERE name = 'reset_cnt'")
                reset_count = c.fetchone()[0]
                c.execute("SELECT MAX(reset_time) FROM reset_log")
                if c.rowcount > 0:
                    last_reset = c.fetchone()[0]
                else:
                    last_reset = None
                return {'count': reset_count, 'last': last_reset}
            finally:
                c.execute('ROLLBACK')

import sqlite3
from contextlib import contextmanager
from typing import Any, Generator, Optional

import pymysql

from core.config import settings


class DatabaseConnection:
    def __init__(self):
        self._connection: Optional[Any] = None

    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        if settings.db_type == 'sqlite':
            conn = sqlite3.connect(str(settings.sqlite_path))
            conn.row_factory = sqlite3.Row
        elif settings.db_type == 'mysql':
            conn = pymysql.connect(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                database=settings.mysql_database,
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            raise ValueError(f'Unsupported database type: {settings.db_type}')

        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


db_connection = DatabaseConnection()
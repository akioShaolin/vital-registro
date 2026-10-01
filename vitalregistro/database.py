"""SQLite repository. Every write is atomic and every connection is closed."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .models import Measurement


class RepositoryError(Exception):
    pass


class RecordNotFound(RepositoryError):
    pass


class Repository:
    def __init__(self, path):
        self.path = Path(path)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self._connection() as conn:
                version = conn.execute("PRAGMA user_version").fetchone()[0]
                if version > 1:
                    raise RepositoryError("Banco de uma versão mais nova. Atualize o aplicativo.")
                conn.execute("""CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measured_at TEXT NOT NULL,
                    systolic INTEGER NOT NULL CHECK(systolic BETWEEN 1 AND 400),
                    diastolic INTEGER NOT NULL CHECK(diastolic BETWEEN 1 AND 300),
                    pulse INTEGER NOT NULL CHECK(pulse BETWEEN 1 AND 350),
                    weight TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                )""")
                conn.execute("CREATE INDEX IF NOT EXISTS measurements_date ON measurements(measured_at)")
                conn.execute("PRAGMA user_version = 1")
        except OSError as exc:
            raise RepositoryError("Não foi possível abrir a pasta de dados.") from exc

    @contextmanager
    def _connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.path, timeout=10)
            conn.row_factory = sqlite3.Row
            with conn:
                yield conn
        except sqlite3.Error as exc:
            raise RepositoryError("Não foi possível acessar o banco. Seus dados não foram substituídos.") from exc
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def _values(record):
        return (record.measured_at.isoformat(timespec="minutes"), record.systolic,
                record.diastolic, record.pulse, str(record.weight), record.note)

    @staticmethod
    def _record(row):
        return Measurement(datetime.fromisoformat(row["measured_at"]), row["systolic"],
                           row["diastolic"], row["pulse"], Decimal(row["weight"]), row["note"], row["id"])

    def create(self, record):
        if record.id is not None:
            raise RepositoryError("Um novo registro não pode ter ID existente.")
        with self._connection() as conn:
            cursor = conn.execute("""INSERT INTO measurements
                (measured_at, systolic, diastolic, pulse, weight, note) VALUES (?, ?, ?, ?, ?, ?)""",
                                  self._values(record))
            return cursor.lastrowid

    def get(self, record_id):
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM measurements WHERE id = ?", (record_id,)).fetchone()
        if row is None:
            raise RecordNotFound("Registro não encontrado. Atualize a listagem.")
        return self._record(row)

    def list(self, start=None, end=None, newest_first=True):
        clauses, parameters = [], []
        if start is not None:
            clauses.append("measured_at >= ?")
            parameters.append(start.isoformat(timespec="minutes"))
        if end is not None:
            clauses.append("measured_at <= ?")
            parameters.append(end.isoformat(timespec="minutes"))
        query = "SELECT * FROM measurements"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        direction = "DESC" if newest_first else "ASC"
        query += f" ORDER BY measured_at {direction}, id {direction}"
        with self._connection() as conn:
            return [self._record(row) for row in conn.execute(query, parameters)]

    def update(self, record):
        with self._connection() as conn:
            result = conn.execute("""UPDATE measurements SET measured_at=?, systolic=?,
                diastolic=?, pulse=?, weight=?, note=? WHERE id=?""", self._values(record) + (record.id,))
            if result.rowcount != 1:
                raise RecordNotFound("Registro não encontrado para edição.")

    def delete(self, record_id):
        with self._connection() as conn:
            result = conn.execute("DELETE FROM measurements WHERE id=?", (record_id,))
            if result.rowcount != 1:
                raise RecordNotFound("Registro não encontrado para exclusão.")

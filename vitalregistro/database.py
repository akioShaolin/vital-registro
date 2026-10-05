"""SQLite repository. Every write is atomic and every connection is closed."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Measurement, ValidationError


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
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                if version != 2 and (version != 0 or tables):
                    raise RepositoryError("Banco incompatível (schema antigo ou mais novo). "
                                          "O arquivo foi preservado; a v0.2.0 usa um banco separado.")
                if version == 2:
                    columns = {row[1] for row in conn.execute("PRAGMA table_info(measurements)")}
                    expected = {"id", "measured_at", "kind", "systolic", "diastolic", "pulse",
                                "weight", "glucose", "context", "note"}
                    if columns != expected:
                        raise RepositoryError("Estrutura do banco incompatível. O arquivo foi preservado.")
                conn.execute("""CREATE TABLE IF NOT EXISTS measurements (
                    id TEXT PRIMARY KEY NOT NULL,
                    measured_at TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK(kind IN ('pressao','peso','glicemia')),
                    systolic INTEGER, diastolic INTEGER, pulse INTEGER,
                    weight TEXT, glucose INTEGER, context TEXT,
                    note TEXT NOT NULL DEFAULT '' CHECK(length(note) <= 5000),
                    CHECK (
                        (kind='pressao' AND systolic IS NOT NULL AND diastolic IS NOT NULL AND pulse IS NOT NULL
                         AND typeof(systolic)='integer' AND systolic BETWEEN 1 AND 400
                         AND typeof(diastolic)='integer' AND diastolic BETWEEN 1 AND 300
                         AND typeof(pulse)='integer' AND pulse BETWEEN 1 AND 350
                         AND weight IS NULL AND glucose IS NULL AND context IS NULL)
                        OR (kind='peso' AND weight IS NOT NULL AND CAST(weight AS REAL)>0
                            AND CAST(weight AS REAL)<=700 AND systolic IS NULL AND diastolic IS NULL
                            AND pulse IS NULL AND glucose IS NULL AND context IS NULL)
                        OR (kind='glicemia' AND glucose IS NOT NULL AND typeof(glucose)='integer'
                            AND glucose BETWEEN 1 AND 2000 AND context IS NOT NULL
                            AND context IN ('jejum','antes_refeicao','apos_refeicao','outro')
                            AND systolic IS NULL AND diastolic IS NULL AND pulse IS NULL AND weight IS NULL)
                    )
                )""")
                conn.execute("CREATE INDEX IF NOT EXISTS measurements_date ON measurements(measured_at)")
                conn.execute("PRAGMA user_version = 2")
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
        return (record.measured_at.isoformat(timespec="minutes"), record.kind, record.systolic,
                record.diastolic, record.pulse, str(record.weight) if record.weight is not None else None,
                record.glucose, record.context, record.note, record.id)

    @staticmethod
    def _record(row):
        try:
            return Measurement(datetime.fromisoformat(row["measured_at"]), row["kind"],
                               row["systolic"], row["diastolic"], row["pulse"],
                               Decimal(row["weight"]) if row["weight"] is not None else None,
                               row["glucose"], row["context"], row["note"], row["id"])
        except (ValidationError, ValueError, InvalidOperation, TypeError) as exc:
            raise RepositoryError("Registro inválido no banco. O arquivo foi preservado.") from exc

    def _insert(self, conn, record):
        conn.execute("""INSERT INTO measurements
            (measured_at,kind,systolic,diastolic,pulse,weight,glucose,context,note,id)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", self._values(record))

    def create(self, record):
        with self._connection() as conn:
            self._insert(conn, record)
        return record.id

    def import_records(self, records):
        """Recheck IDs under a write lock. Any conflict/failure rolls back the batch."""
        inserted = duplicates = 0
        with self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            for record in records:
                row = conn.execute("SELECT * FROM measurements WHERE id=?", (record.id,)).fetchone()
                if row is not None:
                    if self._record(row) != record:
                        raise RepositoryError("UUID com conteúdo diferente. Nada foi importado.")
                    duplicates += 1
                else:
                    self._insert(conn, record)
                    inserted += 1
        return inserted, duplicates

    def get(self, record_id):
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM measurements WHERE id = ?", (record_id,)).fetchone()
        if row is None:
            raise RecordNotFound("Registro não encontrado. Atualize a listagem.")
        return self._record(row)

    def list(self, start=None, end=None, newest_first=True, kind=None):
        clauses, parameters = [], []
        if start is not None:
            clauses.append("measured_at >= ?")
            parameters.append(start.isoformat(timespec="minutes"))
        if end is not None:
            clauses.append("measured_at <= ?")
            parameters.append(end.isoformat(timespec="minutes"))
        if kind is not None:
            clauses.append("kind = ?")
            parameters.append(kind)
        query = "SELECT * FROM measurements"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        direction = "DESC" if newest_first else "ASC"
        query += f" ORDER BY measured_at {direction}, id {direction}"
        with self._connection() as conn:
            return [self._record(row) for row in conn.execute(query, parameters)]

    def update(self, record):
        with self._connection() as conn:
            previous = conn.execute("SELECT kind FROM measurements WHERE id=?", (record.id,)).fetchone()
            if previous and previous["kind"] != record.kind:
                raise RepositoryError("A edição não pode alterar o tipo da medição.")
            result = conn.execute("""UPDATE measurements SET measured_at=?, kind=?, systolic=?,
                diastolic=?, pulse=?, weight=?, glucose=?, context=?, note=? WHERE id=?""", self._values(record))
            if result.rowcount != 1:
                raise RecordNotFound("Registro não encontrado para edição.")

    def delete(self, record_id):
        with self._connection() as conn:
            result = conn.execute("DELETE FROM measurements WHERE id=?", (record_id,))
            if result.rowcount != 1:
                raise RecordNotFound("Registro não encontrado para exclusão.")

"""All measurements below are invented fixtures, never personal records."""

import csv
import io
import sqlite3
import tempfile
import unittest
from contextlib import closing
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from vitalregistro.database import Repository, RepositoryError, RecordNotFound
from vitalregistro.export import HEADER, csv_text, save_csv
from vitalregistro.models import Measurement, ValidationError
from vitalregistro.periods import period_bounds


def fictional_record(day="15/04/2025", clock="08:30", **kwargs):
    return Measurement.from_fields(day, clock, "120", "80", "72", "70,50",
                                   kwargs.get("note", "EXEMPLO FICTÍCIO"))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "measurements.sqlite3"
        self.repo = Repository(self.path)

    def test_create_get_and_persist_after_reopening(self):
        record = fictional_record()
        record_id = self.repo.create(record)
        self.assertEqual(Repository(self.path).get(record_id), replace(record, id=record_id))

    def test_edit_every_field_and_reorder(self):
        record_id = self.repo.create(fictional_record())
        other_id = self.repo.create(fictional_record("16/04/2025"))
        updated = Measurement.from_fields("01/01/2026", "23:59", "125", "82", "75", "71.25",
                                          'FICTÍCIO: edição, "aspas"\nsegunda linha', record_id)
        self.repo.update(updated)
        self.assertEqual(self.repo.get(record_id), updated)
        self.assertEqual([r.id for r in self.repo.list()], [record_id, other_id])

    def test_delete_and_missing_records(self):
        record_id = self.repo.create(fictional_record())
        self.repo.delete(record_id)
        self.assertEqual(self.repo.list(), [])
        for action in (lambda: self.repo.get(record_id), lambda: self.repo.delete(record_id),
                       lambda: self.repo.update(replace(fictional_record(), id=record_id))):
            with self.assertRaises(RecordNotFound):
                action()

    def test_chronology_across_years_and_same_minute(self):
        dates = [("01/01/2026", "00:01"), ("31/12/2025", "23:59"), ("01/01/2026", "00:01")]
        ids = [self.repo.create(fictional_record(*pair)) for pair in dates]
        self.assertEqual([r.id for r in self.repo.list()], [ids[2], ids[0], ids[1]])
        self.assertEqual([r.id for r in self.repo.list(newest_first=False)], [ids[1], ids[0], ids[2]])

    def test_inclusive_date_filter(self):
        for day, hour in (("01/01/2026", "00:00"), ("07/01/2026", "23:59"), ("08/01/2026", "00:00")):
            self.repo.create(fictional_record(day, hour))
        self.assertEqual(len(self.repo.list(*period_bounds(7, date(2026, 1, 7)))), 2)

    def test_future_schema_is_not_overwritten(self):
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute("PRAGMA user_version = 99")
        with self.assertRaises(RepositoryError):
            Repository(self.path)
        with closing(sqlite3.connect(self.path)) as conn:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 99)

    def test_invalid_sql_write_rolls_back(self):
        record_id = self.repo.create(fictional_record())
        with self.assertRaises(RepositoryError):
            with self.repo._connection() as conn:
                conn.execute("UPDATE measurements SET pulse=0 WHERE id=?", (record_id,))
        self.assertEqual(self.repo.get(record_id).pulse, 72)

    def test_corrupt_database_is_not_replaced(self):
        path = Path(self.temp.name) / "corrupt.db"
        path.write_bytes(b"not a SQLite database")
        with self.assertRaises(RepositoryError):
            Repository(path)
        self.assertEqual(path.read_bytes(), b"not a SQLite database")


class ValidationTests(unittest.TestCase):
    def test_historical_leap_day_and_decimal_comma(self):
        record = fictional_record("29/02/2024", "00:00")
        self.assertEqual(record.measured_at, datetime(2024, 2, 29))
        self.assertEqual(record.weight, Decimal("70.50"))

    def test_invalid_dates_and_times(self):
        for day, hour in (("29/02/2025", "12:00"), ("31/04/2025", "12:00"), ("01/01/2025", "24:00")):
            with self.subTest(day=day, hour=hour), self.assertRaises(ValidationError):
                fictional_record(day, hour)

    def test_invalid_numbers(self):
        for weight in ("NaN", "Infinity", "-1", "0", "701", "abc", "1,2,3"):
            with self.subTest(weight=weight), self.assertRaises(ValidationError):
                Measurement.from_fields("01/01/2025", "10:00", "120", "80", "72", weight)
        for field in ("systolic", "diastolic", "pulse"):
            for value in (0, -1, 9999, 12.5, True):
                with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                    replace(fictional_record(), **{field: value})

    def test_long_note_rejected(self):
        with self.assertRaises(ValidationError):
            fictional_record(note="x" * 5001)

    def test_period_crosses_year_boundary(self):
        self.assertEqual(period_bounds(7, date(2026, 1, 3)),
                         (datetime(2025, 12, 28), datetime(2026, 1, 3, 23, 59)))
        self.assertEqual(period_bounds(None), (None, None))


class ExportTests(unittest.TestCase):
    def test_special_characters_round_trip(self):
        note = 'FICTÍCIO: ação, "aspas"\nlinha dois\r\nterceira; =texto'
        rows = list(csv.reader(io.StringIO(csv_text([fictional_record(note=note)]), newline="")))
        self.assertEqual(rows[0], list(HEADER))
        self.assertEqual(rows[1], ["15/04/2025", "08:30", "120", "80", "72", "70.50", note])

    def test_utf8_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fictional.csv"
            text = csv_text([fictional_record()])
            save_csv(path, text)
            original = path.read_bytes()
            self.assertEqual(original.decode("utf-8"), text)
            with self.assertRaises(FileExistsError):
                save_csv(path, "overwrite")
            self.assertEqual(path.read_bytes(), original)

    def test_empty_export_has_header(self):
        self.assertEqual(list(csv.reader(io.StringIO(csv_text([])))), [list(HEADER)])


if __name__ == "__main__":
    unittest.main()

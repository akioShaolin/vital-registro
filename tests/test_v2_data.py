"""Fictional v2 data, strict import and transactional integrity."""
import csv
import io
import sqlite3
import tempfile
import unittest
from contextlib import closing
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from vitalregistro.models import Measurement, ValidationError, CONTEXTS
from vitalregistro.database import Repository, RepositoryError
from vitalregistro.export import csv_text, HEADER
from vitalregistro.import_csv import preview_csv, MAX_BYTES


def samples():
    moment = datetime(2026, 10, 5, 8, 12)
    return [Measurement(moment, "pressao", systolic=151, diastolic=86, pulse=74),
            Measurement(moment.replace(hour=7), "peso", weight=Decimal("104.200")),
            Measurement(moment.replace(hour=9), "glicemia", glucose=96, context="jejum",
                        note='FICTÍCIO: ação, "aspas"\nlinha 2\r\nlinha 3')]

class DataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Repository(Path(self.temp.name)/"data.db")

    def preview(self, records, existing=()):
        return preview_csv(csv_text(records).encode("utf-8"), existing)

    def test_three_types_crud_and_type_filter(self):
        for record in samples():
            self.repo.create(record)
            self.assertEqual(self.repo.get(record.id), record)
            updated = replace(record, note="Editado", measured_at=record.measured_at.replace(day=1))
            self.repo.update(updated)
            self.assertEqual(self.repo.get(record.id), updated)
            self.assertEqual(self.repo.list(kind=record.kind), [updated])
            self.repo.delete(record.id)
        self.assertEqual(self.repo.list(), [])

    def test_edit_preserves_uuid_and_rejects_type_change(self):
        record = samples()[0]
        self.repo.create(record)
        with self.assertRaises(RepositoryError):
            self.repo.update(replace(samples()[1], id=record.id))
        self.assertEqual(self.repo.get(record.id), record)

    def test_same_day_distinct_times_sorted(self):
        records = samples()
        for record in records:
            self.repo.create(record)
        self.assertEqual(self.repo.list(newest_first=False), [records[1], records[0], records[2]])

    def test_round_trip_preserves_all_values_and_ids(self):
        for record in samples():
            self.repo.create(record)
        source = self.repo.list(newest_first=False)
        preview = self.preview(source)
        self.assertTrue(preview.can_import)
        other = Repository(Path(self.temp.name)/"other.db")
        self.assertEqual(other.import_records(preview.records), (3, 0))
        self.assertEqual(other.list(newest_first=False), source)
        repeated = self.preview(source, other.list())
        self.assertEqual((len(repeated.records), repeated.duplicates), (0, 3))
        self.assertFalse(repeated.can_import)
        self.assertEqual(other.import_records(source), (0, 3))

    def test_duplicate_inside_file_and_uuid_conflict(self):
        r = samples()[0]
        p = self.preview([r, r])
        self.assertEqual((len(p.records), p.duplicates), (1, 1))
        p = self.preview([r, replace(r, pulse=75)])
        self.assertEqual(p.conflicts, 1)
        self.assertFalse(p.can_import)
        self.repo.create(r)
        self.assertFalse(self.preview([replace(r, pulse=75)], self.repo.list()).can_import)

    def test_no_fuzzy_deduplication_for_distinct_uuid(self):
        a, b = samples()[0], samples()[0]
        p = self.preview([a, b])
        self.assertEqual(len(p.records), 2)

    def test_import_rolls_back_on_later_conflict(self):
        a, b, _ = samples()
        self.repo.create(b)
        with self.assertRaises(RepositoryError):
            self.repo.import_records([a, replace(b, note="conflito")])
        self.assertEqual(self.repo.list(), [b])

    def test_import_rolls_back_on_unexpected_write_failure(self):
        original = self.repo._insert
        def fail_second(conn, record):
            original(conn, record)
            if record.kind == "peso":
                raise sqlite3.OperationalError("injected failure")
        with patch.object(self.repo, "_insert", side_effect=fail_second), self.assertRaises(RepositoryError):
            self.repo.import_records(samples())
        self.assertEqual(self.repo.list(), [])

    def test_preview_never_writes_and_commit_rechecks_after_preview(self):
        r = samples()[0]
        preview = self.preview([r])
        self.assertEqual(self.repo.list(), [])
        self.repo.create(replace(r, pulse=75))
        with self.assertRaises(RepositoryError):
            self.repo.import_records(preview.records)
        self.assertEqual(self.repo.get(r.id).pulse, 75)

    def test_invalid_csv_cells_block_whole_batch(self):
        base = list(csv.reader(io.StringIO(csv_text([samples()[0]]))))
        for column, value in ((0,"1"),(1,"bad-id"),(2,"other"),(3,"2025-02-29T08:00"),
                              (3,"2026-10-05T08:12:01"),(3,"2026-10-05T08:12+03:00"),
                              (4,""),(4,"NaN"),(4,"0"),(7,"80"),(10,"x"*5001)):
            with self.subTest(column=column, value=value[:20]):
                row = base[1].copy(); row[column] = value
                out = io.StringIO(newline=""); writer=csv.writer(out)
                writer.writerows([base[0], base[1], row])
                p=preview_csv(out.getvalue().encode())
                self.assertFalse(p.can_import)
                self.assertEqual(len(p.errors), 1)
                self.assertEqual(self.repo.list(), [])

    def test_encoding_header_quotes_and_limits(self):
        for payload in (b"bad header", b"\xff", b"x"*(MAX_BYTES+1)):
            with self.assertRaises(ValidationError):
                preview_csv(payload)
        p=preview_csv((",".join(HEADER)+'\n"unfinished').encode())
        self.assertTrue(p.errors)
        self.assertFalse(p.can_import)
        self.assertTrue(preview_csv(b"\xef\xbb\xbf"+csv_text(samples()).encode()).can_import)

    def test_all_contexts_and_decimal_roundtrip(self):
        for context in CONTEXTS:
            record=replace(samples()[2],context=context)
            self.assertEqual(self.preview([record]).records, (record,))
        record=replace(samples()[1],weight=Decimal("1E+2"))
        self.assertEqual(self.preview([record]).records, (record,))
        with self.assertRaises(ValidationError):
            replace(samples()[2],context="unknown")
        with self.assertRaises(ValidationError):
            replace(samples()[1],weight=Decimal("70.1234"))

    def test_old_schema_is_preserved(self):
        path=Path(self.temp.name)/"old.db"
        with closing(sqlite3.connect(path)) as c:
            c.execute("CREATE TABLE measurements (id INTEGER)")
            c.execute("PRAGMA user_version=1")
        original=path.read_bytes()
        with self.assertRaisesRegex(RepositoryError,"preservado"):
            Repository(path)
        self.assertEqual(path.read_bytes(),original)

    def test_sql_type_constraints_and_duplicate_ids(self):
        a=samples()[0]; self.repo.create(a)
        with self.assertRaises(RepositoryError):
            self.repo.create(a)
        with self.assertRaises(RepositoryError), self.repo._connection() as c:
            c.execute("UPDATE measurements SET weight='70' WHERE id=?",(a.id,))
        self.assertEqual(self.repo.get(a.id),a)

    def test_edit_specific_values_each_type(self):
        changes = [{"systolic":130,"diastolic":81,"pulse":75},
                   {"weight":Decimal("71.125")}, {"glucose":101,"context":"apos_refeicao"}]
        for record, values in zip(samples(), changes):
            self.repo.create(record)
            changed=replace(record,**values)
            self.repo.update(changed)
            self.assertEqual(self.repo.get(record.id), changed)
            self.assertEqual(self.preview([changed]).records,(changed,))

    def test_missing_glucose_context_and_extra_fields(self):
        for changes in ({"context":None},{"glucose":None},{"glucose":0},{"glucose":2001},
                        {"glucose":True},{"glucose":96.5},{"weight":Decimal("70")}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                replace(samples()[2],**changes)

    def test_row_count_limit_and_wrong_column_count(self):
        with patch("vitalregistro.import_csv.MAX_RECORDS", 2), self.assertRaises(ValidationError):
            self.preview(samples())
        text=csv_text(samples())+"2,missing-columns\n"
        self.assertFalse(preview_csv(text.encode()).can_import)

    def test_unexpected_non_sql_error_also_rolls_back(self):
        original=self.repo._insert
        def insert_then_fail(conn, record):
            original(conn,record)
            raise RuntimeError("injected unexpected failure")
        with patch.object(self.repo,"_insert",side_effect=insert_then_fail), self.assertRaises(RuntimeError):
            self.repo.import_records(samples())
        self.assertEqual(self.repo.list(),[])

    def test_invalid_stored_record_reports_repository_error(self):
        record=samples()[0]; self.repo.create(record)
        with self.repo._connection() as c:
            c.execute("UPDATE measurements SET measured_at='invalid' WHERE id=?",(record.id,))
        with self.assertRaisesRegex(RepositoryError,"preservado"):
            self.repo.list()

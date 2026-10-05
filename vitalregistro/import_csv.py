"""Strict, bounded UTF-8 CSV preview; no writes until explicit confirmation."""
import csv
import io
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from .export import HEADER, FORMAT_VERSION
from .models import Measurement, ValidationError

MAX_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 20000

@dataclass(frozen=True)
class ImportPreview:
    records: tuple
    total: int
    duplicates: int
    conflicts: int
    errors: tuple

    @property
    def can_import(self):
        return not self.errors and not self.conflicts and bool(self.records)

    def summary(self):
        return (f"{self.total} linhas de dados encontradas\n"
                f"{len(self.records)} registros novos válidos\n"
                f"{self.duplicates} duplicatas idênticas (ignoradas)\n"
                f"{self.conflicts} conflitos de UUID\n"
                f"{len(self.errors)} erros\n\n" + "\n".join(self.errors[:8]) +
                ("\nCorrija os erros/conflitos e selecione o arquivo novamente. Nada será gravado."
                 if self.errors or self.conflicts else "\nA importação adiciona registros; não substitui o histórico."))


def _record(row):
    if len(row) != len(HEADER) or row[0] != FORMAT_VERSION:
        raise ValidationError("Quantidade de colunas ou versão do formato inválida.")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}", row[3]):
        raise ValidationError("Timestamp deve usar AAAA-MM-DDTHH:MM, sem fuso.")
    values = {}
    for name, value in zip(("systolic", "diastolic", "pulse", "weight", "glucose", "context"), row[4:10]):
        if value != "":
            if name in ("systolic", "diastolic", "pulse", "glucose"):
                if not re.fullmatch(r"[0-9]+", value):
                    raise ValidationError("Campo inteiro inválido.")
                values[name] = int(value)
            elif name == "weight":
                if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,3})?", value):
                    raise ValidationError("Peso deve usar ponto decimal e até 3 casas.")
                values[name] = Decimal(value)
            else:
                values[name] = value
    return Measurement(datetime.fromisoformat(row[3]), row[2], id=row[1], note=row[10], **values)


def preview_csv(payload, existing=()):
    if len(payload) > MAX_BYTES:
        raise ValidationError("CSV excede o limite de 10 MiB.")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError("Selecione um CSV codificado em UTF-8.") from exc
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    try:
        if next(reader, None) != list(HEADER):
            raise ValidationError("Cabeçalho incompatível. Use uma exportação v0.2.0 (formato 2).")
    except csv.Error as exc:
        raise ValidationError("Cabeçalho CSV malformado.") from exc
    seen = {r.id: r for r in existing}
    records, errors = [], []
    duplicates = conflicts = total = 0
    try:
        for row in reader:
            total += 1
            if total > MAX_RECORDS:
                raise ValidationError("CSV excede o limite de 20000 registros.")
            try:
                record = _record(row)
            except (ValueError, InvalidOperation) as exc:
                message = str(exc) if isinstance(exc, ValidationError) else "Data ou número inválido."
                errors.append(f"Linha {reader.line_num}: {message}")
                continue
            if record.id in seen:
                if record == seen[record.id]:
                    duplicates += 1
                else:
                    conflicts += 1
            else:
                seen[record.id] = record
                records.append(record)
    except csv.Error:
        errors.append(f"Linha {reader.line_num}: estrutura CSV malformada; leitura interrompida.")
    return ImportPreview(tuple(records), total, duplicates, conflicts, tuple(errors))


def read_csv_file(path):
    with open(path, "rb") as source:
        payload = source.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValidationError("CSV excede o limite de 10 MiB.")
    return payload

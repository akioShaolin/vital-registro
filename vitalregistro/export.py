"""CSV with exact note preservation and exclusive creation of local files."""

import csv
import io

FORMAT_VERSION = "2"
HEADER = ("formato", "id", "tipo", "timestamp", "sistolica", "diastolica", "pulso",
          "peso", "glicemia", "contexto", "observacao")


def csv_text(records):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(HEADER)
    for row in records:
        writer.writerow((FORMAT_VERSION, row.id, row.kind, row.measured_at.isoformat(timespec="minutes"),
                         row.systolic, row.diastolic, row.pulse,
                         format(row.weight, "f") if row.weight is not None else None,
                         row.glucose, row.context, row.note))
    return output.getvalue()


def save_csv(path, text):
    # Never silently overwrite a previous export.
    with open(path, "x", encoding="utf-8", newline="") as output:
        output.write(text)

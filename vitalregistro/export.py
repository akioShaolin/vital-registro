"""CSV with exact note preservation and exclusive creation of local files."""

import csv
import io

HEADER = ("data", "hora", "sistolica", "diastolica", "pulso", "peso", "observacao")


def csv_text(records):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(HEADER)
    for row in records:
        writer.writerow((row.measured_at.strftime("%d/%m/%Y"), row.measured_at.strftime("%H:%M"),
                         row.systolic, row.diastolic, row.pulse, str(row.weight), row.note))
    return output.getvalue()


def save_csv(path, text):
    # Never silently overwrite a previous export.
    with open(path, "x", encoding="utf-8", newline="") as output:
        output.write(text)

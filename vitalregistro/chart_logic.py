"""Time projection and bounded hit testing, independent of Kivy."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ChartPoint:
    x: float
    y: float
    record: object
    field: str


def project_x(moment, first, last, left, width):
    seconds = (last - first).total_seconds()
    return left + width * ((moment - first).total_seconds() / seconds if seconds else .5)


def hit_points(points, x, y, tolerance):
    """Return closest hits only; exact overlaps remain available for disambiguation."""
    hits = [((p.x-x)**2 + (p.y-y)**2, i, p) for i, p in enumerate(points)
            if (p.x-x)**2 + (p.y-y)**2 <= tolerance**2]
    hits.sort(key=lambda item: (item[0], item[1]))
    if not hits:
        return []
    nearest = hits[0][0]
    return [p for distance, _, p in hits if abs(distance - nearest) < 1e-6]


def point_text(point):
    labels = {"systolic": ("Sistólica", "mmHg"), "diastolic": ("Diastólica", "mmHg"),
              "pulse": ("Pulso", "bpm"), "weight": ("Peso", "kg"), "glucose": ("Glicemia", "mg/dL")}
    from .models import CONTEXTS
    record = point.record
    name, unit = labels[point.field]
    value = str(getattr(record, point.field)).replace(".", ",")
    text = f"{record.measured_at:%d/%m/%Y %H:%M}\n{name}: {value} {unit}"
    if record.kind == "glicemia":
        text += "\n" + CONTEXTS[record.context]
    return text

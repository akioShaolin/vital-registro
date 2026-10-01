"""Validation independent of the GUI. Limits reject typing errors, not diagnoses."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Measurement:
    measured_at: datetime
    systolic: int
    diastolic: int
    pulse: int
    weight: Decimal
    note: str = ""
    id: int | None = None

    def __post_init__(self):
        if not isinstance(self.measured_at, datetime) or self.measured_at.tzinfo is not None:
            raise ValidationError("Informe uma data e horário locais válidos.")
        for name, value, maximum in (
            ("Sistólica", self.systolic, 400),
            ("Diastólica", self.diastolic, 300),
            ("Pulso", self.pulse, 350),
        ):
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValidationError(f"{name}: use um inteiro de 1 a {maximum}.")
        if not isinstance(self.weight, Decimal) or not self.weight.is_finite() or not 0 < self.weight <= 700:
            raise ValidationError("Peso: informe um número maior que zero e até 700 kg.")
        if not isinstance(self.note, str) or len(self.note) > 5000:
            raise ValidationError("A observação deve ter até 5000 caracteres.")

    @classmethod
    def from_fields(cls, day, clock, systolic, diastolic, pulse, weight, note="", record_id=None):
        try:
            moment = datetime.strptime(f"{day.strip()} {clock.strip()}", "%d/%m/%Y %H:%M")
        except ValueError as exc:
            raise ValidationError("Confira a data (dia/mês/ano) e o horário (hora:minuto).") from exc
        try:
            values = [int(str(v).strip()) for v in (systolic, diastolic, pulse)]
        except ValueError as exc:
            raise ValidationError("Pressão e pulso devem ser números inteiros.") from exc
        try:
            decimal = Decimal(str(weight).strip().replace(",", "."))
        except InvalidOperation as exc:
            raise ValidationError("Informe um peso válido, como 70,5.") from exc
        return cls(moment, *values, decimal, note, record_id)

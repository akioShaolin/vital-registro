"""Independent, UUID-addressed measurements. Validation is not diagnosis."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid4

TYPES = {"pressao": "Pressão arterial", "peso": "Peso", "glicemia": "Glicemia"}
CONTEXTS = {"jejum": "Jejum", "antes_refeicao": "Antes da refeição",
            "apos_refeicao": "Após a refeição", "outro": "Outro"}
FIELDS = {"pressao": ("systolic", "diastolic", "pulse"), "peso": ("weight",),
          "glicemia": ("glucose", "context")}

class ValidationError(ValueError):
    pass

@dataclass(frozen=True)
class Measurement:
    measured_at: datetime
    kind: str
    systolic: int | None = None
    diastolic: int | None = None
    pulse: int | None = None
    weight: Decimal | None = None
    glucose: int | None = None
    context: str | None = None
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if (not isinstance(self.measured_at, datetime) or self.measured_at.tzinfo is not None
                or self.measured_at.second or self.measured_at.microsecond):
            raise ValidationError("Use data e horário locais com precisão de minuto.")
        if self.kind not in TYPES:
            raise ValidationError("Tipo de medição desconhecido.")
        try:
            if str(UUID(self.id)) != self.id:
                raise ValueError()
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValidationError("Identificador UUID inválido.") from exc
        for name in ("systolic", "diastolic", "pulse", "weight", "glucose", "context"):
            if name not in FIELDS[self.kind] and getattr(self, name) is not None:
                raise ValidationError("Campo incompatível com o tipo da medição.")
        for name, label, maximum in (("systolic", "Sistólica", 400), ("diastolic", "Diastólica", 300),
                                     ("pulse", "Pulso", 350), ("glucose", "Glicemia", 2000)):
            if name in FIELDS[self.kind]:
                value = getattr(self, name)
                if type(value) is not int or not 1 <= value <= maximum:
                    raise ValidationError(f"{label}: use um inteiro de 1 a {maximum}.")
        if self.kind == "peso":
            if (not isinstance(self.weight, Decimal) or not self.weight.is_finite()
                    or not 0 < self.weight <= 700 or self.weight.as_tuple().exponent < -3):
                raise ValidationError("Peso: maior que zero, até 700 kg, com até 3 casas decimais.")
        if self.kind == "glicemia" and self.context not in CONTEXTS:
            raise ValidationError("Escolha o contexto da glicemia.")
        if not isinstance(self.note, str) or len(self.note) > 5000 or "\x00" in self.note:
            raise ValidationError("Observação: até 5000 caracteres, sem caractere nulo.")

    @classmethod
    def from_fields(cls, day, clock, kind, *, record_id=None, note="", **fields):
        try:
            moment = datetime.strptime(f"{day.strip()} {clock.strip()}", "%d/%m/%Y %H:%M")
            values = {}
            for name, value in fields.items():
                if name in ("systolic", "diastolic", "pulse", "glucose"):
                    values[name] = int(str(value).strip())
                elif name == "weight":
                    values[name] = Decimal(str(value).strip().replace(",", "."))
                else:
                    values[name] = value
            return cls(moment, kind, note=note, **values, **({"id": record_id} if record_id else {}))
        except (ValueError, InvalidOperation) as exc:
            if isinstance(exc, ValidationError):
                raise
            raise ValidationError("Confira data, horário e valores numéricos da medição.") from exc

    def summary(self):
        if self.kind == "pressao":
            return f"{self.systolic}/{self.diastolic} mmHg · {self.pulse} bpm"
        if self.kind == "peso":
            return f"{str(self.weight).replace('.', ',')} kg"
        return f"{self.glucose} mg/dL · {CONTEXTS[self.context]}"

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.utils import platform

from .database import Repository, RepositoryError
from .export import csv_text, save_csv
from .models import Measurement, ValidationError, TYPES, FIELDS, CONTEXTS
from .ui.import_flow import ImportFlow
from .periods import period_bounds
from .picker_logic import format_day
from .ui.chart import HistoryChart
from .ui.widgets import BodyLabel, Field, ChoiceSpinner, button, column, dialog, date_picker, time_picker

ROOT = Path(__file__).resolve().parent.parent


class VitalRegistroApp(ImportFlow, App):
    title = "VitalRegistro"
    icon = str(ROOT / "assets" / "icons" / "icone.png")

    def __init__(self, data_dir=None, **kwargs):
        super().__init__(**kwargs)
        self.data_dir_override = data_dir
        self.edit_id = None
        self.original_fields = None
        self.exporter = None
        self.android_insets = None
        self.scrolls = {}

    def build(self):
        Builder.load_file(str(ROOT / "vitalregistro" / "ui" / "theme.kv"))
        Window.clearcolor = (.95, .97, 1, 1)
        # Android IME overlap is handled by the safe viewport, without panning
        # the whole interface a second time. Desktop keeps Kivy's behavior.
        Window.softinput_mode = "" if platform == "android" else "below_target"
        if platform != "android":
            Window.size = (420, 800)
        self.storage_dir = Path(self.data_dir_override or self.user_data_dir)
        try:
            self.repo = Repository(self.storage_dir / "vitalregistro-v2.sqlite3")
        except RepositoryError as exc:
            layout = BoxLayout(orientation="vertical", padding=dp(20))
            layout.add_widget(BodyLabel(text=str(exc)))
            layout.add_widget(button("Fechar", self.stop))
            return layout
        self.manager = ScreenManager(transition=NoTransition())
        self.build_home()
        self.build_type_choice()
        self.build_form()
        self.build_history()
        self.build_charts()
        self.manager.current = "home"
        Window.bind(on_keyboard=self.on_keyboard, on_touch_down=self.dismiss_chart_tooltip)
        self.viewport = BoxLayout()
        self.viewport.add_widget(self.manager)
        if platform == "android":
            from .ui.android_insets import AndroidInsets
            self.viewport.padding = [0, dp(24), 0, dp(48)]
            self.android_insets = AndroidInsets(self.apply_insets)
        return self.viewport

    def on_start(self):
        if (self.storage_dir / "vitalregistro.sqlite3").exists():
            self.message("Banco da v0.1.0 preservado. A v0.2.0 usa um histórico separado; "
                         "não importa o banco ou CSV antigo. Não limpe os dados nem desinstale "
                         "se precisar conservar o histórico anterior.")
        if self.android_insets:
            self.android_insets.start()

    def apply_insets(self, padding):
        if list(self.viewport.padding) != list(padding):
            self.viewport.padding = padding
            Clock.schedule_once(self.reveal_focused_field, .05)

    def reveal_focused_field(self, *_):
        if self.manager.current == "form":
            for field in self.fields.values():
                if getattr(field, "focus", False):
                    self.scrolls["form"].scroll_to(field, padding=dp(24), animate=False)
                    break

    def focus_field(self, field, focused):
        if focused:
            Clock.schedule_once(self.reveal_focused_field, .3)

    def page(self, name, title):
        screen = Screen(name=name)
        outer = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        if name != "home":
            back = button("<", self.go_back)
            back.size_hint_x = None
            back.width = dp(48)
            header.add_widget(back)
        label = BodyLabel(text=title, bold=True, font_size="22sp")
        header.add_widget(label)
        outer.add_widget(header)
        scroll = ScrollView(do_scroll_x=False)
        self.scrolls[name] = scroll
        content = column()
        content.padding = [0, 0, 0, dp(24)]
        scroll.add_widget(content)
        outer.add_widget(scroll)
        screen.add_widget(outer)
        self.manager.add_widget(screen)
        return content, label

    def build_home(self):
        content, _ = self.page("home", "VitalRegistro")
        content.add_widget(BodyLabel(text="Sua saúde registrada, sempre com você"))
        content.add_widget(Image(source=self.icon, size_hint_y=None, height=dp(180)))
        for title, callback, primary in (
            ("+  Novo Registro", self.new_record, True),
            ("Meus Registros", self.show_history, False),
            ("Gráficos", self.show_charts, False),
            ("Exportar Dados", self.export_records, False),
            ("Importar CSV", self.import_records, False),
        ):
            content.add_widget(button(title, callback, primary))
        content.add_widget(BodyLabel(text="Seus registros ficam neste dispositivo.\nSem conta e sem conexão."))

    def build_type_choice(self):
        content, _ = self.page("type", "Novo registro")
        content.add_widget(BodyLabel(text="Qual medição deseja registrar?"))
        for kind, label in TYPES.items():
            content.add_widget(button(label, lambda kind=kind: self.start_record(kind), True))

    def build_form(self):
        content, self.form_title = self.page("form", "Novo Registro")
        self.day_button = button("", self.pick_day)
        self.time_button = button("", self.pick_time)
        for label, control in (("Data da medição", self.day_button), ("Horário da medição", self.time_button)):
            content.add_widget(BodyLabel(text=label))
            content.add_widget(control)
        content.add_widget(BodyLabel(text="Você pode registrar medições de outros dias.", font_size="14sp"))
        self.form_fields = column()
        content.add_widget(self.form_fields)
        self.fields = {}
        content.add_widget(button("Salvar Registro", self.save_record, True))
        content.add_widget(button("Cancelar", self.go_back))

    def configure_fields(self, kind):
        self.record_kind = kind
        self.form_fields.clear_widgets()
        self.fields = {}
        labels = {"systolic": "Sistólica · mmHg", "diastolic": "Diastólica · mmHg", "pulse": "Pulso · bpm",
                  "weight": "Peso · kg", "glucose": "Glicemia · mg/dL", "context": "Contexto da medição",
                  "note": "Observação (opcional)"}
        for key in (*FIELDS[kind], "note"):
            self.form_fields.add_widget(BodyLabel(text=labels[key]))
            if key == "context":
                field = ChoiceSpinner(text="Escolha o contexto", values=tuple(CONTEXTS.values()),
                                      size_hint_y=None, height=dp(52))
            else:
                field = Field()
                field.bind(focus=self.focus_field)
                if key == "note":
                    field.multiline = True
                    field.height = dp(110)
                else:
                    field.input_type = "number"
                    if key != "weight":
                        field.input_filter = "int"
            self.fields[key] = field
            self.form_fields.add_widget(field)

    def form_snapshot(self):
        return (self.day_button.text, self.time_button.text, *(field.text for field in self.fields.values()))

    def new_record(self):
        self.manager.current = "type"

    def start_record(self, kind):
        self.edit_id = None
        self.configure_fields(kind)
        self.form_title.text = TYPES[kind]
        moment = datetime.now()
        self.day_button.text, self.time_button.text = format_day(moment), moment.strftime("%H:%M")
        for key, field in self.fields.items():
            if key != "context":
                field.text = ""
        self.original_fields = self.form_snapshot()
        self.manager.current = "form"
        self.scrolls["form"].scroll_y = 1

    def pick_day(self):
        current = datetime.strptime(self.day_button.text, "%d/%m/%Y").date()
        date_picker(current, lambda value: setattr(self.day_button, "text", format_day(value)))

    def pick_time(self):
        current = datetime.strptime(self.time_button.text, "%H:%M")
        time_picker(current, lambda value: setattr(self.time_button, "text", value))

    def save_record(self):
        try:
            fields = {key: field.text for key, field in self.fields.items()}
            if "context" in fields:
                fields["context"] = next((key for key, label in CONTEXTS.items() if label == fields["context"]), None)
            record = Measurement.from_fields(self.day_button.text, self.time_button.text,
                                             self.record_kind, record_id=self.edit_id, **fields)
            if self.edit_id is None:
                self.repo.create(record)
            else:
                self.repo.update(record)
        except (ValidationError, RepositoryError) as exc:
            self.message(str(exc))
            return
        self.original_fields = self.form_snapshot()
        self.history_filter.text = "Todos"
        self.show_history()
        self.message("Registro salvo.")

    def build_history(self):
        content, _ = self.page("history", "Meus Registros")
        content.add_widget(button("+  Novo Registro", self.new_record, True))
        self.history_filter = ChoiceSpinner(text="Todos", values=("Todos", *TYPES.values()),
                                            size_hint_y=None, height=dp(48))
        content.add_widget(self.history_filter)
        self.history_filter.bind(text=lambda *_: self.show_history())
        self.history_list = column()
        content.add_widget(self.history_list)
        self.history_limit = 50

    def show_history(self):
        self.history_limit = 50
        if self.refresh_history():
            self.manager.current = "history"

    def refresh_history(self):
        try:
            kind = next((key for key, label in TYPES.items() if label == self.history_filter.text), None)
            rows = self.repo.list(kind=kind)
        except RepositoryError as exc:
            self.message(str(exc))
            return False
        self.history_list.clear_widgets()
        if not rows:
            self.history_list.add_widget(BodyLabel(text="Nenhum registro ainda. Comece em Novo Registro."))
        for record in rows[:self.history_limit]:
            text = (f"{record.measured_at:%d/%m/%Y · %H:%M}\n"
                    f"{TYPES[record.kind]} · {record.summary()}")
            item = button(text, lambda record_id=record.id: self.details(record_id))
            item.height = dp(88)
            self.history_list.add_widget(item)
        if len(rows) > self.history_limit:
            self.history_list.add_widget(button("Mostrar mais", self.load_more))
        return True

    def load_more(self):
        self.history_limit += 50
        self.refresh_history()

    def details(self, record_id):
        try:
            record = self.repo.get(record_id)
        except RepositoryError as exc:
            self.message(str(exc))
            return
        content = BoxLayout(orientation="vertical", spacing=dp(10))
        scroll = ScrollView()
        info = BodyLabel(text=(f"{TYPES[record.kind]}\n{record.measured_at:%d/%m/%Y às %H:%M}\n\n"
                               f"{record.summary()}\n\nObservação:\n{record.note or 'Sem observação.'}"))
        scroll.add_widget(info)
        content.add_widget(scroll)
        popup = dialog("Detalhes do registro", content, min(580, Window.height / dp(1) * .9))

        def edit():
            popup.dismiss()
            self.edit_record(record)

        def delete():
            popup.dismiss()
            self.confirm("Excluir este registro definitivamente?", lambda: self.delete_record(record.id))
        content.add_widget(button("Editar", edit, True))
        content.add_widget(button("Excluir", delete))
        content.add_widget(button("Fechar", popup.dismiss))

    def edit_record(self, record):
        self.edit_id = record.id
        self.configure_fields(record.kind)
        self.form_title.text = "Editar " + TYPES[record.kind]
        self.day_button.text = format_day(record.measured_at)
        self.time_button.text = record.measured_at.strftime("%H:%M")
        for key, field in self.fields.items():
            field.text = CONTEXTS[record.context] if key == "context" else str(getattr(record, key))
        self.original_fields = self.form_snapshot()
        self.manager.current = "form"
        self.scrolls["form"].scroll_y = 1

    def delete_record(self, record_id):
        try:
            self.repo.delete(record_id)
        except RepositoryError as exc:
            self.message(str(exc))
            return
        self.show_history()

    def build_charts(self):
        content, _ = self.page("charts", "Gráficos")
        self.metric = ChoiceSpinner(text="Pressão", values=("Pressão", "Pulso", "Peso", "Glicemia"), size_hint_y=None, height=dp(48))
        self.period = ChoiceSpinner(text="Últimos 7 dias", values=("Últimos 7 dias", "Últimos 30 dias", "Todos os registros"),
                              size_hint_y=None, height=dp(48))
        content.add_widget(self.metric)
        content.add_widget(self.period)
        self.legend = BodyLabel(text="")
        content.add_widget(self.legend)
        self.chart = HistoryChart(size_hint_y=None, height=dp(300))
        content.add_widget(self.chart)
        content.add_widget(BodyLabel(text="Toque em um ponto para ver data, horário e valor."))
        self.chart_count = BodyLabel(text="")
        content.add_widget(self.chart_count)
        self.metric.bind(text=self.refresh_chart)
        self.period.bind(text=self.refresh_chart)

    def show_charts(self):
        self.refresh_chart()
        self.manager.current = "charts"

    def refresh_chart(self, *_):
        days = {"Últimos 7 dias": 7, "Últimos 30 dias": 30, "Todos os registros": None}[self.period.text]
        try:
            kind = {"Pressão": "pressao", "Pulso": "pressao", "Peso": "peso", "Glicemia": "glicemia"}[self.metric.text]
            records = self.repo.list(*period_bounds(days), newest_first=False, kind=kind)
        except RepositoryError as exc:
            self.message(str(exc))
            return
        if self.metric.text == "Pressão":
            series = [("systolic", (1, .22, .3, 1)), ("diastolic", (.08, .42, .8, 1))]
            self.legend.text = "Sistólica: vermelho · Diastólica: azul\nmmHg"
        elif self.metric.text == "Pulso":
            series = [("pulse", (.0, .55, .5, 1))]
            self.legend.text = "Pulso · bpm"
        elif self.metric.text == "Peso":
            series = [("weight", (.08, .42, .8, 1))]
            self.legend.text = "Peso · kg"
        else:
            series = [("glucose", (.4, .25, .65, 1))]
            self.legend.text = "Glicemia · mg/dL"
        self.chart.set_data(records, series)
        self.chart_count.text = ("1 registro. Cada ponto representa uma medição." if len(records) == 1
                                else f"{len(records)} registro(s). As linhas apenas conectam medições.")

    def export_records(self):
        try:
            records = self.repo.list(newest_first=False)
            if not records:
                self.message("Adicione um registro antes de exportar.")
                return
            text = csv_text(records)
            filename = f"vitalregistro-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:6]}.csv"
            if platform == "android":
                from .android_export import AndroidExporter
                if self.exporter is None:
                    self.exporter = AndroidExporter()
                self.exporter.save(text, filename, self.message)
            else:
                folder = self.storage_dir / "exports"
                folder.mkdir(parents=True, exist_ok=True)
                destination = folder / filename
                save_csv(destination, text)
                self.message(f"CSV exportado para:\n{destination}")
        except (RepositoryError, OSError, RuntimeError) as exc:
            self.message(str(exc) if isinstance(exc, RepositoryError) else "Não foi possível exportar. Tente novamente.")

    def message(self, text):
        content = BoxLayout(orientation="vertical", spacing=dp(12))
        scroll = ScrollView()
        scroll.add_widget(BodyLabel(text=text))
        content.add_widget(scroll)
        popup = dialog("VitalRegistro", content, 300)
        content.add_widget(button("OK", popup.dismiss, True))
        return popup

    def confirm(self, text, callback):
        content = BoxLayout(orientation="vertical", spacing=dp(12))
        content.add_widget(BodyLabel(text=text))
        popup = dialog("Confirmar", content, 280)

        def accept():
            popup.dismiss()
            callback()
        content.add_widget(button("Confirmar", accept, True))
        content.add_widget(button("Cancelar", popup.dismiss))

    def go_back(self):
        def leave():
            self.manager.current = "home"
        if self.manager.current == "form" and self.form_snapshot() != self.original_fields:
            self.confirm("Descartar as alterações que ainda não foram salvas?", leave)
        else:
            leave()

    def dismiss_chart_tooltip(self, *_):
        self.chart.hide_tooltip()

    def on_keyboard(self, window, key, *_):
        if key == 27 and self.manager.current != "home":
            self.go_back()
            return True
        return False

    def on_pause(self):
        if self.android_insets:
            self.android_insets.stop()
        return True

    def on_resume(self):
        if self.android_insets:
            self.android_insets.start()

    def on_stop(self):
        if self.android_insets:
            self.android_insets.stop()
        Window.unbind(on_keyboard=self.on_keyboard, on_touch_down=self.dismiss_chart_tooltip)

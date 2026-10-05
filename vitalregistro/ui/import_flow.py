"""File selection, read-only preview and explicit import confirmation."""
from pathlib import Path
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import platform
from .widgets import BodyLabel, button, dialog
from ..import_csv import preview_csv, read_csv_file
from ..models import ValidationError
from ..database import RepositoryError

class ImportFlow:
    def import_records(self):
        if getattr(self, "import_busy", False):
            self.message("Uma importação já está em andamento.")
            return
        self.import_busy = True
        if platform == "android":
            from ..android_import import AndroidImporter
            if not getattr(self, "importer", None):
                self.importer = AndroidImporter()
            try:
                self.importer.open(self.preview_import)
            except RuntimeError as exc:
                self.import_busy = False
                self.message(str(exc))
        else:
            content = BoxLayout(orientation="vertical", spacing=dp(8))
            chooser = FileChooserListView(path=str(self.storage_dir), filters=["*.csv", "*.CSV"])
            content.add_widget(chooser)
            popup = dialog("Selecionar CSV v0.2.0", content, min(620, Window.height / dp(1)*.9))
            popup.bind(on_dismiss=lambda *_: setattr(self, "import_busy", False))
            def choose():
                if not chooser.selection:
                    return
                try:
                    payload = read_csv_file(Path(chooser.selection[0]))
                except (OSError, ValidationError) as exc:
                    self.message(str(exc) if isinstance(exc, ValidationError) else "Não foi possível ler o arquivo.")
                    return
                popup.dismiss()
                self.preview_import(payload, None)
            content.add_widget(button("Ler e conferir", choose, True))
            content.add_widget(button("Cancelar", popup.dismiss))

    def preview_import(self, payload, error=None):
        self.import_busy = False
        if error:
            self.message(error)
            return
        try:
            preview = preview_csv(payload, self.repo.list())
        except (ValidationError, RepositoryError) as exc:
            self.message(str(exc))
            return
        self.import_busy = True
        content = BoxLayout(orientation="vertical", spacing=dp(8))
        scroll = ScrollView()
        scroll.add_widget(BodyLabel(text=preview.summary()))
        content.add_widget(scroll)
        popup = dialog("Conferir importação", content, min(540, Window.height / dp(1)*.9))
        popup.bind(on_dismiss=lambda *_: setattr(self, "import_busy", False))
        def accept():
            popup.dismiss()
            try:
                inserted, duplicates = self.repo.import_records(preview.records)
            except RepositoryError as exc:
                self.message(str(exc))
                return
            self.history_filter.text = "Todos"
            self.show_history()
            self.message(f"{inserted} registros importados. "
                         f"{duplicates + preview.duplicates} duplicatas ignoradas.")
        if preview.can_import:
            content.add_widget(button("Confirmar importação", accept, True))
        content.add_widget(button("Cancelar" if preview.can_import else "Fechar", popup.dismiss))
        return preview

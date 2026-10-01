"""Desktop integration smoke. Uses only fictional records in a temporary folder."""

import os
import sys
import tempfile
from pathlib import Path

os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_ARGS"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from vitalregistro.app import VitalRegistroApp
from vitalregistro.ui.widgets import date_picker, time_picker
from datetime import date, datetime
from dataclasses import replace


def close_popups():
    for widget in list(Window.children):
        if isinstance(widget, Popup):
            widget.dismiss()


with tempfile.TemporaryDirectory() as directory:
    app = VitalRegistroApp(data_dir=directory)
    failures = []

    def exercise(_):
        try:
            app.new_record()
            app.day_button.text = "15/04/2025"
            app.time_button.text = "08:30"
            for name, value in {"systolic": "120", "diastolic": "80", "pulse": "72", "weight": "70,5",
                                "note": "DADO FICTÍCIO: ação, aspas e\nsegunda linha"}.items():
                app.fields[name].text = value
            app.save_record()
            close_popups()
            rows = app.repo.list()
            assert len(rows) == 1 and app.manager.current == "history"
            app.details(rows[0].id)
            close_popups()
            app.edit_record(rows[0])
            app.day_button.text = "16/04/2025"
            app.fields["weight"].text = "71.25"
            app.save_record()
            close_popups()
            assert app.repo.get(rows[0].id).measured_at.day == 16
            app.show_charts()
            app.period.text = "Todos os registros"
            assert len(app.chart.records) == 1
            assert "Cada ponto" in app.chart_count.text
            for metric in ("Pressão", "Pulso", "Peso"):
                app.metric.text = metric
                app.chart.redraw()
            recent_id = app.repo.create(replace(app.repo.get(rows[0].id), id=None,
                                                measured_at=datetime.now().replace(second=0, microsecond=0)))
            for metric in ("Pressão", "Pulso", "Peso"):
                app.metric.text = metric
                for period in app.period.values:
                    app.period.text = period
                    app.refresh_chart()
                    app.chart.redraw()
                    assert len(app.chart.records) == (2 if period == "Todos os registros" else 1)
                    options = [option.text for option in app.period._dropdown.container.children]
                    assert period not in options and len(options) == 2
            date_picker(date(2024, 2, 29), lambda _: None)
            close_popups()
            time_picker(datetime.now(), lambda _: None)
            close_popups()
            app.export_records()
            close_popups()
            app.export_records()
            close_popups()
            assert len(list(Path(directory).glob("exports/*.csv"))) == 2
            app.delete_record(rows[0].id)
            app.delete_record(recent_id)
            assert app.repo.list() == []
            app.show_charts()
            assert app.chart.records == []
            app.manager.current = "home"
            if "--screenshot" in sys.argv:
                folder = Path("runtime")
                folder.mkdir(exist_ok=True)
                Clock.schedule_once(lambda _: app.root.export_to_png(str(folder / "home.png")), .5)
            print("UI SMOKE: PASS", flush=True)
        except Exception as exc:
            failures.append(exc)
            import traceback
            traceback.print_exc()
        finally:
            Clock.schedule_once(lambda _: app.stop(), 1)

    Clock.schedule_once(exercise, 1)
    app.run()
    if failures:
        raise SystemExit(1)

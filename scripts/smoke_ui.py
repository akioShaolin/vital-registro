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
from kivy.input.motionevent import MotionEvent
from kivy.base import EventLoop


class SmokeTouch(MotionEvent):
    def __init__(self, x, y):
        super().__init__("smoke", 1, (x/(Window.width-1), y/(Window.height-1)),
                         is_touch=True, type_id="touch")
        self.profile = ["pos"]

    def depack(self, args):
        self.sx, self.sy = args
        super().depack(args)

    def touch_down(self):
        EventLoop.post_dispatch_input("begin", self)

    def touch_up(self):
        EventLoop.post_dispatch_input("end", self)

    def touch_move(self, x, y):
        self.move((x/(Window.width-1), y/(Window.height-1)))
        EventLoop.post_dispatch_input("update", self)


def close_popups():
    for widget in list(Window.children):
        if isinstance(widget, Popup):
            widget.dismiss()


with tempfile.TemporaryDirectory() as directory:
    app = VitalRegistroApp(data_dir=directory)
    failures = []

    def exercise(_):
        try:
            from vitalregistro.models import FIELDS, TYPES
            from vitalregistro.import_csv import preview_csv
            from vitalregistro.ui.wheels import DateWheelPicker, TimeWheelPicker
            app.new_record()
            assert app.manager.current == "type"
            data = {"pressao": {"systolic": "120", "diastolic": "80", "pulse": "72"},
                    "peso": {"weight": "70,5"},
                    "glicemia": {"glucose": "96", "context": "Jejum"}}
            for kind, fields in data.items():
                app.start_record(kind)
                assert set(app.fields) == set(FIELDS[kind]) | {"note"}
                app.day_button.text = "15/04/2025"
                app.time_button.text = "08:30"
                for name, value in fields.items():
                    app.fields[name].text = value
                app.fields["note"].text = 'FICTÍCIO: ação, "aspas"\nsegunda linha'
                app.save_record()
                close_popups()
                record = app.repo.list(kind=kind)[0]
                app.details(record.id)
                close_popups()
                app.edit_record(record)
                app.day_button.text = "16/04/2025"
                app.fields["note"].text += " editado"
                app.save_record()
                close_popups()
                assert app.repo.get(record.id).measured_at.day == 16
                app.history_filter.text = TYPES[kind]
                assert len(app.history_list.children) == 1
            app.history_filter.text = "Todos"
            assert len(app.repo.list()) == 3
            app.show_charts()
            app.period.text = "Todos os registros"
            for metric in app.metric.values:
                app.metric.text = metric
                app.refresh_chart()
                assert len(app.chart.records) == 1
                assert "Cada ponto" in app.chart_count.text
                point = app.chart.points[0]
                app.chart.select_at(point.x, point.y)
                assert app.chart.selected_point == point and app.chart.tooltip
                app.chart.select_at(-100, -100)
                assert app.chart.tooltip is None
            from uuid import uuid4
            for record in app.repo.list():
                app.repo.create(replace(record, id=str(uuid4()),
                                        measured_at=datetime.now().replace(second=0, microsecond=0)))
            for metric in app.metric.values:
                app.metric.text = metric
                for period in app.period.values:
                    app.period.text = period
                    app.refresh_chart()
                    assert len(app.chart.records) == (2 if period == "Todos os registros" else 1)
            app.export_records()
            close_popups()
            app.export_records()
            close_popups()
            exports = list(Path(directory).glob("exports/*.csv"))
            assert len(exports) == 2
            payload = exports[0].read_bytes()
            preview = app.preview_import(payload)
            assert preview.duplicates == 6 and not preview.can_import
            close_popups()
            for record in app.repo.list():
                app.delete_record(record.id)
            assert app.repo.list() == []
            preview = app.preview_import(payload)
            assert preview.can_import and len(preview.records) == 6
            popup = next(w for w in Window.children if isinstance(w, Popup))
            confirm = next(w for w in popup.content.children if getattr(w, "text", "") == "Confirmar importação")
            confirm.dispatch("on_release")
            close_popups()
            assert len(app.repo.list()) == 6
            app.import_records()  # Desktop file chooser opens without reading personal data.
            close_popups()
            assert not app.import_busy
            # Leave a real wheel dialog mounted for layout and scrolling checks.
            popup = date_picker(date(2024, 2, 29), lambda _: None)
            state["wheel"] = next(w for w in popup.content.children if isinstance(w, DateWheelPicker))
            Clock.schedule_once(check_wheel, .7)
        except Exception as exc:
            fail(exc)

    state = {}

    def fail(exc):
        failures.append(exc)
        import traceback
        traceback.print_exc()
        app.stop()

    def check_wheel(_):
        try:
            wheel = state["wheel"]
            assert wheel.value() == date(2024, 2, 29), wheel.value()
            wheel.year.select(wheel.year.values.index(2025))
            assert wheel.day.value == 28
            wheel.month.select(3)  # April
            wheel.day.select(29)
            assert wheel.value() == date(2025, 4, 30), wheel.value()
            def scroll_month(_):
                wheel.month.effect_y.value = 0  # Same path as gesture-driven scrolling.
                Clock.schedule_once(check_scrolled, .6)
            Clock.schedule_once(scroll_month, .3)
        except Exception as exc:
            fail(exc)

    def check_scrolled(_):
        try:
            wheel=state["wheel"]
            assert wheel.month.value == 12, wheel.month.value
            assert 0 < len(wheel.year.layout.children) < 20  # Recycled, not 9999 widgets.
            if "--screenshot" in sys.argv:
                folder=Path("runtime"); folder.mkdir(exist_ok=True)
                Window.screenshot(name=str(folder/"v2-wheels.png"))
            close_popups()
            time_picker(datetime(2026,10,5,23,59), lambda _: None)
            Clock.schedule_once(check_time, .5)
        except Exception as exc:
            fail(exc)

    def check_time(_):
        try:
            from vitalregistro.ui.wheels import TimeWheelPicker
            popup = next(w for w in Window.children if isinstance(w, Popup))
            wheel = next(w for w in popup.content.children if isinstance(w, TimeWheelPicker))
            assert wheel.value() == "23:59", wheel.value()
            wheel.hour.select(0); wheel.minute.select(0)
            assert wheel.value() == "00:00"
            state["time_wheel"] = wheel
            Clock.schedule_once(drag_time_wheel, .3)
        except Exception as exc:
            fail(exc)

    def drag_time_wheel(_):
        try:
            wheel=state["time_wheel"].minute
            x,y=wheel.to_window(wheel.center_x,wheel.center_y)
            touch=SmokeTouch(x,y)
            touch.touch_down()
            Clock.schedule_once(lambda _:touch.touch_move(x,y+60),.08)
            Clock.schedule_once(lambda _:touch.touch_up(),.16)
            Clock.schedule_once(check_time_drag,1.5)
        except Exception as exc:
            fail(exc)

    def check_time_drag(_):
        try:
            wheel=state["time_wheel"].minute
            wheel.commit()
            assert wheel.value > 0, wheel.value
            assert not wheel._dragging
            close_popups()
            app.metric.text = "Pressão"
            app.period.text = "Todos os registros"
            app.show_charts()
            Clock.schedule_once(touch_chart,.5)
        except Exception as exc:
            fail(exc)

    def touch_chart(_):
        try:
            point=app.chart.points[0]
            x,y=app.chart.to_window(point.x,point.y)
            touch=SmokeTouch(x,y)
            touch.touch_down(); touch.touch_up()
            state["point"]=point
            Clock.schedule_once(check_touch_chart,.4)
        except Exception as exc:
            fail(exc)

    def check_touch_chart(_):
        try:
            assert app.chart.selected_point == state["point"], app.chart.selected_point
            if "--screenshot" in sys.argv:
                Window.screenshot(name=str(Path("runtime")/"v2-chart.png"))
            print("UI SMOKE: PASS (three types, CRUD, charts/touch, CSV round-trip, wheels)",flush=True)
            Clock.schedule_once(lambda _:app.stop(),.5)
        except Exception as exc:
            fail(exc)

    Clock.schedule_once(exercise, 1)
    app.run()
    if failures:
        raise SystemExit(1)

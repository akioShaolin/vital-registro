import calendar
from datetime import date

from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.metrics import dp


class VitalButton(Button):
    primary = BooleanProperty(False)


class BodyLabel(Label):
    pass


class Field(TextInput):
    pass


def button(text, callback, primary=False):
    item = VitalButton(text=text, primary=primary)
    item.bind(on_release=lambda *_: callback())
    return item


def column():
    layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
    layout.bind(minimum_height=layout.setter("height"))
    return layout


def dialog(title, content, height=340):
    popup = Popup(title=title, content=content, size_hint=(.94, None), height=dp(height),
                  background="", background_color=(.94, .97, 1, 1),
                  title_color=(.06, .15, .29, 1), separator_color=(.1, .4, .7, 1))
    popup.open()
    return popup


def date_picker(value, callback):
    selected = [value.year, value.month]
    content = BoxLayout(orientation="vertical", spacing=dp(8))
    controls = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
    month = Spinner(text=str(value.month), values=tuple(str(m) for m in range(1, 13)))
    year = Field(text=str(value.year), input_filter="int", input_type="number", size_hint_x=.9)
    controls.add_widget(month)
    controls.add_widget(year)
    content.add_widget(BodyLabel(text="Mês e ano · toque no dia"))
    content.add_widget(controls)
    grid = GridLayout(cols=7, spacing=dp(3))
    content.add_widget(grid)
    popup = dialog("Data da medição", content, 440)

    def choose(day):
        callback(date(selected[0], selected[1], day))
        popup.dismiss()

    def render(*_):
        grid.clear_widgets()
        try:
            y, m = int(year.text), int(month.text)
            if not 1 <= y <= 9999:
                return
        except ValueError:
            return
        selected[:] = [y, m]
        for title in ("S", "T", "Q", "Q", "S", "S", "D"):
            grid.add_widget(BodyLabel(text=title, halign="center"))
        for week in calendar.monthcalendar(y, m):
            for day in week:
                if day:
                    item = button(str(day), lambda day=day: choose(day), day == value.day)
                    item.size_hint_y = 1
                    grid.add_widget(item)
                else:
                    grid.add_widget(Label())
    month.bind(text=render)
    year.bind(text=render)
    content.add_widget(button("Cancelar", popup.dismiss))
    render()


def time_picker(value, callback):
    content = BoxLayout(orientation="vertical", spacing=dp(12))
    content.add_widget(BodyLabel(text="Hora e minuto"))
    row = BoxLayout(spacing=dp(12))
    hour = Spinner(text=value.strftime("%H"), values=tuple(f"{i:02}" for i in range(24)))
    minute = Spinner(text=value.strftime("%M"), values=tuple(f"{i:02}" for i in range(60)))
    row.add_widget(hour)
    row.add_widget(minute)
    content.add_widget(row)
    popup = dialog("Horário da medição", content, 290)

    def confirm():
        callback(f"{hour.text}:{minute.text}")
        popup.dismiss()
    content.add_widget(button("Confirmar", confirm, True))
    content.add_widget(button("Cancelar", popup.dismiss))

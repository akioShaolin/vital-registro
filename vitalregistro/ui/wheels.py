"""Touch scroll wheels, virtualized even for years 1..9999. No keyboard."""
import calendar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from .widgets import BodyLabel
from ..picker_logic import valid_date, wheel_index, wheel_position

class WheelRow(Button):
    wheel = ObjectProperty(None, allownone=True)
    index = NumericProperty(0)

    def on_release(self):
        self.wheel.select(self.index)

class WheelPicker(RecycleView):
    selected = NumericProperty(0)

    def __init__(self, values, selected, **kwargs):
        super().__init__(do_scroll_x=False, bar_width=0, **kwargs)
        self.values = list(values)
        self._changing = False
        self._dragging = False
        self.layout = RecycleBoxLayout(default_size=(None, dp(48)), default_size_hint=(1, None),
                                      size_hint_y=None, orientation="vertical")
        self.layout.bind(minimum_height=self.layout.setter("height"))
        self.add_widget(self.layout)
        self.viewclass = WheelRow
        self._settle = Clock.create_trigger(self.snap, .18)
        self.bind(scroll_y=self.scrolled, height=self.resize)
        self.set_values(values, selected)
        Clock.schedule_once(self.resize, 0)

    def set_values(self, values, selected):
        self.values = list(values)
        self.selected = self.values.index(selected) if selected in self.values else 0
        self.data = [dict(text=f"{v:02}", wheel=self, index=i, font_size="20sp",
                          background_normal="", background_down="",
                          background_color=(.78, .87, .96, 1) if i == self.selected else (.94, .97, 1, 1),
                          color=(.06, .15, .29, 1)) for i, v in enumerate(self.values)]
        self.select(self.selected)
        Clock.schedule_once(lambda _: self.select(self.selected), 0)

    @property
    def value(self):
        return self.values[int(self.selected)]

    def resize(self, *_):
        pad = max(0, (self.height - dp(48)) / 2)
        self.layout.padding = [0, pad, 0, pad]
        Clock.schedule_once(lambda _: self.select(self.selected), 0)

    def select(self, index):
        self._changing = True
        old = int(self.selected)
        self.selected = max(0, min(len(self.values)-1, int(index)))
        for i in {old, int(self.selected)}:
            if i < len(self.data):
                self.data[i]["background_color"] = ((.78, .87, .96, 1) if i == self.selected
                                                     else (.94, .97, 1, 1))
        if old != self.selected:
            self.refresh_from_data()
        self.scroll_y = wheel_position(self.selected, len(self.values))
        if self.effect_y:
            self.effect_y.velocity = 0
            self.effect_y.value = min(0, self.height - self.layout.height) * self.scroll_y
        self._changing = False

    def scrolled(self, *_):
        if not self._changing:
            self._settle.cancel()
            self._settle()

    def on_scroll_start(self, touch, check_children=True):
        result = super().on_scroll_start(touch, check_children)
        if result and not getattr(touch, "is_mouse_scrolling", False):
            self._dragging = True
        return result

    def on_scroll_stop(self, touch, check_children=True):
        result = super().on_scroll_stop(touch, check_children)
        self._dragging = False
        self._settle()
        return result

    def snap(self, *_):
        if self._dragging:
            self._settle()
            return
        if self.effect_y:
            self.effect_y.velocity = 0
        self.select(wheel_index(self.scroll_y, len(self.values)))

    def commit(self):
        self._dragging = False
        self.snap()
        return self.value

def add_wheel(parent, title, values, value):
    box = BoxLayout(orientation="vertical")
    box.add_widget(BodyLabel(text=title, halign="center"))
    wheel = WheelPicker(values, value)
    box.add_widget(wheel)
    parent.add_widget(box)
    return wheel


class DateWheelPicker(BoxLayout):
    def __init__(self, value, **kwargs):
        super().__init__(spacing=dp(6), **kwargs)
        self.day = add_wheel(self, "Dia", range(1, calendar.monthrange(value.year, value.month)[1]+1), value.day)
        self.month = add_wheel(self, "Mês", range(1, 13), value.month)
        self.year = add_wheel(self, "Ano", range(1, 10000), value.year)
        self.month.bind(selected=self.adjust_days)
        self.year.bind(selected=self.adjust_days)

    def adjust_days(self, *_):
        value = valid_date(self.year.value, self.month.value, self.day.value)
        self.day.set_values(range(1, calendar.monthrange(value.year, value.month)[1]+1), value.day)

    def value(self):
        self.year.commit()
        self.month.commit()
        return valid_date(self.year.value, self.month.value, self.day.commit())

class TimeWheelPicker(BoxLayout):
    def __init__(self, value, **kwargs):
        super().__init__(spacing=dp(12), **kwargs)
        self.hour = add_wheel(self, "Hora", range(24), value.hour)
        self.minute = add_wheel(self, "Minuto", range(60), value.minute)

    def value(self):
        return f"{self.hour.commit():02}:{self.minute.commit():02}"

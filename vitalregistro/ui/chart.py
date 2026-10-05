"""Time-scaled charts rendered with Kivy, without matplotlib/native dependencies."""

from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from ..chart_logic import ChartPoint, project_x, hit_points, point_text


class HistoryChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.selected_point = None
        self.tooltip = None
        self.records = []
        self._touch_down = None
        self.series = []
        self.bind(pos=self.redraw, size=self.redraw)

    def set_data(self, records, series):
        self.records, self.series = records, series
        self.redraw()

    def label(self, text, x, y, anchor="left"):
        label = CoreLabel(text=text, font_size=dp(11), color=(.12, .2, .3, 1))
        label.refresh()
        texture = label.texture
        if anchor == "right":
            x -= texture.width
        Color(1, 1, 1, 1)
        Rectangle(texture=texture, pos=(x, y), size=texture.size)

    def redraw(self, *_):
        self.hide_tooltip()
        self.points = []
        self.canvas.clear()
        with self.canvas:
            if not self.records:
                self.label("Sem registros neste período.", self.x + dp(12), self.center_y)
                return
            values = [float(getattr(r, field)) for field, _ in self.series for r in self.records]
            low, high = min(values), max(values)
            margin = max((high - low) * .15, 1)
            low, high = max(0, low - margin), high + margin
            ticks = [f"{low + (high - low) * i / 4:.1f}" for i in range(5)]
            # Measure axis labels instead of assuming a fixed 44dp gutter.
            label_width = 0
            for text in ticks:
                label = CoreLabel(text=text, font_size=dp(11))
                label.refresh()
                label_width = max(label_width, label.texture.width)
            left, bottom = self.x + label_width + dp(12), self.y + dp(40)
            width, height = max(1, self.right - left - dp(16)), max(1, self.height - dp(65))
            first, last = self.records[0].measured_at, self.records[-1].measured_at
            seconds = (last - first).total_seconds()
            for i in range(5):
                y = bottom + height * i / 4
                Color(.82, .87, .92, 1)
                Line(points=[left, y, left + width, y], width=1)
                self.label(ticks[i], left - dp(8), y - dp(5), "right")
            self.label(first.strftime("%d/%m/%y"), left, self.y + dp(12))
            if seconds:
                self.label(last.strftime("%d/%m/%y"), left + width, self.y + dp(12), "right")
            for field, color in self.series:
                points = []
                for record in self.records:
                    x = project_x(record.measured_at, first, last, left, width)
                    y = bottom + height * (float(getattr(record, field)) - low) / (high - low)
                    points.extend((x, y))
                    self.points.append(ChartPoint(x, y, record, field))
                Color(*color)
                if len(points) > 2:
                    Line(points=points, width=dp(1.5))
                for x, y in zip(points[::2], points[1::2]):
                    Ellipse(pos=(x - dp(3), y - dp(3)), size=(dp(6), dp(6)))

    def hide_tooltip(self, *_):
        if self.tooltip:
            self.remove_widget(self.tooltip)
            self.tooltip = None
        self.selected_point = None

    def show_point(self, point):
        self.hide_tooltip()
        self.selected_point = point
        self.tooltip = Label(text=point_text(point), font_size="14sp", color=(.06, .15, .29, 1),
                             size_hint=(None, None), size=(min(self.width, dp(280)), dp(92)))
        self.tooltip.text_size = (self.tooltip.width - dp(12), None)
        self.tooltip.pos = (max(self.x, min(point.x, self.right-self.tooltip.width)),
                            max(self.y, min(point.y + dp(12), self.top-self.tooltip.height)))
        with self.tooltip.canvas.before:
            Color(.87, .93, .98, 1)
            Rectangle(pos=self.tooltip.pos, size=self.tooltip.size)
        self.add_widget(self.tooltip)

    def select_at(self, x, y):
        self.hide_tooltip()
        hits = hit_points(self.points, x, y, dp(24))
        if len(hits) == 1:
            self.show_point(hits[0])
        elif hits:
            from .widgets import column, button, dialog
            from kivy.uix.scrollview import ScrollView
            content = column()
            scroll = ScrollView()
            scroll.add_widget(content)
            popup = dialog("Pontos sobrepostos: escolha", scroll, min(420, Window.height / dp(1)*.85))
            for point in hits:
                def choose(point=point):
                    popup.dismiss()
                    self.show_point(point)
                item = button(point_text(point) + "\nID: " + point.record.id, choose)
                item.height = dp(144)
                content.add_widget(item)
            content.add_widget(button("Cancelar", popup.dismiss))
        return hits

    def on_touch_down(self, touch):
        self.hide_tooltip()
        if self.collide_point(*touch.pos) and not getattr(touch, "is_mouse_scrolling", False):
            self._touch_down = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_down and self.collide_point(*touch.pos):
            x, y = self._touch_down
            self._touch_down = None
            if (touch.x-x)**2 + (touch.y-y)**2 <= dp(12)**2:
                self.select_at(*touch.pos)
                return True
        self._touch_down = None
        return super().on_touch_up(touch)
